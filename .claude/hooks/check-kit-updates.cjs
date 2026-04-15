#!/usr/bin/env node
// t1k-origin: kit=theonekit-core | repo=The1Studio/theonekit-core | module=null | protected=true
/**
 * check-kit-updates.cjs — Auto-update installed kits/modules at session start.
 *
 * Discovers ALL repos to check from:
 *   1. installedModules (v3) — grouped by repository
 *   2. t1k-config-*.json — each config fragment declares a repo
 * Then for each repo: fetch release manifest or tag, compare, auto-update patch/minor.
 *
 * Self-update guard: skips repos matching CWD's git remote.
 * Cache: 1h TTL (.update-check-cache). Opt-out: features.autoUpdate: false.
 */

const fs = require('fs');
const path = require('path');
const { execSync, execFileSync } = require('child_process');
const { extractZip } = require('./module-manifest-helpers.cjs');
const { T1K } = require('./telemetry-utils.cjs');

function isMajorBump(local, remote) {
  return Number(remote.split('.')[0]) > Number((local || '0').split('.')[0]);
}

// Flag readers are centralized in telemetry-utils.cjs — see readFeatureFlag.

/**
 * Fix relative .claude/ paths in global ~/.claude/settings.json.
 * Transforms "node .claude/..." → "node \"$HOME/.claude/...\"" (or %USERPROFILE% on Windows).
 * Idempotent, fail-open. Only touches global settings — never project-level.
 */
function fixGlobalSettingsPaths(home) {
  const settingsPath = path.join(home, '.claude', 'settings.json');
  if (!fs.existsSync(settingsPath)) return;

  let raw;
  try { raw = fs.readFileSync(settingsPath, 'utf8'); } catch { return; }

  // Quick check: if no bare ".claude/" paths exist (without $HOME prefix), nothing to fix
  if (!/(node\s+)(?:\.\/)?(\.claude\/)/.test(raw)) return;
  // Skip if already transformed (has $HOME or %USERPROFILE% in paths)
  if (/\$HOME\/\.claude\//.test(raw) || /%USERPROFILE%/.test(raw)) return;

  let settings;
  try { settings = JSON.parse(raw); } catch { return; }

  const prefix = process.platform === 'win32' ? '$USERPROFILE' : '$HOME';
  let fixCount = 0;

  function fixCommand(cmd) {
    if (!cmd || !cmd.includes('.claude/')) return cmd;
    // Already has a path variable — skip
    if (/\$HOME|%USERPROFILE%|\$CLAUDE_PROJECT_DIR|%CLAUDE_PROJECT_DIR%/.test(cmd)) return cmd;
    // Transform: node .claude/... or node ./.claude/... → node "$HOME/.claude/..."
    const fixed = cmd.replace(
      /(node\s+)(?:\.\/)?(\.claude\/\S+)/,
      `$1"${prefix}/$2"`
    );
    if (fixed !== cmd) fixCount++;
    return fixed;
  }

  // Walk all hook entries
  if (settings.hooks) {
    for (const entries of Object.values(settings.hooks)) {
      if (!Array.isArray(entries)) continue;
      for (const entry of entries) {
        if (entry.command) entry.command = fixCommand(entry.command);
        if (Array.isArray(entry.hooks)) {
          for (const hook of entry.hooks) {
            if (hook.command) hook.command = fixCommand(hook.command);
          }
        }
      }
    }
  }

  // Fix statusLine
  if (settings.statusLine?.command) {
    settings.statusLine.command = fixCommand(settings.statusLine.command);
  }

  if (fixCount === 0) return;

  try {
    fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
    console.log(`[t1k:settings-repair] Fixed ${fixCount} relative path(s) in global settings.json`);
  } catch { /* fail-open */ }
}

(async () => {
  try {
    const CACHE_TTL_MS = 60 * 60 * 1000;
    const cwd = process.cwd();
    const { resolveClaudeDir, isT1KMetadata, readFeatureFlag } = require('./telemetry-utils.cjs');
    const { logHook, createHookTimer, logHookCrash } = require('./hook-logger.cjs');
    const resolved = resolveClaudeDir();
    if (!resolved) process.exit(0);
    const { claudeDir, isGlobalOnly, home } = resolved;
    const timer = createHookTimer('check-kit-updates');

    // Always fix global settings paths (fast, idempotent, no network)
    fixGlobalSettingsPaths(home);

    // Check opt-out flag (shared helper — see readFeatureFlag in telemetry-utils.cjs)
    if (readFeatureFlag(claudeDir, T1K.FEATURES.AUTO_UPDATE, true) === false) process.exit(0);

    // Dry-run: skip all gh network calls and extraction — exposes branching for CI tests
    const noop = process.env[T1K.ENV.KIT_UPDATE_NOOP] === '1';

    // Cache check
    const cacheFile = path.join(claudeDir, '.update-check-cache');
    if (fs.existsSync(cacheFile)) {
      if (Date.now() - new Date(fs.readFileSync(cacheFile, 'utf8').trim()).getTime() < CACHE_TTL_MS) process.exit(0);
    }

    const metadataPath = path.join(claudeDir, T1K.METADATA_FILE);
    if (!fs.existsSync(metadataPath)) process.exit(0);
    let metadata;
    try { metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8')); } catch { process.exit(0); }
    // Don't update CK or other framework metadata that happens to live next door.
    if (!isT1KMetadata(metadata)) process.exit(0);

    // Self-update guard: skip repos matching CWD's git remote
    let cwdRemotes = '';
    try { cwdRemotes = execSync('git remote -v', { encoding: 'utf8', timeout: 5000, stdio: ['pipe', 'pipe', 'ignore'] }); } catch { /* ok */ }

    // ── Discover all repos to check ──────────────────────────────────────────
    // Map<repo, { modules: [{name, version}], isModular: bool, localKitVersion: string }>
    const repoMap = new Map();

    // Source 1: installedModules (v3) — per-module tracking
    for (const [name, entry] of Object.entries(metadata.installedModules || {})) {
      if (!entry.repository || cwdRemotes.includes(entry.repository)) continue;
      if (!repoMap.has(entry.repository)) repoMap.set(entry.repository, { modules: [], isModular: true });
      repoMap.get(entry.repository).modules.push({ name, version: (entry.version || '0.0.0').replace(/^v/, '') });
    }

    // Source 2: t1k-config-*.json — each config declares its repo (catches core + any kit not in installedModules)
    for (const cf of fs.readdirSync(claudeDir).filter(f => f.startsWith(T1K.CONFIG_PREFIX) && f.endsWith('.json'))) {
      try {
        const config = JSON.parse(fs.readFileSync(path.join(claudeDir, cf), 'utf8'));
        const repo = config.repos?.primary;
        if (!repo || cwdRemotes.includes(repo) || repoMap.has(repo)) continue;
        // Kit-level entry (not per-module) — use metadata.version as local version
        const localVersion = (metadata.version || '0.0.0').replace(/^v/, '');
        repoMap.set(repo, { modules: [], isModular: false, localKitVersion: localVersion });
      } catch { /* skip */ }
    }

    if (repoMap.size === 0) { fs.writeFileSync(cacheFile, new Date().toISOString()); process.exit(0); }

    // ── Check each repo for updates ──────────────────────────────────────────
    const extractionRoot = isGlobalOnly ? home : cwd;
    const allowMajor = readFeatureFlag(claudeDir, T1K.FEATURES.AUTO_UPDATE_MAJOR, true) !== false;

    if (noop) {
      // Dry-run: log discovered repos and decision plan, skip network
      for (const [repo, info] of repoMap) {
        const kind = info.isModular ? `modular (${info.modules.length} modules)` : `flat (v${info.localKitVersion})`;
        console.log(`[t1k:noop] would check ${repo} — ${kind} — allowMajor=${allowMajor}`);
      }
      fs.writeFileSync(cacheFile, new Date().toISOString());
      timer.end({ outcome: 'noop', repos: repoMap.size, allowMajor });
      process.exit(0);
    }

    for (const [repo, info] of repoMap) {
      try {
        if (info.isModular && info.modules.length > 0) {
          checkModularRepo(repo, info.modules, metadata, metadataPath, claudeDir, extractionRoot, allowMajor);
        } else {
          checkKitRepo(repo, info.localKitVersion, metadata, metadataPath, claudeDir, extractionRoot, allowMajor);
        }
      } catch { /* skip repo, retry next session */ }
    }

    // ── Auto-commit updated .claude/ files (skip in global-only mode) ──────
    if (!isGlobalOnly) {
      autoCommitUpdates(cwd);
    }

    fs.writeFileSync(cacheFile, new Date().toISOString());
    logHook('check-kit-updates', { repos: repoMap.size });
    timer.end({ outcome: 'ok', repos: repoMap.size });
    process.exit(0);
  } catch (err) {
    try { require('./hook-logger.cjs').logHookCrash('check-kit-updates', err); } catch { /* ok */ }
    process.exit(0); // fail-open
  }
})();

// ── Auto-commit helper ──────────────────────────────────────────────────────

/**
 * Auto-commit .claude/ changes after kit/module updates.
 * Only stages .claude/ files — never touches user's working changes.
 * Skips if no .claude/ changes detected or if git state is unsafe (rebase, merge).
 */
function autoCommitUpdates(cwd) {
  try {
    const gitStatus = execSync('git status --porcelain', { encoding: 'utf8', cwd, timeout: 5000, stdio: ['pipe', 'pipe', 'ignore'] });
    if (!gitStatus.trim()) return; // nothing changed

    const gitDir = path.join(cwd, '.git');
    if (fs.existsSync(path.join(gitDir, 'MERGE_HEAD')) || fs.existsSync(path.join(gitDir, 'rebase-merge')) || fs.existsSync(path.join(gitDir, 'rebase-apply'))) return;

    // Collect only .claude/ changes (new, modified, deleted)
    const claudeChanges = gitStatus.split('\n')
      .map(l => l.trim())
      .filter(l => l.length > 0)
      .filter(l => {
        // Extract file path — status is first 2 chars, then space, then path
        const filePath = l.substring(3).trim().replace(/^"(.*)"$/, '$1');
        return filePath.startsWith('.claude/');
      })
      .map(l => l.substring(3).trim().replace(/^"(.*)"$/, '$1'));

    if (claudeChanges.length === 0) return; // no .claude/ changes

    // Stage only .claude/ files
    execSync('git add .claude/', { cwd, timeout: 5000 });

    // Build commit message with updated module/kit names
    // Parse [t1k:updated] lines from earlier output isn't possible here,
    // so detect what changed from git diff --cached
    let diffSummary = '';
    try {
      diffSummary = execSync('git diff --cached --name-only', { encoding: 'utf8', cwd, timeout: 5000, stdio: ['pipe', 'pipe', 'ignore'] }).trim();
    } catch { /* ok */ }

    if (!diffSummary) return; // nothing staged after add

    const changedFiles = diffSummary.split('\n').filter(Boolean);
    const updatedNames = new Set();
    for (const f of changedFiles) {
      // Detect module from path: .claude/modules/{name}/
      const moduleMatch = f.match(/\.claude\/modules\/([^/]+)\//);
      if (moduleMatch) { updatedNames.add(moduleMatch[1]); continue; }
      // Detect skill from path: .claude/skills/{name}/
      const skillMatch = f.match(/\.claude\/skills\/([^/]+)\//);
      if (skillMatch) { updatedNames.add(skillMatch[1]); continue; }
      // Detect agent from path: .claude/agents/{name}.md
      const agentMatch = f.match(/\.claude\/agents\/([^/]+)\.md$/);
      if (agentMatch) { updatedNames.add(agentMatch[1]); continue; }
      // Detect rule from path: .claude/rules/{name}.md
      const ruleMatch = f.match(/\.claude\/rules\/([^/]+)\.md$/);
      if (ruleMatch) { updatedNames.add(ruleMatch[1]); continue; }
      // Registry/config files
      if (f.match(/\.claude\/t1k-/)) { updatedNames.add('registry'); continue; }
      if (f === '.claude/metadata.json') updatedNames.add('metadata');
    }

    // Build a descriptive scope: list up to 5 names, then "and N more"
    const names = [...updatedNames];
    let scope;
    if (names.length === 0) scope = 'kit';
    else if (names.length <= 5) scope = names.join(', ');
    else scope = `${names.slice(0, 5).join(', ')} +${names.length - 5} more`;

    const msg = `chore(deps): auto-update ${scope}\n\nAuto-committed by check-kit-updates hook.\nFiles: ${changedFiles.length} changed in .claude/`;

    // --no-verify is intentional here: this auto-commit runs INSIDE a hook, so triggering
    // pre-commit hooks would cause infinite recursion. The commit only stages .claude/ files.
    execFileSync('git', ['commit', '-m', msg, '--no-verify'], { cwd, timeout: 10000, stdio: ['pipe', 'pipe', 'ignore'], windowsHide: true });
    console.log(`[t1k:auto-commit] Committed ${changedFiles.length} .claude/ file(s) from kit/module update`);
  } catch {
    // fail-open: if commit fails, updates are still extracted — user can commit manually
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function readMetadata(metadataPath) {
  try { return JSON.parse(fs.readFileSync(metadataPath, 'utf8')); } catch { return null; }
}

function writeMetadata(metadataPath, data) {
  try { fs.writeFileSync(metadataPath, JSON.stringify(data, null, 2) + '\n'); } catch { /* ok */ }
}

/**
 * Check a modular repo: fetch manifest.json, compare per-module versions, download ZIPs.
 * Majors are gated by features.autoUpdateMajor (default true). When false, majors
 * emit a [t1k:major-update] notice and require manual action.
 */
function checkModularRepo(repo, modules, metadata, metadataPath, claudeDir, cwd, allowMajor) {
  let manifest;
  try {
    const raw = execFileSync('gh', ['release', 'download', '--repo', repo, '--pattern', 'manifest.json', '--output', '-'], { encoding: 'utf8', timeout: 10000, stdio: ['pipe', 'pipe', 'ignore'], windowsHide: true });
    const parsed = JSON.parse(raw);
    manifest = parsed.modules || parsed;
  } catch {
    // Fallback: use release tag for all modules
    try {
      const tag = JSON.parse(execFileSync('gh', ['release', 'view', '--repo', repo, '--json', 'tagName'], { encoding: 'utf8', timeout: 10000, stdio: ['pipe', 'pipe', 'ignore'], windowsHide: true })).tagName.replace(/^v/, '');
      manifest = Object.fromEntries(modules.map(m => [m.name, { version: tag }]));
    } catch { return; }
  }

  for (const { name, version: local } of modules) {
    const remote = (manifest[name]?.version || '').replace(/^v/, '');
    if (!remote || remote === local) continue;

    const isMajor = isMajorBump(local, remote);
    if (isMajor && !allowMajor) {
      console.log(`${T1K.TAGS.KIT_MAJOR} ${name} ${local} → ${remote} (major). features.${T1K.FEATURES.AUTO_UPDATE_MAJOR} is false — run: gh release download --repo ${repo} --pattern "${name}-*.zip"`);
      continue;
    }

    try {
      // Save old manifest file list before overwriting
      const oldManifestPath = path.join(claudeDir, 'modules', name, '.t1k-manifest.json');
      let oldFiles = [];
      try { oldFiles = JSON.parse(fs.readFileSync(oldManifestPath, 'utf8')).files || []; } catch { /* no old manifest */ }

      const tmpZip = path.join(claudeDir, `.${name}-update.zip`);
      execFileSync('gh', ['release', 'download', '--repo', repo, '--pattern', `${name}-*.zip`, '--output', tmpZip, '--clobber'], { timeout: 30000, stdio: ['pipe', 'pipe', 'ignore'], windowsHide: true });
      extractZip(tmpZip, cwd);
      try { fs.unlinkSync(tmpZip); } catch { /* ok */ }

      // Clean up orphaned files (removed between versions)
      let newFiles = [];
      try { newFiles = JSON.parse(fs.readFileSync(oldManifestPath, 'utf8')).files || []; } catch { /* ok */ }
      const newSet = new Set(newFiles);
      for (const f of oldFiles) {
        if (!newSet.has(f)) {
          const fullPath = path.join(claudeDir, f);
          try { fs.rmSync(fullPath, { recursive: true, force: true }); } catch { /* ok */ }
        }
      }

      const m = readMetadata(metadataPath);
      if (m?.installedModules?.[name]) { m.installedModules[name].version = remote; writeMetadata(metadataPath, m); }
      const majorTag = isMajor ? ' (major)' : '';
      console.log(`${T1K.TAGS.KIT_UPDATED} ${name} ${local} → ${remote}${majorTag}`);
    } catch { /* retry next session */ }
  }
}

/**
 * Check a kit-level repo (non-modular, e.g., core): fetch release tag, compare, download ZIP.
 * Majors are gated by features.autoUpdateMajor (default true). When false, majors
 * emit a [t1k:major-update] notice and require manual action.
 */
function checkKitRepo(repo, localVersion, metadata, metadataPath, claudeDir, cwd, allowMajor) {
  if (!localVersion || localVersion === '0.0.0-source' || localVersion === '0.0.0') return;

  const rel = JSON.parse(execFileSync('gh', ['release', 'view', '--repo', repo, '--json', 'tagName,assets'], { encoding: 'utf8', timeout: 10000, stdio: ['pipe', 'pipe', 'ignore'], windowsHide: true }));
  const remote = rel.tagName.replace(/^v/, '');
  if (remote === localVersion) return;

  const kitName = repo.split('/').pop();
  const isMajor = isMajorBump(localVersion, remote);

  if (isMajor && !allowMajor) {
    console.log(`${T1K.TAGS.KIT_MAJOR} ${kitName} ${localVersion} → ${remote} (major). features.${T1K.FEATURES.AUTO_UPDATE_MAJOR} is false — run: gh release download --repo ${repo} --pattern "*.zip"`);
    return;
  }

  if (rel.assets?.find(a => a.name.endsWith('.zip'))) {
    const tmpZip = path.join(claudeDir, `.${kitName}-update.zip`);
    execFileSync('gh', ['release', 'download', '--repo', repo, '--pattern', '*.zip', '--output', tmpZip, '--clobber'], { timeout: 30000, stdio: ['pipe', 'pipe', 'ignore'], windowsHide: true });
    extractZip(tmpZip, cwd);
    try { fs.unlinkSync(tmpZip); } catch { /* ok */ }
    const m = readMetadata(metadataPath);
    if (m) { m.version = remote; writeMetadata(metadataPath, m); }
    const majorTag = isMajor ? ' (major)' : '';
    console.log(`${T1K.TAGS.KIT_UPDATED} ${kitName} ${localVersion} → ${remote}${majorTag}`);
  }
}
