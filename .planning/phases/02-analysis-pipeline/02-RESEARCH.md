# Phase 2: Analysis Pipeline - Research

**Researched:** 2026-02-08
**Domain:** Workflow orchestration for brownfield codebase analysis pipeline (Markdown-defined agents, not library code)
**Confidence:** HIGH

## Summary

Phase 2 creates the `brownfield-flow.md` workflow and enhances the `gsd-brownfield-analyzer` agent to support 4-aspect parallel analysis, a user-facing summary dashboard, concern priority ranking, and scoped (subdirectory) analysis. The domain is GSD's own workflow/agent Markdown definition system — no external libraries are involved.

The primary challenge is **workflow orchestration design**: how `brownfield-flow.md` delegates to `brownfield-analyzer`, how it presents the analysis summary to the user, and how the scoped analysis option filters input. Phase 1 already created the agent definition and summary template; Phase 2 wires them into a functioning pipeline and adds the analysis intelligence (concern ranking, scoping).

**Primary recommendation:** Create `brownfield-flow.md` following the exact `map-codebase.md` orchestration pattern (spawn agent via Task(), receive confirmation, present to user). Enhance `brownfield-analyzer` to support an optional `scope` parameter for subdirectory focus, and formalize the 4-aspect analysis + concern ranking logic within the agent's process steps.

## Standard Stack

This phase involves **no external libraries or code**. All artifacts are Markdown workflow/agent definitions consumed by Claude Code's agent system. The "stack" is GSD's own conventions.

### Core

| Component | Type | Purpose | Location |
|-----------|------|---------|----------|
| Workflow definition | Markdown | Orchestrates analysis pipeline | `get-shit-done/workflows/brownfield-flow.md` |
| Agent definition | Markdown | Synthesizes 7 codebase docs | `agents/gsd-brownfield-analyzer.md` |
| Template | Markdown | Structures output format | `get-shit-done/templates/brownfield-summary.md` |

### Supporting (Already Exist from Phase 1)

| Component | Type | Purpose | Status |
|-----------|------|---------|--------|
| `brownfield-summary.md` | Template | Defines output structure with 7 dimensions | EXISTS - Phase 1 |
| `gsd-brownfield-analyzer.md` | Agent | Reads codebase docs, writes analysis | EXISTS - needs enhancement |
| `brownfield-detection.md` | Reference | Mode detection logic | EXISTS - Phase 1 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Single brownfield-analyzer agent | 4 separate analysis agents (one per dimension) | More parallelism but agent context is already sufficient for 7 docs (~200-1000 lines total); extra spawning overhead outweighs benefit for synthesis task |
| Inline analysis in workflow | Agent delegation | Inline would consume workflow context reading 7 docs; agent keeps orchestrator lean (established pattern) |
| Separate template for scoped analysis | Same template with conditional sections | Reuse is cleaner; scoped analysis just has fewer source docs but same output structure |

## Architecture Patterns

### Recommended Structure: brownfield-flow.md

The workflow follows the same pattern as `map-codebase.md`:

```
brownfield-flow.md (workflow)
    │
    ├── Step 1: Verify .planning/codebase/ exists (7 docs)
    │   └── If missing: error — user must run /gsd:map-codebase first
    │
    ├── Step 2: Determine scope
    │   └── If scope parameter provided: filter to subdirectory
    │   └── If no scope: analyze full codebase (default)
    │
    ├── Step 3: Spawn brownfield-analyzer agent via Task()
    │   └── Pass: scope (if any), analysis mode
    │   └── Agent reads .planning/codebase/*.md
    │   └── Agent writes .planning/brownfield-analysis.md
    │   └── Agent returns: executive summary confirmation (~20 lines)
    │
    ├── Step 4: Present analysis summary to user
    │   └── Read brownfield-analysis.md executive summary section
    │   └── Display health rating, 7-dimension table, top concerns
    │
    └── Step 5: Return structured result to caller
        └── { health, top_concerns, summary_path }
```

### Pattern 1: Workflow-Agent Delegation (Established GSD Pattern)

**What:** Workflow orchestrates by spawning agent via `Task()`. Agent does heavy work (reading 7 docs, synthesizing). Agent writes output file directly. Agent returns lightweight confirmation. Workflow presents results to user.

**When to use:** When the work involves reading many files and producing a synthesis. Keeps orchestrator context lean.

**Evidence from existing codebase:**
- `map-codebase.md` spawns 4 `gsd-codebase-mapper` agents, each writes documents directly, returns confirmation only
- `execute-phase.md` spawns `gsd-executor` agents with Task(), receives SUMMARY.md confirmation
- This is the canonical GSD pattern: orchestrator coordinates, agents execute

**How brownfield-flow uses it:**
```
Task(
  prompt="Analyze codebase documents and write brownfield analysis summary.

  Scope: [full | subdirectory path]

  Read .planning/codebase/*.md documents.
  Write .planning/brownfield-analysis.md using template.
  Return executive summary confirmation only.",
  subagent_type="gsd-brownfield-analyzer"
)
```

### Pattern 2: 4-Aspect Parallel Analysis Within Single Agent

**What:** The brownfield-analyzer agent performs 4 analysis dimensions sequentially within a single agent context, NOT as 4 parallel sub-agents.

**Why single agent, not 4 parallel:**
1. The input is 7 Markdown documents totaling 200-1000 lines. This fits easily in one agent context.
2. Cross-document synthesis REQUIRES seeing all docs simultaneously (e.g., connecting CONCERNS.md issues with STACK.md dependencies).
3. The `brownfield-summary.md` template already structures the output as a single document with 7 sections.
4. Spawning 4 sub-sub-agents adds complexity for minimal gain.

**The 4 analysis aspects (from ANALYSIS-01):**
1. **Structure/Architecture** — from ARCHITECTURE.md + STRUCTURE.md
2. **Tech Stack** — from STACK.md + INTEGRATIONS.md
3. **Concerns/Tech Debt** — from CONCERNS.md (primary) + cross-references
4. **Testing State** — from TESTING.md + cross-reference with CONCERNS.md gaps

**Evidence:** The existing `gsd-brownfield-analyzer.md` agent already reads all 7 docs and synthesizes. The 4-aspect requirement is about structuring the analysis output, not about parallelizing the agent.

### Pattern 3: Concern Priority Ranking (ANALYSIS-03)

**What:** Concerns are classified as critical/moderate/minor and sorted by impact.

**How it works within the agent:**
The `brownfield-summary.md` template already defines the Top Concerns section with severity tags:
```markdown
## Top Concerns
1. **[Concern]** — [description] (severity: critical)
2. **[Concern]** — [description] (severity: moderate)
3. **[Concern]** — [description] (severity: minor)
```

And the Detailed Concerns section groups by severity:
```markdown
**Critical:**
- [Concern] — [Impact + affected files]
**Moderate:**
- [Concern] — [Impact + affected files]
**Minor:**
- [Concern] — [Impact + affected files]
```

**What Phase 2 adds:** Formalize the severity classification criteria in the agent's `<philosophy>` or `<process>` section:
- **Critical:** Breaks users, blocks development, security vulnerability, data loss risk
- **Moderate:** Degrades experience, slows development, accumulates debt, performance issues
- **Minor:** Cosmetic, naming inconsistency, style deviation, low-impact tech debt

**Sorting rule:** Within each severity level, sort by scope of impact (number of files/modules affected). This gives a deterministic, reproducible ranking.

### Pattern 4: Scoped Analysis (ANALYSIS-04)

**What:** Option to analyze only a specific subdirectory instead of full codebase.

**Design approach:** The scope parameter filters which parts of the 7 codebase documents are relevant. It does NOT re-run `map-codebase` for a subdirectory.

**Implementation in the agent:**
1. Workflow passes `scope: "src/services/"` (or similar) to agent
2. Agent reads all 7 codebase documents but filters findings to those mentioning paths within the scope
3. Agent writes scoped analysis to `.planning/brownfield-analysis.md` (same path, overwrites)
4. Executive Summary table still has 7 rows but entries may show "No findings in scope" for irrelevant dimensions

**Why filter existing docs instead of re-mapping:**
- Re-running map-codebase for a subdirectory would require modifying the mapper agents (out of Phase 2 scope)
- The 7 codebase documents already contain file paths — filtering by path prefix is straightforward
- This matches the requirement: "specific subdirectory focused analysis option"

**Edge case:** If the scoped path has no mentions in any codebase document, the agent should inform the user that the scope yielded no relevant findings and suggest broadening or checking the path.

### Pattern 5: Summary Dashboard (ANALYSIS-02)

**What:** Present analysis results in a user-friendly dashboard of 10 lines or fewer.

**The dashboard IS the Executive Summary table.** The existing `brownfield-summary.md` template defines exactly this:

```markdown
## Executive Summary

| Dimension | Finding | Confidence |
|-----------|---------|------------|
| Architecture | [one-liner] | HIGH/MEDIUM |
| Tech Stack | [one-liner] | HIGH/MEDIUM |
| Code Quality | [one-liner] | HIGH/MEDIUM |
| Testing | [one-liner] | HIGH/MEDIUM |
| Integrations | [one-liner] | HIGH/MEDIUM |
| Structure | [one-liner] | HIGH/MEDIUM |
| Concerns | [one-liner] | HIGH/MEDIUM |
```

This is 7 data rows + header + separator = 9 lines. Plus the health rating line = 10 lines total. The template already meets the requirement.

**What Phase 2 adds:** The workflow must read this section from `brownfield-analysis.md` and present it inline to the user, rather than just pointing to the file. The workflow step should extract and display the Executive Summary + Top Concerns sections.

### Anti-Patterns to Avoid

- **Anti-Pattern: Re-reading raw source code.** The brownfield-analyzer must ONLY read `.planning/codebase/*.md`. Never Grep/Read source files directly. The codebase-mapper agents already did that work.

- **Anti-Pattern: Spawning 4 sub-agents for 4 aspects.** The 4-aspect analysis is a structuring concern within the single agent, not a parallelization opportunity. The input (7 docs) is small enough for one agent.

- **Anti-Pattern: Creating a new template for scoped analysis.** Reuse `brownfield-summary.md`. Scoped analysis uses the same structure with filtered content.

- **Anti-Pattern: Making the workflow interactive.** The brownfield-flow workflow in Phase 2 should NOT ask user questions. It runs analysis and returns results. User interaction (purpose selection, questioning) is Phase 3's responsibility.

- **Anti-Pattern: Modifying the 7 codebase documents.** The analysis pipeline is read-only with respect to `.planning/codebase/*.md`. It only writes `.planning/brownfield-analysis.md`.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Analysis output structure | Custom format for brownfield analysis | `brownfield-summary.md` template (Phase 1) | Template already defines exact 2-tier structure with executive summary + detailed sections |
| Agent-workflow communication | Complex return protocol | Same pattern as map-codebase confirmations | Agent writes file, returns ~20 line confirmation; orchestrator reads file for presentation |
| Severity classification | ML-based scoring or numeric ranks | Simple 3-tier classification (critical/moderate/minor) | CONCERNS.md already categorizes by area; mapping to severity is a rule-based decision |
| Codebase document discovery | Hardcoded 7 file paths | `Glob` on `.planning/codebase/*.md` | Handles missing documents gracefully; agent already does this in Phase 1 definition |

**Key insight:** Phase 1 already built 80% of the foundation. Phase 2 is primarily about creating the orchestration workflow (`brownfield-flow.md`) and enhancing the existing agent with scoping + formalized ranking logic. Most building blocks exist.

## Common Pitfalls

### Pitfall 1: Workflow Tries to Do Agent's Work

**What goes wrong:** The workflow reads all 7 codebase documents inline instead of delegating to the agent. This bloats the workflow's context and violates the delegation pattern.

**Why it happens:** It feels simpler to "just read the files" instead of spawning an agent. But the workflow has limited context and the 7 docs can be 1000+ lines total.

**How to avoid:** Strictly follow the map-codebase pattern: workflow spawns agent, agent reads and writes, workflow receives confirmation only. The workflow reads ONLY `brownfield-analysis.md` (the output), never `codebase/*.md` (the inputs).

**Warning signs:** If the workflow file has `Read` calls to `.planning/codebase/*.md`, it is doing the agent's work.

### Pitfall 2: Scoped Analysis Requires Re-Mapping

**What goes wrong:** The scoped analysis feature tries to re-run `map-codebase` for a subdirectory, which would require modifying the mapper agents and is out of Phase 2 scope.

**Why it happens:** Confusion between "mapping a directory" and "analyzing findings about a directory."

**How to avoid:** Scoped analysis FILTERS existing codebase documents by file path prefix. It does not re-map. The agent reads all 7 docs but only extracts findings mentioning paths within the scope.

**Warning signs:** If the plan includes modifying `gsd-codebase-mapper.md` or `map-codebase.md`, scope creep has occurred.

### Pitfall 3: Analysis Becomes Recommendation

**What goes wrong:** The analysis agent starts recommending fixes ("should migrate to X", "consider upgrading Y") instead of documenting current state.

**Why it happens:** Natural tendency to offer solutions when identifying problems.

**How to avoid:** The existing agent definition already has a critical rule: "DO NOT RECOMMEND FIXES OR IMPROVEMENTS. Document what IS, not what SHOULD BE." This must be preserved. Recommendations happen in Phase 3 (Purpose Routing).

**Warning signs:** If the brownfield-analysis.md output contains "should", "consider", "recommend", the agent is overstepping.

### Pitfall 4: Dashboard Exceeds 10-Line Target

**What goes wrong:** The summary dashboard grows beyond 10 lines, defeating the purpose of a scannable overview.

**Why it happens:** Adding context, explanation, or sub-items to the executive summary table.

**How to avoid:** The template already constrains this: 7 table rows + header/separator = 9 lines + health rating = 10. Enforce that each row is a ONE-LINER (the template says "10 words or fewer per row"). Detailed information goes in Tier 2 sections.

**Warning signs:** If the executive summary section exceeds ~15 lines including the table markup, it is too long.

### Pitfall 5: Missing Cross-Document Synthesis

**What goes wrong:** The agent produces per-document summaries instead of synthesizing across documents. "STACK.md says X. CONCERNS.md says Y." instead of connecting X and Y.

**Why it happens:** It is easier to summarize each document individually than to find cross-cutting patterns.

**How to avoid:** The agent's philosophy section already states: "Synthesize, don't summarize. Extract patterns that span multiple documents." The formalized ranking criteria should also require cross-referencing (e.g., "outdated dependency in STACK.md + dependency risk in CONCERNS.md = one merged concern").

**Warning signs:** If the brownfield-analysis.md has 7 sections that read like individual document summaries with no cross-references.

## Code Examples

These are Markdown workflow/agent definition patterns, not programming language code.

### Workflow Step: Spawn Brownfield Analyzer

Based on the established `map-codebase.md` pattern (lines 79-175):

```markdown
<step name="run_analysis">
Spawn brownfield-analyzer agent to synthesize codebase documents.

Task tool parameters:
  subagent_type: "gsd-brownfield-analyzer"
  description: "Analyze codebase documents and write brownfield summary"

Prompt:
  First, read your agent definition for full instructions.

  Scope: {scope_path or "full"}

  Analyze .planning/codebase/*.md documents.
  Write .planning/brownfield-analysis.md using the brownfield-summary template.
  Return executive summary confirmation only.

Wait for agent to complete.
Read agent's return for health rating and top concerns.
</step>
```

### Workflow Step: Present Dashboard to User

```markdown
<step name="present_dashboard">
Read the executive summary from brownfield-analysis.md:

Read .planning/brownfield-analysis.md (first ~30 lines for executive summary section)

Present inline:

  ## Codebase Analysis

  **Health:** {health_rating}

  | Dimension | Finding | Confidence |
  |-----------|---------|------------|
  {7 rows from executive summary table}

  **Top Concerns:**
  {top 3-5 concerns with severity tags}

  ---
  Full analysis: `.planning/brownfield-analysis.md`

</step>
```

### Agent Enhancement: Severity Classification Criteria

To add to `gsd-brownfield-analyzer.md` process section:

```markdown
<step name="classify_severity">
Classify each concern from CONCERNS.md into severity levels:

**Critical** — Any of:
- Breaks end-user functionality
- Security vulnerability with exploitable vector
- Data loss or corruption risk
- Blocks development progress on critical path

**Moderate** — Any of:
- Degrades user experience noticeably
- Slows development velocity
- Performance bottleneck under normal load
- Accumulating tech debt in core modules

**Minor** — Any of:
- Cosmetic or naming inconsistency
- Style deviation from conventions
- Low-traffic performance issue
- Tech debt in peripheral code

**Sorting within severity:**
Sort by scope of impact (number of files/modules affected), then by how
many other concerns it connects to (cross-document references).
</step>
```

### Agent Enhancement: Scoped Analysis Logic

To add to `gsd-brownfield-analyzer.md` process section:

```markdown
<step name="apply_scope">
If scope parameter is provided (a subdirectory path):

1. Read all 7 codebase documents as normal
2. For each finding, check if its file paths include the scope prefix
3. Include findings where ANY mentioned file path starts with the scope
4. For sections with no in-scope findings, write: "No findings in scope: {scope_path}"
5. Top Concerns section: only include concerns with in-scope file paths
6. Health rating: assess based on in-scope findings only

If scope yields zero findings across all documents:
  Return:
    "Scope '{scope_path}' yielded no findings in codebase documents.
    Verify the path exists and was covered during codebase mapping."

If no scope parameter: analyze all findings (default behavior, unchanged).
</step>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Binary brownfield detection (code exists?) | Multi-signal detection (5 signals) | Phase 1 of this project | More accurate mode determination |
| Manual "Map codebase first?" prompt | Auto-detection + auto-analysis pipeline | Phase 2 target | Removes a decision point, adds value instead |
| No analysis synthesis | 7-doc synthesis into structured summary | Phase 1 (agent+template) | Foundation exists, Phase 2 activates it |

**Deprecated/outdated:**
- The current `new-project.md` Phase 2 "Brownfield Offer" (ask user "Map codebase first?") will be replaced by automatic pipeline invocation in Phase 4.

## Open Questions

### 1. Scoped Analysis UX: How Does the User Specify Scope?

**What we know:** ANALYSIS-04 requires "specific subdirectory focused analysis option." The agent can filter by path prefix.

**What's unclear:** How does the user provide the scope path? Options:
- a) Workflow parameter: `brownfield-flow.md` accepts an optional `scope` argument
- b) Interactive prompt: workflow asks "Analyze full codebase or specific area?" with `AskUserQuestion`
- c) Deferred to Phase 4: the `new-project.md` command passes scope when delegating

**Recommendation:** Use option (a) — workflow accepts optional scope parameter. The caller (future `new-project.md` in Phase 4, or manual invocation) decides when to pass it. This keeps the workflow non-interactive (analysis only) while enabling scoping. The workflow definition just documents: "If `scope` is provided in the spawn prompt, pass it to the analyzer agent."

### 2. brownfield-flow.md Scope: Analysis Only or Analysis + Purpose?

**What we know:** ARCHITECTURE.md describes brownfield-flow as handling "Analysis -> Summary -> Purpose -> Questioning." But Phase 2 is Analysis Pipeline only; Phase 3 is Purpose Routing.

**What's unclear:** Should `brownfield-flow.md` in Phase 2 include purpose selection steps (as placeholders or stubs), or should it ONLY contain analysis steps?

**Recommendation:** Phase 2 creates brownfield-flow.md with analysis steps only (Steps 1-5 above). Phase 3 EXTENDS the same file to add purpose routing steps. This avoids writing placeholder/stub code that gets rewritten. The workflow file is modified in Phase 3, not replaced.

### 3. Does brownfield-flow.md Write Any Files Besides brownfield-analysis.md?

**What we know:** The agent writes `.planning/brownfield-analysis.md`. The workflow presents results.

**What's unclear:** Should the workflow also write/update any other files (e.g., STATE.md, a config flag)?

**Recommendation:** No. In Phase 2, the workflow ONLY orchestrates the agent and presents results. State updates happen when `new-project.md` integrates the workflow in Phase 4. Keeping the workflow stateless makes it testable and reusable.

## Sources

### Primary (HIGH confidence)

- `get-shit-done/workflows/map-codebase.md` — Canonical workflow orchestration pattern (4 parallel agents, confirmation-only returns, orchestrator stays lean). Lines 1-343.
- `agents/gsd-brownfield-analyzer.md` — Phase 1 agent definition. Already defines 7-doc input, synthesis process, executive summary return. Lines 1-205.
- `get-shit-done/templates/brownfield-summary.md` — Phase 1 template. Defines 2-tier structure, 7-dimension executive summary table, severity-tagged concerns. Lines 1-325.
- `get-shit-done/references/brownfield-detection.md` — Phase 1 detection logic. Defines MODE variable and integration with new-project.md. Lines 1-541.
- `.planning/research/ARCHITECTURE.md` — System architecture research. Defines brownfield-flow placement, data flow, component responsibilities. Lines 1-647.
- `get-shit-done/workflows/execute-phase.md` — Wave-based execution workflow pattern. Shows how workflows spawn agents, handle confirmations, present results. Lines 1-693.
- `agents/gsd-codebase-mapper.md` — Source agent that creates the 7 input documents. Shows exploration and document-writing pattern. Lines 1-763.
- `commands/gsd/new-project.md` — The command that will invoke brownfield-flow in Phase 4. Current Phase 2 (Brownfield Offer) shows integration point. Lines 1-991.
- `.planning/ROADMAP.md` — Phase structure and dependencies. Phase 2 depends on Phase 1 (complete). Lines 1-142.
- `.planning/REQUIREMENTS.md` — ANALYSIS-01 through ANALYSIS-04, INFRA-02 requirements. Lines 1-105.
- `.planning/phases/01-foundation/01-VERIFICATION.md` — Phase 1 verification. Confirms all foundation artifacts exist and meet requirements. 14/14 must-haves passed.

### Secondary (MEDIUM confidence)

- `get-shit-done/workflows/discuss-phase.md` — Gray area identification pattern. Informs how the workflow might handle ambiguity, though not directly applicable to analysis pipeline.

### Tertiary (LOW confidence)

- None. All findings are based on direct codebase analysis.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all components are existing GSD Markdown definitions, no external libraries
- Architecture: HIGH — directly follows established map-codebase.md and execute-phase.md patterns
- Pitfalls: HIGH — identified from actual existing agent/workflow constraints and cross-referenced with Phase 1 verification
- Open questions: MEDIUM — scope UX and workflow boundary are design decisions that need planner attention

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (stable — no external dependency changes possible; only internal GSD convention changes)
