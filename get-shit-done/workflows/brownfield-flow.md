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

**Analysis only (Phase 2):**
This workflow performs analysis and returns results. It does NOT ask users questions about purpose (fix/improve/refactor). Purpose routing is Phase 3, which will EXTEND this file with additional steps.

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
Read the agent's return value for the executive summary confirmation (health rating, summary table, top concerns).

Continue to present_dashboard.
</step>

<step name="present_dashboard">
Read the executive summary from the agent's output file and present it inline to the user.

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

End workflow.
</step>

</process>

<success_criteria>
- .planning/codebase/*.md documents verified (prerequisite check)
- gsd-brownfield-analyzer agent spawned via Task() with optional scope parameter
- Agent writes .planning/brownfield-analysis.md (workflow does NOT write this file)
- Executive summary (health + 7-dimension table + top concerns) presented inline to user
- Inline dashboard is approximately 10 lines of content (table rows + health + concerns header)
- Structured result returned to caller with health, scope, and top concern
- Workflow did NOT read .planning/codebase/*.md directly
- Workflow did NOT write STATE.md or any file besides delegating to agent
- Workflow did NOT ask user interactive questions (analysis only, no purpose routing)
</success_criteria>
