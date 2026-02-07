<purpose>
Orchestrate brownfield codebase analysis by spawning gsd-brownfield-analyzer agent and presenting results.

The workflow reads NO codebase documents directly. It delegates all analysis work to the agent, receives a confirmation, reads the agent's output file for presentation, and returns a structured result.

Input: .planning/codebase/ (7 documents created by map-codebase workflow)
Output: .planning/brownfield-analysis.md (written by agent) + inline dashboard for user
</purpose>

<philosophy>
**Orchestrator stays lean:**
This workflow does NOT read .planning/codebase/*.md documents. The agent reads them. The workflow only reads .planning/brownfield-analysis.md (the agent's output) for presentation.

**Stateless:**
This workflow does NOT write STATE.md, PROJECT.md, or any planning file. It only orchestrates the agent and presents results. State updates happen when new-project.md integrates this workflow in Phase 4.

**Analysis then routing:**
Steps 1-5 perform analysis and present results. Steps 6-9 handle purpose routing — purpose selection, questioning, debug bridging, and roadmap generation. Purpose routing runs by default; callers can opt out with `purpose_routing: false` for standalone analysis.

**Follow map-codebase pattern:**
Spawn agent via Task(), agent writes file, agent returns lightweight confirmation, workflow presents results to user.
</philosophy>

<process>

<step name="check_prerequisites">
Verify that codebase mapping has been completed:

```bash
ls .planning/codebase/*.md 2>/dev/null | wc -l
```

**If 0 files found:**
```
Codebase documents not found. The brownfield analyzer needs .planning/codebase/*.md documents as input.

Run `/gsd:map-codebase` first to map the codebase, then re-run this workflow.
```
Stop workflow. Do not proceed.

**If 1-6 files found:**
Note which documents are available. Proceed with partial analysis. The agent handles missing documents gracefully (marks dimensions as "Not available").

**If 7 files found:**
All documents available. Proceed normally.

Continue to determine_scope.
</step>

<step name="determine_scope">
Check if a scope parameter was provided in the workflow invocation.

The scope parameter is an optional subdirectory path (e.g., `src/services/`, `app/api/`) passed by the caller (future new-project.md or manual invocation).

**If scope is provided:**
Store the scope path. It will be passed to the agent in the next step.
Validate the scope path is a plausible directory (contains `/` or is a top-level directory name).

**If no scope is provided:**
Default to full codebase analysis. No filtering.

Do NOT ask the user for scope. The caller decides whether to pass scope. This keeps the workflow non-interactive.

Continue to run_analysis.
</step>

<step name="run_analysis">
Spawn the brownfield-analyzer agent to synthesize codebase documents.

Use Task tool with:
  subagent_type: "gsd-brownfield-analyzer"
  description: "Analyze codebase documents and write brownfield summary"

Prompt (pass to agent):
```
First, read your agent definition for full instructions:
@agents/gsd-brownfield-analyzer.md

{If scope is provided:}
Scope: {scope_path}
Only include findings with file paths starting with `{scope_path}`.

{If no scope:}
Scope: full codebase (no filtering)

Analyze the .planning/codebase/*.md documents.
Write .planning/brownfield-analysis.md using the brownfield-summary template.
Return executive summary confirmation only (~20 lines).
```

Wait for the agent to complete.

**If the agent fails or returns an error:**
- Inform the user: "코드베이스 분석 에이전트가 실패했습니다."
- Check if `.planning/brownfield-analysis.md` was partially written. If so, note partial state.
- Offer to retry the analysis or proceed with limited context.
- If retry: re-spawn the agent with the same parameters.
- If proceed: skip to return_result with health="Unknown" and empty concerns.

**If the agent returns a scope-empty message:**
- Present the scope-empty message to the user (the agent returns this instead of writing a file).
- Offer to retry with a broader scope or without scope.
- Do NOT continue to present_dashboard (there is no file to read).

Read the agent's return value for the executive summary confirmation (health rating, summary table, top concerns).

Continue to present_dashboard.
</step>

<step name="present_dashboard">
Read the executive summary from the agent's output file and present it inline to the user.

**First, verify the file exists:**
Check if `.planning/brownfield-analysis.md` exists. If the file does not exist, inform the user that analysis output is missing and offer to retry the analysis step.

Read `.planning/brownfield-analysis.md` — extract the content from the beginning through the end of the "Top Concerns" section (approximately the first 30-40 lines, stopping before the "Architecture Overview" section).

Present to the user inline (this IS the 10-line dashboard from ANALYSIS-02):

```
## Codebase Analysis Complete

**Health:** {health_rating from document header}
{If scoped: **Scope:** `{scope_path}`}

| Dimension | Finding | Confidence |
|-----------|---------|------------|
{7 rows from Executive Summary table}

**Top Concerns:**
{numbered list of top 3-5 concerns with severity tags}

---
Full analysis: `.planning/brownfield-analysis.md`
```

**Important:** Read only the executive summary + top concerns sections from the file. Do NOT read or display the detailed sections (Architecture Overview, Technology Stack, etc.). Those are Tier 2 reference material the user can consult in the file.

Continue to return_result.
</step>

<step name="return_result">
Return a structured result to the caller (future new-project.md or manual invocation).

```
## Analysis Pipeline Complete

**Output:** `.planning/brownfield-analysis.md`
**Health:** {health_rating}
**Scope:** {scope_path or "full codebase"}
**Top concern:** {first concern title and severity}

Ready for purpose routing (Phase 3).
```

This lightweight return enables the caller to decide next steps based on health rating and top concerns without re-reading the analysis file.

**Continuation check:**
If `purpose_routing` parameter is true (or not explicitly set to false):
  Continue to select_purpose.

If `purpose_routing` is explicitly false:
  End workflow here. (Backward compatible with standalone analysis invocations.)

Default: When invoked without explicit `purpose_routing` parameter, continue to select_purpose.
This makes purpose routing the default behavior. Callers that want analysis-only must explicitly pass `purpose_routing: false`.

**Rationale (diverges from 03-RESEARCH.md Pattern 5):** The research recommended defaulting to false (analysis-only) for backward compatibility. However, the primary caller will be `new-project.md` (Phase 4) which always wants the full pipeline. Making purpose routing the default avoids requiring every caller to explicitly opt in. The minority case (standalone analysis) can opt out with `purpose_routing: false`. This design choice prioritizes the common case over the legacy case.
</step>

<step name="select_purpose">
Read the analysis health rating and top concerns from the present_dashboard output (already in context from Step 4).

**Determine purpose suggestion based on analysis:**
- If health is "Concerning" AND analysis has >= 2 critical concerns:
  Suggest "Fix" — "Your codebase has {N} critical issues. Addressing these first is recommended."
- If health is "Moderate" AND analysis has >= 3 moderate concerns:
  Suggest "Improve" — "Several areas could be strengthened. A good time to enhance capabilities."
- If health is "Good":
  Suggest "Improve" or "Refactor" — "Codebase is healthy. Good time to add features or clean up."
- Otherwise:
  No suggestion — present all options equally.

Use AskUserQuestion:
  header: "Purpose"
  question: "{Suggestion context, if any}. What do you want to do with this codebase?"
  options:
    - "Fix issues" — Address bugs, security issues, broken functionality
    - "Add/improve features" — Enhance existing capabilities, add new ones
    - "Refactor/restructure" — Improve code quality, architecture, patterns
    - "Something else" — I'll explain my goal

**If "Something else" selected:**
Ask freeform: "What's your goal?"
Based on response, either:
  - Map to the closest mode (fix/improve/refactor) if response clearly fits one
  - Continue with "other" mode questioning if response is genuinely different

Store the selected purpose (fix | improve | refactor | other).

Continue to purpose_questioning.
</step>

<step name="purpose_questioning">
Load questioning reference: @get-shit-done/references/brownfield-questioning.md

Branch based on selected purpose from Step 6:

**If purpose == "fix":**
Follow the fix_thread from brownfield-questioning.md:
  1. Present top concerns from analysis as selectable options (AskUserQuestion, multiSelect: true)
     Include severity tags on each option.
  2. For each selected concern, ask 1-2 adaptive follow-ups:
     - Observation: "Have you seen this in practice?" (yes with details / yes can't reproduce / no)
     - Impact: "How does this affect you?" (blocks users / degrades experience / slows development / minor)
  3. Confirm priority order with user.
  4. Ask scope: root cause fix vs quick patch vs mix.
  5. Decision gate: ready for roadmap?

**If purpose == "improve":**
Follow the improve_thread from brownfield-questioning.md:
  1. Ask vision: "What do you want this codebase to do that it doesn't do now?" (freeform)
  2. Present architecture fit: "Your codebase uses [pattern from analysis]. How does this fit?"
  3. Cross-reference affected areas with analysis concerns.
  4. Ask constraints (test coverage, performance, timeline) — skip irrelevant ones.
  5. Decision gate: ready for roadmap?

**If purpose == "refactor":**
Follow the refactor_thread from brownfield-questioning.md:
  1. Present concerns + structural findings as pain point options (AskUserQuestion, multiSelect: true)
  2. Ask target state per pain area: architecture, conventions, testing.
  3. Risk tolerance: small/safe vs moderate vs significant.
  4. Confirm strategy based on risk tolerance.
  5. Decision gate: ready for roadmap?

**If purpose == "other":**
Follow the other_thread from brownfield-questioning.md:
  1. Ask goal (freeform).
  2. Ask how existing codebase relates to goal.
  3. Ask which analysis findings are relevant.
  4. Decision gate: ready for roadmap?

**All modes:** Follow questioning.md philosophy — adaptive, not checklist. Skip questions that are irrelevant based on prior answers. Dive deeper where the user shows energy.

Store questioning output as purpose_context (selected concerns/improvements/refactoring areas + priorities + constraints + target state).

If purpose is "fix" AND user chose "debug the top issue first" at decision gate:
  Continue to bridge_to_debug.
Else:
  Continue to generate_roadmap.
</step>

<step name="bridge_to_debug">
**Conditional:** Only runs if purpose is "fix" AND user chose to debug.

If this step was not triggered (purpose is not "fix" or user chose "plan first"):
  Skip to generate_roadmap.

For the user's highest-priority selected concern:

Use AskUserQuestion:
  header: "Debug Bridge"
  question: "Start debugging '[concern title]' now with pre-filled analysis findings?"
  options:
    - "Debug now" — Create debug session, then continue to roadmap
    - "Plan first" — Skip debug, go straight to roadmap
    - "Debug only" — Create debug session, skip roadmap generation

If "Debug now" or "Debug only":
  1. Create .planning/debug/ directory:
     ```bash
     mkdir -p .planning/debug
     ```

  2. Generate debug file slug from concern title:
     Lowercase, replace spaces with hyphens, remove special characters.
     Example: "N+1 query pattern" -> "n1-query-pattern"

  3. Write .planning/debug/{concern-slug}.md following the existing gsd-debugger debug_file_protocol format:

     ```markdown
     ---
     status: investigating
     trigger: "[Concern title from analysis]"
     created: [YYYY-MM-DD HH:MM]
     updated: [YYYY-MM-DD HH:MM]
     ---

     ## Current Focus

     hypothesis: [Inferred from analysis finding — what is likely causing this]
     test: [Suggested first verification step based on file paths from analysis]
     expecting: [Expected behavior based on concern description]
     next_action: Verify concern in code at [primary file path from analysis]

     ## Symptoms

     expected: [Expected behavior inferred from concern context]
     actual: [Concern description from analysis — the observed problem]
     errors: [Error details if available from analysis, else "See analysis finding"]
     reproduction: [Inferred from file paths and concern description]
     started: Detected during codebase analysis [analysis date]

     ## Eliminated

     (none yet)

     ## Evidence

     - timestamp: [analysis date]
       checked: Codebase analysis (brownfield-analysis.md)
       found: [Full concern description with severity tag]
       implication: [Impact assessment — why this matters]

     ## Resolution

     root_cause:
     fix:
     verification:
     files_changed: []
     ```

  4. Present to user:
     "Debug session created: `.planning/debug/{concern-slug}.md`

     Symptoms pre-filled from codebase analysis.
     Run `/gsd:debug` to start investigating. The debug command will detect this active session."

If "Debug now": Continue to generate_roadmap.
If "Debug only": Return result and end workflow.
If "Plan first": Continue to generate_roadmap.
</step>

<step name="generate_roadmap">
Spawn the gsd-roadmapper agent with purpose-aware context to create a brownfield roadmap.

Determine ordering rule from purpose:
  - fix -> "severity_desc" (critical first)
  - improve -> "dependency_asc" (foundations first)
  - refactor -> "impact_effort_ratio_desc" (quick wins first)
  - other -> "dependency_asc" (default to dependency order)

Use Task tool with:
  subagent_type: "gsd-roadmapper"
  description: "Create purpose-aware brownfield roadmap"

Prompt (pass to agent):
```
First, read your agent definition for full instructions:
@agents/gsd-roadmapper.md

<planning_context>

**Project:**
@.planning/PROJECT.md

**Codebase Analysis:**
@.planning/brownfield-analysis.md

**Roadmap Template:**
@get-shit-done/templates/brownfield-roadmap.md

**Purpose:** {fix | improve | refactor | other}

**Purpose Context:**
{Questioning output from Step 7:
  - Selected concerns/improvements/refactoring areas with priorities
  - User-provided constraints, target state, risk tolerance
  - Analysis findings relevant to the selected items}

**Ordering Rule:** {severity_desc | dependency_asc | impact_effort_ratio_desc}

</planning_context>

<instructions>
Create a purpose-aware roadmap for this brownfield project:
1. Read the brownfield-roadmap.md template for structure and ordering rules
2. Derive phases from the purpose context items (concerns / improvements / refactoring areas)
3. Order phases by the specified ordering rule
4. Map each item to exactly one phase
5. Derive 2-5 success criteria per phase (observable, with file paths from analysis)
6. Write .planning/ROADMAP.md using the brownfield roadmap template structure
7. Write .planning/STATE.md with purpose recorded in Decisions
8. Update .planning/REQUIREMENTS.md with item-to-phase traceability
9. Return ROADMAP CREATED with summary
</instructions>
```

Wait for agent to complete.

**If agent returns `## ROADMAP BLOCKED`:**
- Present the blocker information to the user
- Ask the user to provide missing context or resolve the issue
- Re-spawn the roadmapper agent with updated context when resolved

**If agent fails or returns an error:**
- Inform the user that roadmap generation failed
- Present what was gathered so far (purpose, questioning output, analysis)
- Offer to retry or to proceed manually with `/gsd:plan-phase 1`

**If agent returns `## ROADMAP CREATED`:**
Read and present the roadmap summary to the user.

Return structured result:

```
## Purpose Routing Complete

**Purpose:** {selected purpose}
**Ordering:** {ordering rule description}
**Roadmap:** `.planning/ROADMAP.md`
**Phases:** {N} phases derived from {M} items

{If debug session created:}
**Debug session:** `.planning/debug/{concern-slug}.md` — run `/gsd:debug` to investigate

Next: `/gsd:plan-phase 1` to begin executing the roadmap.
```

End workflow.
</step>

</process>

<success_criteria>
Phase 2 (Steps 1-5) — Analysis Pipeline:
- .planning/codebase/*.md documents verified (prerequisite check)
- gsd-brownfield-analyzer agent spawned via Task() with optional scope parameter
- Agent writes .planning/brownfield-analysis.md (workflow does NOT write this file)
- Executive summary (health + 7-dimension table + top concerns) presented inline to user
- Structured result returned to caller with health, scope, and top concern

Phase 3 (Steps 6-9) — Purpose Routing:
- User selects purpose from 4 options (fix/improve/refactor/other) with analysis-informed suggestion
- Purpose-specific questioning gathers context using brownfield-questioning.md reference
- Fix mode: concerns selected, validated, prioritized; debug bridge offered
- Improve mode: vision captured, architecture fit assessed, constraints gathered
- Refactor mode: pain points selected, target state defined, risk tolerance set
- Debug bridging (fix mode): .planning/debug/{slug}.md created in gsd-debugger format with status: investigating
- Roadmap generation: gsd-roadmapper spawned with purpose-aware context and ordering rule
- Fix roadmap ordered by severity, improve by dependency, refactor by impact/effort ratio

Backward compatibility:
- Steps 1-5 unchanged when purpose_routing: false is passed
- Standalone analysis invocations produce identical output to Phase 2 behavior
</success_criteria>
