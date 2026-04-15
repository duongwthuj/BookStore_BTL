---
origin: theonekit-core
repository: The1Studio/theonekit-core
module: null
protected: true
---

# Quality Gates — Contributor Rules

This file documents the CI-enforced quality gates for all T1K kit repositories.
**Audience: kit maintainers and contributors.** This file is excluded from release ZIPs — end users never receive it.

---

## 1. Metadata Deletions Rule

When you permanently remove a `.claude/` file or directory from a kit, you MUST register the deletion so the CLI can clean up older installs automatically.

### Where to register

| Kit type | Register in | Format |
|---|---|---|
| **Flat kit** (core, web, cli, release-action, nakama, telemetry-worker) | `.claude/metadata.json` → `deletions[]` | Path relative to `.claude/` |
| **Modular kit** (unity, rn, cocos, designer) | `.claude/modules/<name>/.t1k-manifest.json` → `deletions[]` | Path relative to `.claude/` |

Both styles can coexist within the same kit — flat-kit deletions live in `metadata.json`, module-scoped deletions live in the module's manifest.

### Supported entry formats

```json
"deletions": [
  "rules/old-rule.md",          // exact path (relative to .claude/)
  "skills/deprecated-skill/**", // glob: all files under the directory
  "agents/old-agent.md"
]
```

### CI enforcement

`check-t1k-manifest-deletions.cjs` (in `theonekit-release-action/scripts/`) runs on every PR and push to main. It:

1. Reads `metadata.json → deletions[]` (flat kit schema)
2. Reads every `modules/*/.t1k-manifest.json → deletions[]` (modular kit schema)
3. Expands glob patterns recursively
4. Fails (exit 1) if any deletion entry still exists in the working tree

**Fix:** Remove the actual file, or remove the deletion entry if the file was intentionally re-added.

### Example

```json
// .claude/metadata.json
{
  "name": "theonekit-core",
  "version": "1.54.0",
  "deletions": [
    "rules/old-contributor-guide.md",
    "skills/deprecated-skill/**"
  ]
}
```

---

## 2. Skill Registry Contract

### Name format

Every skill's `SKILL.md` MUST have a `name:` field in YAML frontmatter:

```yaml
---
name: t1k:<skill-name>
# or for kit-scoped skills:
name: t1k:<kit>:<skill-name>
# examples:
name: t1k:cook
name: t1k:unity:scene
---
```

Rules:
- Value MUST start with `t1k:`
- Name segments use lowercase letters, digits, and hyphens only: `[a-z0-9][a-z0-9-]*`
- One or two segments after `t1k:` (e.g., `cook` or `unity:scene`)
- Must be unique across the entire kit (enforced by `/t1k:doctor`)

### Cross-reference form

When referencing a skill from any `.md` file (rules, agents, skill docs), use the exact slash-command form matching the registered name:

```
See /t1k:cook for the full workflow.        (core skill — name: t1k:cook)
```

For kit-scoped skills, the two-segment form is used: `/t1k:<kit>:<skill>` (e.g., the Unity kit registers skills with names like `t1k:unity:scene`). The cross-ref registry validates that the name after `/t1k:` matches a registered key.

The reference key is everything after `/t1k:` — must match the registered name after stripping `t1k:` prefix from the `name:` field.

### Avoiding Claude Code built-in collisions

Do not register skill names that collide with Claude Code's built-in slash commands (e.g., `/help`, `/clear`, `/compact`). Check the current Claude Code CLI documentation before registering a new skill name.

---

## 3. Skill Cross-Reference Integrity

### What is checked

`check-skill-cross-refs.cjs` (in `theonekit-release-action/scripts/`) scans these file types for `/t1k:<name>` patterns:

| Scanned path | What is found |
|---|---|
| `.claude/rules/**/*.md` | Rule cross-references |
| `.claude/skills/*/SKILL.md` | Skill self-references and gotchas |
| `.claude/skills/*/references/*.md` | Gotcha / reference entries |
| `.claude/modules/*/skills/*/SKILL.md` | Module skill references |
| `.claude/modules/*/skills/*/references/*.md` | Module gotchas |
| `.claude/agents/*.md` | Agent skill activations |

### Pass / fail conditions

| Condition | Exit code | Annotation level |
|---|---|---|
| All `/t1k:<name>` refs are registered | 0 | — |
| Any `/t1k:<name>` ref is NOT registered | 1 | `::error` |
| Any `/ck:<name>` ref (legacy CK pattern) | 0 | `::warning` |

Legacy `/ck:` references are warnings only — they indicate port-in-progress and will be cleaned up in a later phase. They do NOT block CI.

### Warn-only rollback mode

If the gate produces false positives after a release, set `T1K_GATE_WARN_ONLY=1` in the reusable workflow env. All errors become warnings. Pin back to a known-good release-action tag while the issue is investigated.

### How to fix broken refs

1. Run locally: `node /path/to/theonekit-release-action/scripts/check-skill-cross-refs.cjs .`
2. The output shows an annotation like: `::error file=.claude/rules/foo.md,line=12::Broken skill ref: /t1k:<name> (not registered in any SKILL.md)`
3. Either:
   - Register the skill: create `.claude/skills/<name>/SKILL.md` with `name: t1k:<name>` in frontmatter
   - Fix the reference: update the `/t1k:<name>` in the file to point to a registered skill
   - Remove the reference if the skill was intentionally deleted

---

## 4. No-Override Rule

### Requirement

All `.claude/` file paths MUST be globally unique across every kit and module. No file from any kit or module may silently overwrite a file from another.

### Why

When users install T1K globally, all kits write into the same `~/.claude/` directory. If two kits ship a file with the same name, the second install overwrites the first — silently dropping functionality.

### How it works

At release time, `validate-no-collisions.cjs` checks all `.claude/` filenames within the kit being released against a registry of all known-deployed file names. CI fails if any collision is detected.

Agent filenames are auto-prefixed before release:
- Core agents: no prefix (e.g., `planner.md`)
- Kit-wide agents: `{kit-short}-` prefix (e.g., `unity-planner.md`)
- Module agents: `{kit-short}-{module}-` prefix (e.g., `unity-dots-core-implementer.md`)

Already-prefixed filenames are skipped. Source repos keep clean names; prefixing is applied by CI before packaging.

### For contributors

- Do NOT manually prefix agent filenames in source — CI handles it
- If you add a new agent or skill, use a descriptive name unlikely to collide
- If CI reports a collision, rename your file and update all references

---

## 5. Origin Metadata Injection

All `.claude/` files receive origin tracking metadata injected by CI/CD. This metadata is committed back to git, making it visible in the repo.

### Format by file type

| File type | Location | Example |
|---|---|---|
| `.md` (Markdown) | YAML frontmatter block | `origin: theonekit-core` |
| `.json` | Top-level `"_origin"` key | `"_origin": {"kit": "theonekit-core", ...}` |
| `.cjs` / `.js` | Comment header (line 1 or 2) | `// t1k-origin: kit=theonekit-core \| repo=...` |
| `.sh` / `.yml` | Comment header | `# t1k-origin: kit=theonekit-core \| repo=...` |

### Fields

| Field | Purpose | Scope |
|---|---|---|
| `origin` / `kit` | Which kit repo owns this file | All `.claude/` files |
| `repository` | GitHub owner/repo (used by `/t1k:sync-back` and `/t1k:issue`) | All `.claude/` files |
| `module` | Module name, or `null` for kit-wide / core files | All `.claude/` files |
| `protected` | `true` = core-protected; cannot be overridden by kit or module layers | All `.claude/` files |
| `version` | Semver from `module.json` (modular) or `metadata.json` (flat) | **SKILL.md only** |

### Rules

- **DO NOT** hand-edit these fields. They are CI/CD-managed and will be overwritten on the next release.
- The `version` field in SKILL.md is CI-managed: sourced from `module.json` (modular kits) or `metadata.json` (flat kits). Do not set it manually — CI injects the correct version at release time.
- Files missing origin metadata will have it injected on the next CI run after any push.
- The `settings.json` file is intentionally exempt — it is user-configurable and excluded from origin injection.
- **DO NOT** remove origin metadata from a file to "unprotect" it — `protected=true` is enforced by CI validation.

### Sync-back

When you modify a `.claude/` file locally (e.g., a skill gotcha), use `/t1k:sync-back` to propagate the change back to the source kit repo. The skill reads the `origin` metadata to determine which repo to target and creates a PR automatically.

---

## 6. Settings Schema Validation

`validate-settings-schema.cjs` (in `theonekit-release-action/scripts/`) validates `.claude/settings.json` on every PR and push to main.

### What is checked

- Every entry in `hooks` arrays is an object with a `type` string and `command` string
- Hook entries use the **grouped format** expected by Claude Code (not the legacy flat format)
- No malformed entries that would silently be ignored by Claude Code at runtime

### Pass / fail conditions

| Condition | Exit code |
|---|---|
| All hook entries have valid `type` and `command` fields | 0 |
| Any hook entry is missing `type` or `command` | 1 |
| `settings.json` is not valid JSON | 1 |

### How to fix failures

1. Run locally: `node /path/to/theonekit-release-action/scripts/validate-settings-schema.cjs .`
2. The output identifies which hook entries are malformed
3. Ensure every hook entry follows this format:
   ```json
   {
     "hooks": {
       "SessionStart": [
         { "type": "command", "command": "node .claude/hooks/hook-runner.cjs SessionStart" }
       ]
     }
   }
   ```
4. Remove any entries that are plain strings — they must be objects

---

## 7. Activation Coverage Validation

`validate-activation-coverage.cjs` (in `theonekit-release-action/scripts/`) checks that every skill directory in `skills/` has at least one keyword mapping in the activation fragments.

### What is checked

- Scans `skills/*/SKILL.md` and `modules/*/skills/*/SKILL.md` for skill directories
- For each skill directory, looks for keyword mappings in `t1k-activation-*.json` fragments and `module.json` `activation` fields
- Warns if a skill has no keyword coverage (it will never auto-activate)

### Pass / fail conditions

| Condition | Exit code | Annotation level |
|---|---|---|
| All skills have at least one keyword mapping | 0 | — |
| Any skill has no keyword mapping | 0 | `::warning` |

This gate is **warning-only** — it does not block CI. It highlights skills that are effectively unreachable via auto-activation.

### How to fix warnings

1. Run locally: `node /path/to/theonekit-release-action/scripts/validate-activation-coverage.cjs .`
2. For each warned skill, add keyword mappings to the appropriate `t1k-activation-*.json` or `module.json` → `activation.mappings`
3. If the skill is intentionally invocation-only (e.g., always called explicitly), suppress the warning by adding a comment to its `SKILL.md` frontmatter: `activation: explicit-only`

---

## 8. Routing Coverage Validation

`validate-routing-coverage.cjs` (in `theonekit-release-action/scripts/`) checks that every agent in `agents/` has at least one role registration in the routing fragments.

### What is checked

- Scans `agents/*.md` for agent files
- For each agent, looks for role registrations in `t1k-routing-*.json` fragments and `module.json` `routingOverlay` fields
- Warns if an agent has no role registration (it can never be dispatched by the registry)

### Pass / fail conditions

| Condition | Exit code | Annotation level |
|---|---|---|
| All agents have at least one role registration | 0 | — |
| Any agent has no role registration | 0 | `::warning` |

This gate is **warning-only** — it does not block CI. It highlights agents that are unreachable through the standard registry routing system.

### How to fix warnings

1. Run locally: `node /path/to/theonekit-release-action/scripts/validate-routing-coverage.cjs .`
2. For each warned agent, add a role mapping to `t1k-routing-*.json`:
   ```json
   {
     "roles": {
       "implementer": "your-agent-name"
     }
   }
   ```
3. Or register it in `module.json` → `routingOverlay.roles` if it is module-scoped

---

## 9. Cross-Platform Hook Validation

`validate-cross-platform.cjs` (in `theonekit-release-action/scripts/`) scans all hook `.cjs` files for platform-specific patterns that would break on Windows or macOS.

### What is checked

Scans `.claude/hooks/**/*.cjs` for banned patterns:

| Banned Pattern | Reason | Cross-Platform Alternative |
|---|---|---|
| `/dev/stdin` | Linux/macOS only | `fs.readFileSync(0, 'utf8')` (fd 0) |
| `2>/dev/null` | Shell redirect — bash only | `stdio: ['pipe', 'pipe', 'ignore']` in execSync |
| `execSync('...', { shell: true })` | Shell-dependent | Use `execFileSync` without shell |
| Hardcoded `/tmp/` | Linux/macOS only | `os.tmpdir()` |
| String path concatenation with `/` | Breaks on Windows | `path.join()` |

### Pass / fail conditions

| Condition | Exit code | Annotation level |
|---|---|---|
| No banned patterns found | 0 | — |
| Any banned pattern found | 1 | `::error` |

### How to fix failures

1. Run locally: `node /path/to/theonekit-release-action/scripts/validate-cross-platform.cjs .`
2. The output shows the file, line number, and the banned pattern
3. Replace each banned pattern with the cross-platform alternative shown above
4. Test on Windows if possible, or verify the alternative is used elsewhere in the codebase
