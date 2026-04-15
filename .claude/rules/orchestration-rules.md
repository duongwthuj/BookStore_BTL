---

origin: theonekit-core
repository: The1Studio/theonekit-core
module: null
protected: true
---
# TheOneKit Orchestration Rules

**TheOneKit (T1K)** provides registry-based command routing. All commands read JSON registry fragments to determine which agent to delegate to.

## Decision Tree

```
User Request → Classify:

 1. FEATURE / IMPLEMENT       → /t1k:cook
 2. PLANNING / ARCHITECTURE   → /t1k:plan
 3. BUG / ERROR / COMPILE     → /t1k:fix
 4. RUN TESTS                 → /t1k:test
 5. INVESTIGATE / DEBUG       → /t1k:debug
 6. CODE REVIEW               → /t1k:review
 7. DOCUMENTATION             → /t1k:docs
 8. GIT OPERATIONS            → /t1k:git (cm|cp|pr|merge)
 9. SKILL / AGENT MANAGEMENT  → /t1k:issue, /t1k:sync-back
10. TRIAGE ISSUES / PRs       → /t1k:triage
11. BRAINSTORM / IDEATION     → /t1k:brainstorm
12. TECHNICAL QUESTION        → /t1k:ask
13. EXPLORE CODEBASE          → /t1k:scout
14. SESSION REVIEW            → /t1k:watzup
15. REGISTRY VALIDATION       → /t1k:doctor
16. USAGE GUIDE               → /t1k:help
17. MODULE MANAGEMENT         → /t1k:modules (add|remove|list|preset|validate|split|merge|audit|create)
18. PARALLEL MULTI-AGENT      → /t1k:team (research|review|cook|debug|triage)
19. CONTEXT OPTIMIZATION       → /t1k:context
20. STUCK / BLOCKED            → /t1k:problem-solve (auto-triggers after 3+ failures)
21. STRUCTURED REASONING       → /t1k:think
```

## Registry-Based Agent Routing

Follow protocol: `rules/routing-protocol.md`

**Standard Roles:**
| Role | Used by command |
|------|----------------|
| `implementer` | t1k:cook, t1k:fix |
| `tester` | t1k:test |
| `reviewer` | t1k:review, t1k:triage |
| `debugger` | t1k:debug, t1k:fix |
| `optimizer` | t1k:profile (kit-level) |
| `brainstormer` | t1k:brainstorm |
| `planner` | t1k:plan, t1k:cook |
| `docs-manager` | t1k:docs, t1k:cook (finalize) |
| `git-manager` | t1k:git, t1k:cook (finalize) |
| `project-manager` | t1k:cook (finalize) |
| `skills-manager` | t1k:triage, t1k:modules |

## Module-Aware Routing

Follow protocol: `rules/module-detection-protocol.md` to detect module state.

In the module-first architecture, **modules are the installable unit** (not kits). Each module has its own `module.json` with version, dependencies, skills, and activation keywords. Kits are container repos.

**Mode 1 — Single-Module Task** (keywords match 0-1 installed modules):
- Standard highest-priority routing — one agent per role
- Inject that module's skills into the agent (follow `rules/subagent-injection-protocol.md`)

**Mode 2 — Multi-Module Task** (keywords match 2+ installed modules):
- Context-based routing — each module's agent handles its own domain in parallel
- Triggers multi-agent pipeline (parallel domain agents)
- Each agent receives only its module's skills
- Integration planner assembles results

**Detection:** Count distinct installed modules matched by prompt keywords (from `module.json` activation fields or `t1k-activation-*.json` fragments).
- 0-1 modules → Mode 1
- 2+ modules → Mode 2

## Skill Auto-Activation

Follow protocol: `rules/activation-protocol.md`

## Priority Order

1. **T1K Commands** (all registry-routed workflows)
2. **Skills** (auto-activated by context)
3. **Standard Tools** (Read, Write, Edit, Bash — trivial tasks only)

## Mandatory Skill Usage (NEVER bypass)

These T1K skills exist for a reason — **ALWAYS invoke them, NEVER do their job manually**:
- `/t1k:sync-back` — sync .claude/ changes to kit repos. **MUST run as a background sub-agent** (`Task` tool, `run_in_background: true`) to avoid interrupting the user. NEVER manually copy files and NEVER run inline. See `rules/error-recovery.md` → "Background Sub-Agent Invocation".
- `/t1k:issue` — report skill/agent bugs to kit repos. **MUST run as a background sub-agent** (same pattern). NEVER manually create GitHub issues and NEVER run inline.
- `/t1k:triage` — process issues/PRs from kit repos. NEVER manually browse and process issues
- `/t1k:git` — git operations. NEVER run raw git commit/push without the skill's security checks

## Related Rules

- `routing-protocol.md` — routing resolution algorithm
- `activation-protocol.md` — skill activation algorithm + fragment schema
- `subagent-injection-protocol.md` — skill injection for subagents
- `module-detection-protocol.md` — module state detection
- `error-recovery.md` — error type → command → agent
- `session-lifecycle.md` — start/during/finalize/wrap protocol
- `command-chaining.md` — chain patterns and auto-chains
- `execution-context.md` — context detection
