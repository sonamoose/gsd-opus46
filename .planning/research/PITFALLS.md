# Domain Pitfalls

**Domain:** AI-powered CLI workflow tool with brownfield codebase analysis and intelligent mode branching
**Researched:** 2026-02-08
**Overall confidence:** MEDIUM (based on analysis of existing GSD codebase, Claude Code agent behavior patterns, and domain experience with AI-assisted development tools; WebSearch unavailable for external verification)

---

## Critical Pitfalls

Mistakes that cause rewrites, broken workflows, or user trust erosion.

### Pitfall 1: Analysis Agent Hallucination — Reporting Issues That Don't Exist

**What goes wrong:** AI agents (gsd-codebase-mapper) explore code via Read/Grep/Glob and infer problems that are not real. For example, an agent sees a function returning `{}` in a test fixture and reports "empty implementation stub" in CONCERNS.md. Or an agent reads an abstract base class and reports "missing implementation." The user then gets routed to a "fix" workflow for nonexistent issues.

**Why it happens:** LLM agents pattern-match against training data expectations. When they see code that looks like a common anti-pattern but is actually intentional (test mocks, factory patterns, configuration objects, abstract classes, intentionally minimal implementations), they flag it. The 4-dimension analysis compounds this because each agent independently creates false positives without cross-verification.

**Consequences:**
- User presented with "fix" options for code that works correctly
- Erodes trust in the entire analysis system — one wrong finding taints all findings
- User wastes time investigating phantom issues
- Downstream workflows (planner, executor) receive poisoned context and generate wrong plans

**Prevention:**
1. **Severity-gate all findings.** Agents must distinguish OBSERVED (objective: "file has 500 lines") from INFERRED (subjective: "this looks like technical debt"). Mark inferences with confidence levels.
2. **Cross-reference between analysis dimensions.** Structure analysis should inform problem analysis — if STRUCTURE.md shows a test directory, CONCERNS.md should not flag files in that directory as "stubs."
3. **Present analysis as hypothesis, not verdict.** Use language like "Potential concern: ..." not "Bug found: ..." The user decides which findings are real.
4. **Include evidence links.** Every finding must cite specific file paths and line ranges. This lets users quickly verify or dismiss.

**Detection (warning signs):**
- Analysis produces more than 5 "critical" concerns for a small codebase (<20 files)
- Findings reference test files, fixtures, or mock directories as problems
- Agent reports contradict each other (STACK.md says "testing framework configured" but CONCERNS.md says "no test infrastructure")

**Phase to address:** Analysis design phase — before implementing the 4-dimension agents. The prompt templates for each agent must include anti-hallucination guardrails.

---

### Pitfall 2: Mode Detection Threshold — The "What Counts As Existing Code?" Problem

**What goes wrong:** The brownfield detection in `new-project.md` Phase 1 uses file-extension matching (`find . -name "*.ts" -o -name "*.js" ...`) to decide if a codebase exists. This is a brittle heuristic. It will:
- False-positive on scaffolded projects (e.g., `npx create-next-app` just ran, there are `.ts` files but no meaningful custom code yet)
- False-positive on config-only repos (e.g., infrastructure repos with only `.js` config files)
- False-negative on uncommon languages (e.g., `.ex` for Elixir, `.kt` for Kotlin, `.lua`, `.zig` not listed)
- False-positive on vendor/generated code (e.g., `.js` files in `dist/`, generated protobuf code)

**Why it happens:** There is no clean binary between "greenfield" and "brownfield." The real question is "does this directory contain custom application code that a human wrote and wants to maintain?" but the detection uses file-extension existence as a proxy. The current exclusion is only `node_modules` and `.git`.

**Consequences:**
- User scaffolds a new project, runs `/gsd:new-project`, and gets routed to brownfield mode unnecessarily — this wastes time and confuses the user
- Infrastructure or config repo triggers brownfield analysis that finds no meaningful application patterns — produces thin/useless documents
- Project with Elixir or Kotlin code is treated as greenfield — existing code gets ignored
- Generated code gets analyzed as if it were hand-written — producing irrelevant findings

**Prevention:**
1. **Multi-signal detection.** Don't rely on file existence alone. Check:
   - File count threshold (>5 non-config source files)
   - Presence of custom code indicators (functions, classes, not just imports/exports)
   - Presence of meaningful project structure (multiple directories with source files)
   - Git history depth (>5 commits by humans suggests real project)
2. **Expand language coverage.** Add `.ex`, `.exs`, `.kt`, `.kts`, `.dart`, `.lua`, `.zig`, `.c`, `.cpp`, `.h`, `.rb`, `.php`, `.scala`, `.clj` to the detection list.
3. **Exclude generated/vendor directories.** Add `dist/`, `build/`, `.next/`, `__pycache__/`, `vendor/`, `target/`, `_generated/`, `.turbo/` to exclusions.
4. **Add a confidence signal.** Instead of binary yes/no, report "Detected N source files across M directories. Looks like [brownfield/scaffolded/greenfield]." Let the user confirm.

**Detection (warning signs):**
- Users say "I just ran create-next-app" and brownfield mode triggers
- Brownfield analysis produces mostly empty documents (all sections say "Not detected")
- Users in non-mainstream languages never get brownfield detection

**Phase to address:** Phase 1 (Setup/Detection) — the very first phase must nail this detection logic before building the analysis pipeline on top.

---

### Pitfall 3: Context Loss Between Analysis and Execution

**What goes wrong:** The brownfield analysis runs 4 parallel agents that produce 7 documents in `.planning/codebase/`. Then the user goes through questioning, requirements, and roadmap creation. By the time `/gsd:execute-phase` runs, the analysis findings are stale or the executor agent doesn't load the right codebase documents. The executor writes code that contradicts existing patterns because it didn't read CONVENTIONS.md, or creates duplicate functionality because it didn't read ARCHITECTURE.md.

**Why it happens:** GSD's architecture deliberately isolates agent context (each agent gets minimal context to avoid token waste). This is correct for greenfield, where there is little existing context to lose. But for brownfield, the existing codebase state IS the critical context. If the executor agent's prompt doesn't explicitly load the right `.planning/codebase/` documents, the analysis was wasted.

**Consequences:**
- Executor creates a new `utils/format.ts` when `lib/formatters.ts` already exists
- Executor uses a different naming convention than existing code
- Executor adds a new ORM when the project already uses Prisma
- New code doesn't integrate with existing architecture patterns

**Prevention:**
1. **Mandatory codebase context loading for brownfield.** When `.planning/codebase/` exists, executor and planner prompts MUST include relevant codebase documents. The existing plan-phase workflow already has a partial mapping (phase type to documents), but it must be enforced as mandatory, not optional.
2. **Staleness detection.** Compare `.planning/codebase/*.md` modification dates against recent git commits. If source code changed significantly since last mapping, warn user to re-run `/gsd:map-codebase`.
3. **Analysis-to-plan traceability.** PLAN.md should reference which codebase documents informed each task. This creates an audit trail.
4. **Codebase context hook.** The existing `gsd-context-loader.py` hook loads STATE.md and CODEMAP.md on session start. Extend it to also load a condensed codebase summary for brownfield projects.

**Detection (warning signs):**
- Executor creates files that duplicate existing functionality
- Code style in new files doesn't match existing codebase
- Planner creates tasks that contradict information in codebase documents

**Phase to address:** Two phases: (1) Analysis pipeline phase ensures documents are comprehensive. (2) Execution integration phase ensures downstream agents consume those documents.

---

### Pitfall 4: Treating Brownfield as Greenfield-With-Extra-Steps

**What goes wrong:** The brownfield workflow becomes: analyze codebase, then ignore analysis and run the standard greenfield project initialization flow. The analysis documents exist in `.planning/codebase/` but the questioning, requirements, and roadmap phases don't fundamentally change their behavior. Requirements start from scratch instead of inferring existing capabilities. Roadmap doesn't account for integration with existing code.

**Why it happens:** The greenfield flow is already complex (9 phases in `new-project.md`). Adding brownfield support by inserting an analysis step before the existing flow seems like the minimum-change approach. But brownfield projects need fundamentally different questioning ("What do you want to change?" not "What do you want to build?"), different requirements ("What exists + what's new" not "Everything is new"), and different roadmapping (integration-aware phases, not independent build phases).

**Consequences:**
- Requirements duplicate what already exists (user asked to scope features the app already has)
- Roadmap creates "build authentication" phase when authentication already works
- User spends 30 minutes re-specifying what their app already does
- The 4-dimension analysis feels like wasted effort because nothing downstream uses it

**Prevention:**
1. **Fork the questioning flow for brownfield.** When codebase map exists:
   - Start with "Based on the codebase analysis, here's what your app does: [summary from analysis]. What would you like to change or add?"
   - Pre-populate Validated requirements from existing capabilities
   - Only ask about net-new features
2. **Fork the roadmap for brownfield.** Brownfield phases should be integration-centric:
   - "Extend authentication to support OAuth" not "Build authentication"
   - "Refactor user service to support new fields" not "Create user management"
   - Phases should reference specific existing files to modify
3. **The fix-vs-improve fork.** After analysis, the user should choose:
   - "Fix" → Roadmap focuses on CONCERNS.md findings (tech debt, bugs, test gaps)
   - "Improve" → Roadmap focuses on new features integrated with existing architecture
   - "Both" → Prioritized combination

**Detection (warning signs):**
- Requirements phase asks "What are the main things users need to do?" even when codebase analysis exists
- Roadmap contains phases like "Set up project structure" when structure already exists
- User says "I already have this" during requirements scoping

**Phase to address:** Brownfield workflow design phase — this is the architectural decision that shapes everything downstream. Must be designed before implementing individual components.

---

### Pitfall 5: Analysis Agent Token Exhaustion on Large Codebases

**What goes wrong:** The 4 parallel codebase-mapper agents each need to explore a real codebase. For a large monorepo (e.g., 1000+ files, 200+ directories), the agents exhaust their context window trying to read too many files. They either hit the token limit and produce truncated documents, or they take 10+ minutes and the user gives up.

**Why it happens:** The current exploration strategy in `gsd-codebase-mapper.md` uses broad `find`, `grep -r`, and `ls` commands. For a 100-file project this works fine. For a 5000-file enterprise codebase, `grep -r "import" src/ | head -100` returns 100 lines that may all be from the same module, missing the big picture entirely. The agent has no sampling strategy — it either reads everything (token explosion) or reads the first N results (sampling bias).

**Consequences:**
- Analysis documents are incomplete (only cover the first few directories alphabetically)
- Agent crashes or returns error mid-analysis, producing partial documents
- Analysis takes 15+ minutes, user cancels
- Findings are biased toward whatever `find` returns first

**Prevention:**
1. **Codebase size pre-check.** Before spawning mapper agents, run a quick size assessment:
   ```bash
   find . -name "*.ts" -o -name "*.py" ... | wc -l
   ```
   If >500 files, switch to sampling mode. If >2000 files, require user to specify focus area.
2. **Progressive sampling strategy.** Instead of broad grep, use:
   - Directory tree structure first (understand shape)
   - README/docs files for high-level understanding
   - Entry points (main, index, app) for architecture
   - Sample 2-3 files per directory for conventions
   - Package manifests for stack (not grep-all-imports)
3. **Focus area scoping.** The `map-codebase` command already accepts an optional focus area argument. For large codebases, make it required: `/gsd:map-codebase api` or `/gsd:map-codebase frontend`.
4. **Depth limits.** Set explicit exploration budgets: "Read at most 30 files, use directory structure for the rest."

**Detection (warning signs):**
- Mapper agents return errors or timeout
- Analysis documents have uneven coverage (detailed for src/auth/, empty for src/billing/)
- File paths in documents all start with the same few directories
- Analysis takes >5 minutes for a medium codebase

**Phase to address:** Analysis agent implementation phase — the exploration strategy is core to the agent prompt design.

---

## Moderate Pitfalls

Mistakes that cause delays, poor UX, or technical debt in the tool itself.

### Pitfall 6: State Management Divergence Between Greenfield and Brownfield

**What goes wrong:** The `.planning/` directory structure diverges between greenfield and brownfield projects. Greenfield has `PROJECT.md`, `ROADMAP.md`, `STATE.md`. Brownfield additionally has `codebase/` with 7 documents. Downstream commands (`progress`, `execute-phase`, `plan-phase`) only know about the greenfield structure. When they encounter a brownfield project, they either ignore codebase documents or crash because they assume a structure that doesn't exist.

**Prevention:**
1. **Unified state schema.** Define a clear `.planning/` schema that works for both modes. `config.json` should include a `"mode": "greenfield|brownfield"` field. All downstream commands check this field.
2. **Optional codebase directory.** Commands that can use codebase context should check `if [ -d .planning/codebase ]` and load it when present, not require it.
3. **STATE.md brownfield section.** When in brownfield mode, STATE.md should track which codebase documents exist and when they were last refreshed.

**Detection (warning signs):**
- Commands crash with "file not found" when run on brownfield projects
- `progress` command doesn't show codebase mapping status
- Brownfield-specific state (analysis freshness, fix-vs-improve choice) gets lost between sessions

**Phase to address:** State management design phase — before implementing brownfield-specific commands.

---

### Pitfall 7: The "Fix vs Improve" Fork Creates Two Parallel Workflows That Both Need Maintenance

**What goes wrong:** After analysis, the user chooses "fix" or "improve." Each fork needs its own questioning flow, requirements templates, roadmap patterns, and execution strategies. Maintaining two parallel workflows doubles the surface area for bugs and inconsistencies. When you update the greenfield/improve path, you forget to update the fix path.

**Prevention:**
1. **Shared core, minimal forks.** The fork should happen as late as possible. Questioning, requirements, and roadmap should be mostly shared, with brownfield-aware modifications rather than completely separate paths.
2. **Fix-as-milestone, not fix-as-mode.** Instead of a separate "fix mode," treat fix requests as a milestone within the standard flow: "Milestone 1: Address tech debt" with phases derived from CONCERNS.md. Then "Milestone 2: New features" using the standard improve flow.
3. **Testing matrix.** Explicitly test: greenfield new-project, brownfield fix, brownfield improve, brownfield both. Four scenarios, not two.

**Detection (warning signs):**
- Bug reports that only affect brownfield-fix but not brownfield-improve (or vice versa)
- New features added to one path but not the other
- Duplicated code between fix and improve workflows

**Phase to address:** Workflow design phase — decide on forking strategy before implementation.

---

### Pitfall 8: Analysis Summaries That Are Too Long for Useful User Review

**What goes wrong:** The 4-dimension analysis produces 7 documents totaling 500-1000 lines. The user is presented with "Here's what I found" and a wall of text. They don't read it, blindly select "fix" or "improve," and the analysis effectively becomes unused. This is especially bad because the analysis took time and tokens — if the user ignores it, it was pure waste.

**Prevention:**
1. **Executive summary FIRST.** Before showing full analysis, present a 10-line summary:
   - Stack: [1 line]
   - Architecture: [1 line]
   - Top 3 concerns: [3 lines]
   - Test coverage: [1 line]
   - Recommendation: [1 line]
2. **Progressive disclosure.** User can expand each section if interested, or just act on the summary.
3. **Actionable framing.** Don't present findings as a report. Present them as decisions: "Found 3 critical concerns. Fix these first? Or proceed with new features?"
4. **Severity ranking.** Not all findings are equal. Sort by impact. The user should see the most important finding first.

**Detection (warning signs):**
- Users always select the first option without reading the analysis
- Users ask "what did the analysis find?" even though it was just presented
- Time between analysis completion and user response is <5 seconds (they didn't read it)

**Phase to address:** UX design phase — the presentation layer for analysis results.

---

### Pitfall 9: Parallel Analysis Agents Writing Conflicting Information

**What goes wrong:** The 4 mapper agents run in isolation. Agent 1 (tech) determines the project uses React 18. Agent 2 (arch) reads a different config file and reports React 19. Agent 3 (quality) finds ESLint configured for React 17. There is no reconciliation step. Downstream consumers of these documents get contradictory information.

**Prevention:**
1. **Single source of truth for facts.** Factual findings (versions, languages, frameworks) should come from ONE agent (tech focus). Other agents reference those facts, don't re-derive them.
2. **Post-analysis reconciliation pass.** After all 4 agents complete, run a lightweight consistency check: do version numbers match across documents? Do file paths mentioned in one document exist in STRUCTURE.md?
3. **Cross-agent context injection.** Consider giving the arch agent access to STACK.md (written by tech agent) as input, rather than having it independently determine the stack. This requires sequential execution for some agents, but prevents contradictions.

**Detection (warning signs):**
- Version numbers differ between STACK.md and CONVENTIONS.md
- File paths in CONCERNS.md don't exist in STRUCTURE.md
- Architecture patterns described in ARCHITECTURE.md contradict testing patterns in TESTING.md

**Phase to address:** Analysis pipeline design phase — agent orchestration order and data flow.

---

### Pitfall 10: Not Handling the "Partially Brownfield" Case

**What goes wrong:** User has a project that was scaffolded (has `package.json`, `tsconfig.json`, maybe a few generated files) but hasn't written real custom code yet. It's technically brownfield (files exist) but practically greenfield (no meaningful code to analyze). The analysis runs, finds nothing interesting, and the user is confused about why they went through an extra step.

**Prevention:**
1. **Code complexity threshold.** After detecting files, assess whether they contain custom logic:
   - Count non-config, non-generated source files
   - Check if files have been modified from scaffolding defaults (git diff against initial commit)
   - Look for custom imports, business logic functions, custom types
2. **Graceful downgrade.** If analysis finds "This is mostly scaffolding," say so and offer to switch to greenfield mode: "This looks like a freshly scaffolded project. Treat as new project?"
3. **Third option in detection.** Instead of binary brownfield/greenfield, offer: "Map codebase first / Start fresh (scaffolding only) / Skip mapping"

**Detection (warning signs):**
- Analysis documents for a "brownfield" project are mostly "Not detected" sections
- All source files match default scaffold templates
- Git history has only 1-2 commits (initial scaffolding)

**Phase to address:** Detection phase — the initial mode-determination logic.

---

## Minor Pitfalls

Mistakes that cause annoyance but are fixable without rework.

### Pitfall 11: Codebase Map Staleness After Execution

**What goes wrong:** User maps codebase, initializes project, executes 3 phases of changes. The `.planning/codebase/` documents now describe the project as it was, not as it is. Phase 4's planner loads ARCHITECTURE.md that describes the old architecture, not the one Phase 3 modified.

**Prevention:**
1. **Auto-staleness warning.** After each phase execution, compare last-modified dates of codebase docs vs latest code commits. If gap >1 phase, show: "Codebase map may be outdated. Run `/gsd:map-codebase` to refresh?"
2. **Incremental updates.** Instead of full re-analysis, allow updating specific documents: `/gsd:map-codebase architecture` to refresh just ARCHITECTURE.md and STRUCTURE.md.
3. **Phase-aware updates.** After execute-phase, have the verifier agent note which codebase documents are now potentially stale based on what files were changed.

**Phase to address:** Post-execution workflow — add staleness checks to verify-work or execute-phase completion.

---

### Pitfall 12: Language/Framework-Specific Analysis Gaps

**What goes wrong:** The current mapper agent exploration commands are heavily JavaScript/TypeScript-centric. The bash examples grep for `import.*from`, check for `package.json`, look for `src/` directories. A Python project with `requirements.txt`, `__init__.py` patterns, and `tests/` (not `src/__tests__/`) gets an incomplete analysis. A Go project with `go.mod`, `cmd/`, `internal/` structure is barely understood.

**Prevention:**
1. **Language detection first.** Before running exploration, detect primary language(s) from package manifests and file extensions. Then use language-appropriate exploration commands.
2. **Template library per language.** Maintain exploration command sets for at least: TypeScript/JavaScript, Python, Go, Rust, Java/Kotlin, Swift. Fall back to generic file-structure-only analysis for others.
3. **Extensible exploration.** Allow users to provide custom exploration hints: "This is a Django project" → use Django-specific checks (manage.py, settings.py, urls.py, models.py patterns).

**Phase to address:** Agent template design phase — extend mapper agent prompts with multi-language support.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Mode detection (Phase 1) | False positives on scaffolded projects, false negatives on non-JS languages | Multi-signal detection with user confirmation (Pitfalls 2, 10) |
| Analysis agent design | Hallucinated issues, token exhaustion on large codebases | Confidence-gated findings, progressive sampling (Pitfalls 1, 5) |
| Analysis-to-user presentation | Information overload, user ignores analysis | Executive summary first, progressive disclosure (Pitfall 8) |
| Fix vs Improve routing | Two parallel workflows that diverge over time | Shared core with late forking, fix-as-milestone (Pitfall 7) |
| State management | Greenfield and brownfield schemas diverge | Unified schema with optional codebase directory (Pitfall 6) |
| Execution integration | Analysis context not loaded by executor/planner | Mandatory codebase context loading, staleness detection (Pitfall 3) |
| Post-execution freshness | Codebase map becomes stale after changes | Auto-staleness warnings, incremental updates (Pitfall 11) |
| Multi-language support | JS/TS-centric exploration misses other stacks | Language detection first, per-language exploration templates (Pitfall 12) |
| Cross-agent consistency | Parallel agents produce contradictory findings | Single source of truth for facts, reconciliation pass (Pitfall 9) |

---

## Key Recommendations for Roadmap

1. **Detection must be right before analysis can be useful.** Phase 1 should focus exclusively on reliable brownfield detection with multi-signal heuristics and user confirmation. Ship this before building the analysis pipeline.

2. **Analysis quality is a trust problem, not a coverage problem.** It is better to produce 3 high-confidence findings than 20 mixed-confidence findings. A single hallucinated "critical bug" that turns out to be intentional code will make the user distrust all future analysis.

3. **The brownfield/greenfield fork should happen in the questioning phase, not before it.** Detection triggers a different questioning flow, which produces different requirements, which produces a different roadmap. Don't try to retrofit brownfield onto the existing greenfield pipeline — design the fork point deliberately.

4. **Context handoff is the hardest part.** The analysis is only valuable if downstream agents (planner, executor) actually consume it correctly. Budget significant effort for the integration between analysis output and execution input.

---

## Sources

- GSD-Opus46 codebase analysis: `/Users/redinmay/myprj/gsd-opus46-dev/commands/gsd/new-project.md` (current brownfield detection, Phase 1-2)
- GSD-Opus46 mapper agent: `/Users/redinmay/myprj/gsd-opus46-dev/agents/gsd-codebase-mapper.md` (exploration strategy, templates)
- GSD-Opus46 map-codebase workflow: `/Users/redinmay/myprj/gsd-opus46-dev/get-shit-done/workflows/map-codebase.md` (orchestration, parallel agents)
- GSD-Opus46 verification patterns: `/Users/redinmay/myprj/gsd-opus46-dev/get-shit-done/references/verification-patterns.md` (stub detection heuristics)
- GSD-Opus46 architecture: `/Users/redinmay/myprj/gsd-opus46-dev/.planning/codebase/CODEMAP.md` (system component map)
- GSD-Opus46 refactoring analysis: `/Users/redinmay/myprj/gsd-opus46-dev/ANALYSIS-REVISED.md` (axis analysis, context management patterns)
- Domain knowledge: AI agent-based codebase exploration patterns, LLM code analysis limitations (MEDIUM confidence — based on training data, not externally verified)

---

*Pitfalls research: 2026-02-08*
*Note: WebSearch was unavailable during this research session. External verification of pitfalls against community experience could not be performed. Confidence is MEDIUM based on direct analysis of the GSD codebase and domain expertise. Recommend re-running with WebSearch enabled for external validation.*
