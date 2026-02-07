# Feature Research: Brownfield Analysis Mode

**Domain:** CLI workflow tool with intelligent mode branching (brownfield codebase analysis)
**Researched:** 2026-02-08
**Confidence:** HIGH (domain is well-understood from existing GSD architecture and codebase analysis tool landscape)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these means brownfield mode feels broken or useless.

| # | Feature | Why Expected | Complexity | Notes |
|---|---------|--------------|------------|-------|
| TS-1 | **Auto-detect brownfield vs greenfield** | Users should not have to declare "I have existing code." The system must detect code files, package manifests, and config. Current `/gsd:new-project` Phase 1 already does this partially. | LOW | Existing logic detects `CODE_FILES` and `HAS_PACKAGE`. Enhance to be the authoritative branch point instead of just an "offer." |
| TS-2 | **4-dimension codebase scan** (structure, stack, problems, tests) | The whole promise of brownfield mode. Without comprehensive analysis, the tool is just a glorified `tree` command. Must cover: (1) directory structure and architecture, (2) technology stack and dependencies, (3) tech debt, bugs, security concerns, (4) test coverage and patterns. | MEDIUM | Maps directly to existing `gsd-codebase-mapper` focus areas: `arch`, `tech`, `concerns`, `quality`. The infrastructure exists; need to repackage output for brownfield flow. |
| TS-3 | **Human-readable findings summary** | Users need to see what was found BEFORE choosing next steps. Raw `.planning/codebase/*.md` files are for agents, not humans. Brownfield mode must synthesize findings into a concise, scannable presentation. | MEDIUM | Think "executive briefing" not "full audit report." Show counts, severity ratings, key highlights. User reads this, then decides direction. |
| TS-4 | **"Fix bugs" vs "Improve features" routing** | After seeing analysis, users must choose intent. Bug fixing demands different workflow (diagnose -> targeted fix -> verify) than feature improvement (plan -> implement -> verify). These are fundamentally different modes. | LOW | This is a single AskUserQuestion branch point. The downstream workflows already exist: `/gsd:debug` for fixes, `/gsd:plan-phase` + `/gsd:execute-phase` for improvements. |
| TS-5 | **Analysis context persists into downstream workflows** | If the system analyzes the codebase but then the planner/executor ignores those findings, the analysis was wasted. CONCERNS.md must feed into debug sessions. ARCHITECTURE.md must constrain planning. TESTING.md must guide test creation. | LOW | Already built into `gsd-planner` and `gsd-executor` via codebase document loading (see `gsd-codebase-mapper` why_this_matters section). Just needs the brownfield flow to ensure these files exist before downstream commands run. |
| TS-6 | **Greenfield flow remains unchanged** | Brownfield mode is an addition, not a replacement. If no code detected, the flow must be identical to current `/gsd:new-project`. Zero behavioral regression for greenfield users. | LOW | Architecture: brownfield branch happens in Phase 2 of new-project. If not triggered, flow continues to Phase 3 (deep questioning) as before. |

### Differentiators (Competitive Advantage)

Features that set brownfield mode apart from generic "analyze my code" tools. Not required, but make GSD's approach distinctly valuable.

| # | Feature | Value Proposition | Complexity | Notes |
|---|---------|-------------------|------------|-------|
| D-1 | **Prioritized problem ranking** | Don't just list problems -- rank them. Show "3 critical, 5 moderate, 8 minor" with the critical items front and center. Users waste time triaging when tools dump flat lists. Ranking by impact (what breaks) and fixability (how hard to address) makes the analysis immediately actionable. | MEDIUM | Requires the concerns-focus mapper agent to assign severity during analysis. Current CONCERNS.md template has categories (Tech Debt, Known Bugs, Security, Performance, Fragile Areas) but no cross-category severity ranking. Add a summary table at top. |
| D-2 | **Intent-aware questioning** | After routing (fix vs improve), ask DIFFERENT questions. Bug-fix mode: "Which of these problems is most urgent?" "Does anything currently prevent your users from working?" Feature-improve mode: "What capability should the codebase gain?" "What's the user-facing change you want?" This is the brownfield analog of greenfield's "deep questioning" phase. | MEDIUM | New questioning flows tailored per mode. Greenfield asks "what do you want to build?" -- brownfield-fix asks "what's broken?" and brownfield-improve asks "what should change?" Consult `questioning.md` techniques but apply to existing-code context. |
| D-3 | **Scoped analysis** (optional area focus) | Let users scope analysis to a subdirectory or subsystem. "I only care about the API layer" or "Just look at auth." Saves time on large codebases where full analysis takes minutes. | LOW | `gsd:map-codebase` already accepts `$ARGUMENTS` for focus area. Thread this through to brownfield analysis mode. |
| D-4 | **Analysis-to-roadmap pipeline** | After analysis and intent selection, automatically generate a roadmap that references specific findings. Bug-fix roadmap: phases organized by severity (critical first). Feature-improve roadmap: phases organized by dependency (foundation first). Both reference concrete files and line numbers from analysis. | HIGH | Requires a brownfield-specific roadmapper prompt that ingests codebase analysis as primary input (instead of user requirements as in greenfield). This is the most complex differentiator -- it bridges analysis and action. |
| D-5 | **Existing test awareness** | When planning fixes or improvements, know what tests already exist and what patterns they follow. Don't write Jest tests when the project uses Vitest. Don't create a new test directory when tests are co-located. Automatically inherit project conventions. | LOW | Already handled: TESTING.md and CONVENTIONS.md are loaded by planner/executor. Differentiator is surfacing test health in the findings summary: "47 tests found, 12 failing, 0 E2E tests, coverage estimated at 62%." |
| D-6 | **Incremental re-analysis** | After fixes are applied, re-analyze just the changed areas. Don't re-scan the whole codebase. Track what changed and verify improvements. "Before: 3 critical issues. After fix: 1 critical remaining." | HIGH | Requires diff-aware analysis. Could be implemented as: (1) track files changed in fix commits, (2) re-run relevant mapper agents scoped to changed files, (3) compare before/after CONCERNS.md. Valuable but complex. |
| D-7 | **Problem-to-debug session bridging** | When a user selects a specific problem from the analysis to fix, auto-create a debug session with symptoms pre-filled from CONCERNS.md findings. Skip the symptom-gathering phase of `/gsd:debug`. This mirrors how `diagnose-issues.md` workflow pre-fills from UAT gaps. | LOW | Pattern already exists in `diagnose-issues` workflow: `symptoms_prefilled: true` and `goal: find_root_cause_only`. Apply same pattern with CONCERNS.md as the symptom source instead of UAT.md. |

### Anti-Features (Deliberately NOT Building)

Features that seem valuable but create problems in this specific context.

| # | Anti-Feature | Why Requested | Why Problematic | Alternative |
|---|--------------|---------------|-----------------|-------------|
| AF-1 | **Real-time code monitoring** | "Detect when code changes and re-analyze automatically." | Burns tokens continuously. Users don't want surprise analysis runs. GSD is command-driven, not daemon-based. Context windows are finite. | On-demand re-analysis via `/gsd:map-codebase --refresh` or after phase execution. User triggers when ready. |
| AF-2 | **Automated fix application without routing** | "Just fix everything you find automatically." | Dangerous. Automated bulk fixes without user intent selection can: (1) break working code, (2) change behavior users depend on, (3) conflict with each other, (4) overwhelm the user with unexpected changes. | Always route through user decision. Present findings, let user choose what to address, then fix with verification. |
| AF-3 | **Static analysis tool integration** (ESLint, SonarQube, etc.) | "Parse ESLint output and incorporate into findings." | Adds hard dependencies on tools that may not be installed. Different projects use different linters. Configuration varies wildly. GSD uses AI agents (Read, Grep, Glob) which work universally -- no tool installation required. | AI agents can detect the same patterns static analyzers find (unused variables, missing error handling, complexity) by reading code directly. If lint config exists, agents can read it for context. |
| AF-4 | **Full dependency vulnerability scanning** | "Check npm audit / pip audit and report CVEs." | Security scanning is a specialized domain with dedicated tools (Snyk, Dependabot, npm audit). GSD's AI agents are not equipped to maintain a CVE database. False positives erode trust. | Note outdated/unmaintained dependencies in CONCERNS.md (agents can check last-updated dates). Recommend `npm audit` or equivalent as a manual step. Don't pretend to be a security scanner. |
| AF-5 | **Cross-repository analysis** | "Analyze my monorepo with 15 packages." | Scope explosion. Context windows can't hold 15 codebases simultaneously. Analysis quality degrades as scope grows. | Focus analysis on one package/service at a time. User can run `/gsd:map-codebase` scoped to each package. Each gets its own `.planning/codebase/` set. |
| AF-6 | **Historical trend analysis** | "Show me how tech debt has changed over the last 6 months." | Requires persistent storage across sessions, git history parsing at scale, and metric definitions that vary by project. Massive complexity for marginal value in a session-based tool. | Snapshot comparison: "Last analysis (date) found X issues. Current analysis finds Y." Simple before/after, not time-series. |
| AF-7 | **Code quality scoring** (A-F grades, numeric scores) | "Give my codebase a health score of 73/100." | Reductive. A single number hides what matters. Is 73 good? For what kind of project? Scores invite gaming ("how do I get to 80?") instead of fixing real problems. Scores also create false precision from inherently subjective analysis. | Categorized findings with severity (critical/moderate/minor) and actionable fix approaches. Users understand "3 critical security issues" better than "security score: 42." |

## Feature Dependencies

```
[TS-1] Auto-detect brownfield
    |
    v
[TS-2] 4-dimension codebase scan ──────────────> [D-3] Scoped analysis (enhances TS-2)
    |
    v
[TS-3] Human-readable findings summary ────────> [D-1] Prioritized problem ranking (enhances TS-3)
    |                                             [D-5] Existing test awareness (enhances TS-3)
    v
[TS-4] Fix vs Improve routing
    |
    ├── Fix route ──> [D-2] Intent-aware questioning (fix) ──> [D-7] Problem-to-debug bridging
    |                                                           |
    |                                                           v
    |                                                     [D-4] Analysis-to-roadmap (fix variant)
    |
    └── Improve route ──> [D-2] Intent-aware questioning (improve)
                          |
                          v
                    [D-4] Analysis-to-roadmap (improve variant)
                          |
                          v
                    [D-6] Incremental re-analysis (post-execution)

[TS-5] Context persistence ──> Required by ALL downstream features (cross-cutting)
[TS-6] Greenfield unchanged ──> Independent (guard rail, not dependency)
```

### Dependency Notes

- **TS-2 requires TS-1:** Can't scan codebase if brownfield not detected. TS-1 is the gate.
- **TS-3 requires TS-2:** Can't summarize findings without having run the scan.
- **TS-4 requires TS-3:** User must see findings before choosing direction.
- **D-1 enhances TS-3:** Prioritization makes the summary more actionable. Not blocked by it -- can add ranking later.
- **D-2 requires TS-4:** Intent-aware questions only make sense after routing decision is made.
- **D-4 requires D-2 and TS-2:** Roadmap generation needs both user intent (from questioning) and codebase analysis (from scan).
- **D-7 requires TS-2 (concerns output):** Debug bridging uses CONCERNS.md findings as pre-filled symptoms.
- **D-6 requires D-4 (completed roadmap execution):** Can only re-analyze incrementally after changes are made.
- **D-3 is independent:** Scoped analysis can be added to TS-2 at any time without affecting other features.
- **TS-5 is cross-cutting:** Every downstream feature depends on analysis context being available. Must be validated early.

## MVP Definition

### Launch With (v1)

Minimum viable brownfield mode -- what's needed to validate the concept.

- [x] **TS-1: Auto-detect brownfield** -- Gate everything else. Already partially implemented.
- [x] **TS-2: 4-dimension codebase scan** -- Core value. Reuse `gsd-codebase-mapper` agents.
- [x] **TS-3: Human-readable findings summary** -- Users must see results before acting.
- [x] **TS-4: Fix vs Improve routing** -- The branch point that makes brownfield mode distinct from greenfield.
- [x] **TS-5: Context persistence** -- Already built into agent architecture. Validate it works in brownfield flow.
- [x] **TS-6: Greenfield unchanged** -- Guard rail. Test greenfield path still works after changes.
- [x] **D-2: Intent-aware questioning** -- Without this, the post-routing experience is generic. This is what makes each route feel purposeful.

### Add After Validation (v1.x)

Features to add once core brownfield flow is working end-to-end.

- [ ] **D-1: Prioritized problem ranking** -- Trigger: users report analysis output is overwhelming or unactionable.
- [ ] **D-7: Problem-to-debug bridging** -- Trigger: users repeatedly copy-paste from analysis into debug sessions manually.
- [ ] **D-5: Test awareness in summary** -- Trigger: users ask "how tested is this code?" during analysis review.
- [ ] **D-3: Scoped analysis** -- Trigger: analysis takes too long on large codebases.

### Future Consideration (v2+)

Features to defer until brownfield mode proves its value.

- [ ] **D-4: Analysis-to-roadmap pipeline** -- HIGH complexity. Defer until fix/improve routing is validated. Users can use `/gsd:new-milestone` manually for now.
- [ ] **D-6: Incremental re-analysis** -- HIGH complexity. Defer until users complete full fix/improve cycles and ask "did it get better?"

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority | Depends On |
|---------|------------|---------------------|----------|------------|
| TS-1: Auto-detect | HIGH | LOW | **P1** | Nothing (entry point) |
| TS-2: 4-dimension scan | HIGH | MEDIUM | **P1** | TS-1 |
| TS-3: Findings summary | HIGH | MEDIUM | **P1** | TS-2 |
| TS-4: Fix/Improve routing | HIGH | LOW | **P1** | TS-3 |
| TS-5: Context persistence | HIGH | LOW | **P1** | TS-2 (validation) |
| TS-6: Greenfield guard | HIGH | LOW | **P1** | TS-1 |
| D-2: Intent questioning | HIGH | MEDIUM | **P1** | TS-4 |
| D-1: Problem ranking | MEDIUM | MEDIUM | **P2** | TS-3 |
| D-7: Debug bridging | MEDIUM | LOW | **P2** | TS-2 |
| D-5: Test awareness | MEDIUM | LOW | **P2** | TS-2 |
| D-3: Scoped analysis | MEDIUM | LOW | **P2** | TS-2 |
| D-4: Analysis-to-roadmap | HIGH | HIGH | **P3** | D-2, TS-2 |
| D-6: Incremental re-analysis | MEDIUM | HIGH | **P3** | D-4 |

**Priority key:**
- **P1:** Must have for launch (brownfield mode is broken without these)
- **P2:** Should have, add when core flow proves out
- **P3:** Nice to have, future consideration after validation

## Competitor Feature Analysis

| Feature | Current GSD (map-codebase) | Claude Code (native) | Cursor / AI IDEs | Our Brownfield Mode |
|---------|---------------------------|---------------------|-------------------|---------------------|
| Auto-detect existing code | Partial (detects, offers mapping) | None (user drives) | Implicit (always in IDE context) | Full auto-detect with mode branching |
| Structured analysis | 7 documents, 4 parallel agents | Ad-hoc (user asks questions) | Codebase indexing (semantic search) | 4-dimension scan with human-readable summary |
| Problem identification | CONCERNS.md (thorough but raw) | Only if user asks | Inline warnings, no system view | Prioritized problems with severity ranking |
| Fix vs improve routing | None (user picks commands manually) | None (user decides) | None (user decides) | Automatic intent detection and workflow routing |
| Context persistence | Strong (7 codebase docs loaded by agents) | Weak (per-conversation) | Medium (project indexing) | Strong (analysis feeds all downstream agents) |
| Fix workflow | `/gsd:debug` (scientific method) | Ad-hoc | Inline suggestions | Analysis-informed debug sessions with pre-filled symptoms |
| Improvement workflow | `/gsd:plan-phase` + `/gsd:execute-phase` | Ad-hoc | Generate/apply diffs | Intent-aware planning with codebase constraints |

**Key insight:** No existing tool combines structured codebase analysis with intent routing into specialized fix/improve workflows. AI IDEs offer inline suggestions but lack system-level analysis. Static analysis tools lack the fix/improve workflow. GSD's brownfield mode bridges the gap: understand the system, then act on it with purpose.

## Sources

- GSD-Opus46 source code analysis (direct codebase reading):
  - `/Users/redinmay/myprj/gsd-opus46-dev/commands/gsd/new-project.md` -- current brownfield detection logic
  - `/Users/redinmay/myprj/gsd-opus46-dev/commands/gsd/map-codebase.md` -- existing codebase mapping orchestrator
  - `/Users/redinmay/myprj/gsd-opus46-dev/agents/gsd-codebase-mapper.md` -- 4-focus mapper agent
  - `/Users/redinmay/myprj/gsd-opus46-dev/agents/gsd-debugger.md` -- debug workflow (fix route target)
  - `/Users/redinmay/myprj/gsd-opus46-dev/get-shit-done/workflows/diagnose-issues.md` -- parallel diagnosis pattern
  - `/Users/redinmay/myprj/gsd-opus46-dev/get-shit-done/templates/codebase/concerns.md` -- problem documentation template
  - `/Users/redinmay/myprj/gsd-opus46-dev/.planning/PROJECT.md` -- project requirements and constraints
  - `/Users/redinmay/myprj/gsd-opus46-dev/.planning/codebase/CODEMAP.md` -- system architecture overview
- Domain knowledge from codebase analysis tool patterns (training data, flagged as MEDIUM confidence):
  - Feature expectations derived from SonarQube, CodeClimate, Codacy feature sets
  - Anti-pattern awareness from static analysis tool adoption failure patterns
  - Brownfield development methodology from software engineering practices

---
*Feature research for: Brownfield Analysis Mode in GSD-Opus46*
*Researched: 2026-02-08*
