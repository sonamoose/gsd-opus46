# Phase 5: State Integration + Polish - Research

**Researched:** 2026-02-08
**Domain:** State management template updates for brownfield context propagation to downstream agents (planner, executor)
**Confidence:** HIGH

## Summary

Phase 5 completes the brownfield milestone by ensuring that brownfield analysis context propagates correctly through the GSD system's state management layer (templates/project.md and templates/state.md) to downstream consumers (gsd-planner, gsd-executor, and all workflows that read STATE.md and PROJECT.md).

The research found that the **current templates already have brownfield support** at a foundational level. The project.md template has a `<brownfield>` section with 4-step instructions for brownfield initialization, and the state.md template has a `<state_reference>` cross-link to PROJECT.md. However, both templates lack **explicit structural sections** that downstream agents can reliably parse for brownfield context. Specifically: (1) project.md has no formal "Codebase Mode" section in its template markdown, (2) state.md has no fields for brownfield analysis references, codebase context, or purpose, and (3) the planner/executor agents read these files but have no instructions for how to interpret brownfield-specific content.

The key insight is that Phase 4 (new-project.md Phase 2B Step 3) already writes brownfield-specific content to the PROJECT.md instance (Codebase Mode, Primary Language, analysis reference in Context section, Validated requirements from ARCHITECTURE.md/STACK.md). However, this writing logic is hardcoded in the command file -- it is NOT guided by the template. Phase 5's job is to formalize these patterns in the templates so they are: (a) consistently applied, (b) discoverable by downstream agents, and (c) self-documenting.

**Primary recommendation:** Add a `## Codebase Context` section to the project.md template (within the `<brownfield>` guidance), add brownfield fields to the state.md template, and verify that gsd-planner and gsd-executor already read these files correctly (they do -- no agent modifications needed, only template changes ensure the content structure is reliable).

## Architecture Patterns

### Pattern 1: Current State of Templates

**project.md template** (`get-shit-done/templates/project.md`):
- Has a `<brownfield>` section (lines 146-167) with guidance: map codebase, infer Validated requirements, gather Active from user, initialize
- Has a `<state_reference>` section (lines 169-184) showing how STATE.md links to PROJECT.md
- The file template (lines 5-68) does NOT include a "Codebase Context" or "Codebase Mode" section in its Markdown structure
- The `<guidelines>` section (lines 72-123) does NOT mention brownfield-specific fields

**state.md template** (`get-shit-done/templates/state.md`):
- Template (lines 9-74) has: Project Reference, Current Position, Performance Metrics, Accumulated Context (Decisions/Pending Todos/Blockers), Session Continuity
- NO brownfield-specific fields anywhere in the template
- The `<sections>` documentation (lines 115-163) does not mention codebase context, analysis references, or purpose
- brownfield-flow Step 9 calls roadmapper which "writes STATE.md with purpose recorded in Decisions" (brownfield-roadmap.md line 129) -- but this happens as an ad hoc insertion, not guided by template structure

### Pattern 2: What Phase 2B Step 3 Currently Writes (Command-Level)

The `new-project.md` Phase 2B Step 3 (lines 249-272) currently instructs:
1. Read ARCHITECTURE.md and STACK.md
2. Infer Validated requirements from existing code capabilities
3. Add "Codebase Mode: brownfield" and "Primary Language: {PRIMARY_LANG}" to Context section
4. Reference .planning/brownfield-analysis.md in Context section
5. Write PROJECT.md using templates/project.md

This works, but the template itself has no structured section for this content. The writing instructions are in the command, not the template. If someone modifies the template or writes a brownfield PROJECT.md from a different entry point, the brownfield sections could be omitted or placed inconsistently.

### Pattern 3: How Downstream Agents Consume State

**gsd-planner** (`agents/gsd-planner.md`):
- Step `load_project_state`: Reads STATE.md for position, decisions, blockers, pending todos
- Step `load_codebase_context`: Checks `.planning/codebase/*.md` existence and loads relevant docs based on phase keywords
- Step `gather_phase_context`: Reads ROADMAP.md, CONTEXT.md, RESEARCH.md
- Uses `@.planning/PROJECT.md`, `@.planning/ROADMAP.md`, `@.planning/STATE.md` in plan context
- **Key finding:** The planner already loads codebase documents (ARCHITECTURE.md, STACK.md, etc.) via the `load_codebase_context` step. It does NOT read PROJECT.md for brownfield mode or analysis references -- it discovers codebase context independently.

**gsd-executor** (`agents/gsd-executor.md`):
- Step `load_project_state`: Reads STATE.md for position, decisions, blockers
- Step `load_plan`: Reads PLAN.md context references (which include `@.planning/PROJECT.md`, `@.planning/STATE.md`)
- **Key finding:** The executor reads PROJECT.md and STATE.md as referenced by the plan. Brownfield context reaches the executor through PROJECT.md's Context section and through STATE.md's Decisions section.

**execute-plan.md** workflow:
- Reads STATE.md first (load_project_state step)
- Reads config.json for commit/parallelization settings
- Passes STATE.md content to executor agents

**execute-phase.md** workflow:
- Reads STATE.md, loads config, loads parallelization settings
- Passes STATE_CONTENT to subagent prompts (line 278)

**resume-project.md** workflow:
- Reads STATE.md and PROJECT.md to restore session context
- Extracts: Core value, Current focus, Requirements (Validated/Active/Out of Scope), Key Decisions, Constraints

**transition.md** workflow:
- Reads STATE.md and PROJECT.md
- Updates STATE.md position, project reference, accumulated context

### Pattern 4: The Propagation Chain

The brownfield context propagation chain is:

```
brownfield-flow.md (writes brownfield-analysis.md, calls roadmapper)
    ↓
gsd-roadmapper (writes ROADMAP.md, STATE.md, REQUIREMENTS.md with purpose)
    ↓
new-project.md Phase 2B Step 3 (writes PROJECT.md with Validated reqs + Codebase Mode)
    ↓
gsd-planner (reads PROJECT.md, STATE.md, ROADMAP.md, .planning/codebase/*.md)
    ↓
PLAN.md <context> section (references PROJECT.md, STATE.md, ROADMAP.md)
    ↓
gsd-executor (reads PLAN.md context, executes, updates STATE.md)
```

**Current gaps in this chain:**
1. PROJECT.md template does not define where "Codebase Mode" goes -- it's ad hoc in the Context section
2. STATE.md template does not define where "purpose" or "analysis reference" goes -- it's inserted by roadmapper into Decisions
3. The planner's `load_codebase_context` step works independently of PROJECT.md's brownfield indicators -- it just checks if `.planning/codebase/*.md` files exist
4. There is no explicit "this is a brownfield project" flag in STATE.md that downstream agents can quickly check

### Pattern 5: What Actually Needs to Change

After analyzing the full propagation chain, the changes needed are **MINOR** (as ROADMAP.md stated):

**templates/project.md:**
1. Add a `## Codebase Context` section to the template markdown (inside `<template>` block) -- only present for brownfield projects
2. Expand `<brownfield>` guidance to specify exactly what fields to write and where
3. Update `<guidelines>` to document the Codebase Context section

**templates/state.md:**
1. Add a "Codebase Context" subsection under "Accumulated Context" -- for brownfield projects only
2. Document when and how this section is populated
3. Add purpose field to the template structure

**No agent modifications needed:**
- gsd-planner already has `load_codebase_context` that discovers .planning/codebase/*.md
- gsd-executor reads what's in PROJECT.md and STATE.md -- it doesn't need brownfield-specific instructions
- All workflows read STATE.md and PROJECT.md generically -- the content structure matters, not the workflow code

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Brownfield field definitions | New custom schema | Extend existing template sections with clear markers | Templates are the schema -- agents parse markdown sections by heading |
| Codebase context propagation | New propagation mechanism | Existing @file reference system in PLAN.md context | Plans already reference PROJECT.md, STATE.md -- content in those files automatically propagates |
| Analysis reference tracking | New reference tracking system | Simple markdown reference in PROJECT.md Context section | The existing "See: .planning/brownfield-analysis.md" pattern already works |
| Agent brownfield awareness | Modified agent definitions | Template-driven content structure | If the right sections exist in PROJECT.md and STATE.md, agents read them automatically |

**Key insight:** The GSD system propagates context through FILE CONTENT, not through agent code. If templates define the right sections, agents pick them up through their existing file-reading behavior. No agent modification needed.

## Common Pitfalls

### Pitfall 1: Over-Engineering State Propagation

**What goes wrong:** Creating new mechanisms (new agent steps, new workflow phases, new file formats) for brownfield context propagation.

**Why it happens:** The problem sounds complex ("context propagation to downstream agents") but the existing system already propagates everything through files. PROJECT.md and STATE.md ARE the propagation mechanism.

**How to avoid:** Only modify templates. Do not touch agent definitions, workflow definitions, or command definitions. The templates define structure; the content structure IS the propagation.

**Warning signs:** PR touches agents/*.md or workflows/*.md files. Those should not change in Phase 5.

### Pitfall 2: Making Templates Brownfield-Only

**What goes wrong:** Adding brownfield sections that break greenfield template usage or make templates confusing for greenfield projects.

**Why it happens:** Adding new sections without conditional guidance.

**How to avoid:** Use clear conditional markers: "For brownfield projects only" and "Omit for greenfield projects." The template should work for both modes. Greenfield projects simply skip the brownfield-specific sections.

**Warning signs:** Greenfield PROJECT.md has empty "Codebase Context" section with placeholder text.

### Pitfall 3: Duplicating Analysis Content in STATE.md

**What goes wrong:** Copying detailed analysis findings into STATE.md, making it exceed the 100-line size constraint.

**Why it happens:** Trying to make STATE.md self-contained for brownfield context.

**How to avoid:** STATE.md should reference analysis, not contain it. Use: "Codebase analysis: .planning/brownfield-analysis.md" (one line) not a summary of findings. The purpose and health rating are sufficient for quick context; detailed findings live in the analysis file.

**Warning signs:** STATE.md exceeds 100 lines after brownfield initialization.

### Pitfall 4: Missing the Validation Requirement (STATE-01)

**What goes wrong:** Focusing only on template structure without ensuring the "Validated requirements auto-inference" actually works end-to-end.

**Why it happens:** STATE-01 says "Validated 요구사항으로 자동 추론" -- this means the template must guide the writing agent to infer capabilities from ARCHITECTURE.md and STACK.md and write them as Validated requirements. The command (new-project.md Phase 2B Step 3) already does this, but the template's `<brownfield>` guidance should be the authoritative source.

**How to avoid:** Ensure the template's brownfield guidance includes explicit instructions for reading ARCHITECTURE.md and STACK.md, identifying existing capabilities, and formatting them as `- checkmark [Existing capability] -- existing` in the Validated section.

**Warning signs:** Brownfield PROJECT.md has empty "Validated" section.

### Pitfall 5: Forgetting Context Propagation Validation

**What goes wrong:** Updating templates but not verifying that the changes actually result in downstream agents receiving the context.

**Why it happens:** Templates define structure but don't execute. Validation requires tracing the chain: template -> written file -> agent reads file -> agent uses content.

**How to avoid:** Include a validation step in the plan that traces context from brownfield-analysis.md through PROJECT.md through STATE.md to a hypothetical PLAN.md context section. This can be done by reviewing the planner-subagent-prompt.md template which shows exactly what context the planner receives.

**Warning signs:** Templates updated but no verification that downstream agents would actually benefit.

## Specific Changes Needed

### templates/project.md Changes

**1. Add Codebase Context section to template markdown:**

```markdown
## Codebase Context

<!-- For brownfield projects only. Omit for greenfield. -->

**Mode:** [brownfield]
**Primary Language:** [Language from detection]
**Analysis:** `.planning/brownfield-analysis.md`
**Health:** [Good / Moderate / Concerning]
**Purpose:** [Fix / Improve / Refactor]
**Codebase Map:** `.planning/codebase/`
```

Place AFTER the existing `## Context` section and BEFORE `## Constraints`.

**2. Expand `<brownfield>` guidance:**

Add to the existing `<brownfield>` section:
- Explicit instructions to write the Codebase Context section
- Instructions to read ARCHITECTURE.md for architecture pattern and key capabilities
- Instructions to read STACK.md for language, framework, and runtime info
- Instructions to format inferred capabilities as Validated requirements with `existing` tag

**3. Add to `<guidelines>`:**

Add a "Codebase Context" entry explaining:
- Only present for brownfield projects
- Mode, language, health from detection/analysis
- Purpose from user selection during brownfield-flow
- Reference to analysis and codebase map for full details

### templates/state.md Changes

**1. Add Codebase Context subsection to template:**

Under `## Accumulated Context`, add:

```markdown
### Codebase Context

<!-- For brownfield projects only. Omit for greenfield. -->

**Analysis:** `.planning/brownfield-analysis.md`
**Purpose:** [Fix / Improve / Refactor]
**Health:** [Good / Moderate / Concerning]
```

This is 3 lines of content -- well within the 100-line budget.

**2. Update `<sections>` documentation:**

Add documentation for the Codebase Context subsection:
- When it's populated (after brownfield-flow completes)
- What it contains (analysis reference, purpose, health)
- How downstream agents use it (quick mode check, links to detailed analysis)

**3. Update `<lifecycle>`:**

Add to the Creation lifecycle:
- If brownfield: populate Codebase Context with analysis ref, purpose, health

### Verification Plan

**Context Propagation Validation:**

1. Trace: templates/project.md `<brownfield>` guidance -> new-project.md Phase 2B Step 3 writing logic -> resulting PROJECT.md has Codebase Context section with Validated requirements
2. Trace: brownfield-flow Step 9 -> roadmapper writes STATE.md -> STATE.md has purpose in Decisions + Codebase Context subsection
3. Trace: planner-subagent-prompt.md references `@.planning/PROJECT.md` and `@.planning/STATE.md` -> planner receives brownfield context
4. Trace: phase-prompt.md `<context>` references `@.planning/PROJECT.md` and `@.planning/STATE.md` -> executor receives brownfield context
5. Confirm: gsd-planner `load_codebase_context` step independently discovers `.planning/codebase/*.md` for brownfield projects

## Requirement Traceability

### STATE-01: Validated Requirements Auto-Inference

**Requirement:** "브라운필드 PROJECT.md에 기존 기능을 Validated 요구사항으로 자동 추론"

**How it's satisfied:**
- The project.md template `<brownfield>` section guides inferring Validated requirements from ARCHITECTURE.md and STACK.md
- new-project.md Phase 2B Step 3 implements this inference
- Phase 5's template update formalizes the guidance (currently implicit) into explicit template instructions

**What Phase 5 does:** Ensure the template explicitly instructs: "Read ARCHITECTURE.md and STACK.md. Identify what the codebase already does. Write these as Validated requirements with `existing` tag."

### STATE-02: Analysis Context Propagation to Downstream

**Requirement:** "분석 컨텍스트가 다운스트림 워크플로우(planner, executor)에 전달"

**How it's satisfied:**
- PROJECT.md's Codebase Context section carries mode, language, analysis reference, purpose
- STATE.md's Codebase Context subsection carries analysis reference, purpose, health
- PLAN.md `<context>` section references `@.planning/PROJECT.md` and `@.planning/STATE.md`
- gsd-planner independently loads `.planning/codebase/*.md` via `load_codebase_context` step
- All downstream agents (planner, executor) read PROJECT.md and STATE.md by default

**What Phase 5 does:** Ensure templates define the structural sections so content is reliably placed and parseable by downstream agents.

## Open Questions

### 1. Should the Codebase Context Section Be Separate or Merged into Context?

**What we know:** Currently, new-project.md Phase 2B Step 3 adds brownfield info to the existing `## Context` section. A separate `## Codebase Context` section would be cleaner but adds another section.

**What's unclear:** Whether downstream agents benefit from a separate section (easier to find) vs. merged content (fewer sections to scan).

**Recommendation:** Use a separate section. The planner and executor read by section heading. A dedicated `## Codebase Context` section is immediately identifiable as brownfield-specific context. This is a minor structural decision that the planner can finalize.

**Confidence:** MEDIUM -- either approach works; separate section is slightly cleaner for machine parsing.

### 2. Does brownfield-flow Roadmapper Already Write Correct STATE.md?

**What we know:** brownfield-roadmap.md line 129 instructs: "Write ROADMAP.md, STATE.md, and update REQUIREMENTS.md following the existing roadmapper protocol." The roadmapper writes STATE.md with purpose in Decisions.

**What's unclear:** Does the roadmapper currently write the Codebase Context subsection? Almost certainly not, since it doesn't exist in the template yet.

**Recommendation:** The template update adds the subsection. The roadmapper will follow the template when it writes STATE.md. The brownfield-flow's generate_roadmap step already passes analysis context and purpose to the roadmapper. Once the template defines where to put it, the roadmapper will comply.

**Confidence:** HIGH -- the roadmapper reads templates and follows their structure.

## Files Affected

| File | Change Type | What Changes |
|------|------------|--------------|
| `get-shit-done/templates/project.md` | MINOR UPDATE | Add Codebase Context section to template, expand `<brownfield>` guidance, update `<guidelines>` |
| `get-shit-done/templates/state.md` | MINOR UPDATE | Add Codebase Context subsection to template, update `<sections>` docs, update `<lifecycle>` |

**Files NOT changed (confirmed):**
- `agents/gsd-planner.md` -- already has `load_codebase_context` step
- `agents/gsd-executor.md` -- reads files by reference, no brownfield-specific logic needed
- `commands/gsd/new-project.md` -- Phase 2B Step 3 already writes brownfield PROJECT.md correctly
- `get-shit-done/workflows/brownfield-flow.md` -- already orchestrates the full pipeline
- `get-shit-done/workflows/execute-plan.md` -- reads STATE.md generically
- `get-shit-done/workflows/execute-phase.md` -- reads STATE.md generically
- `get-shit-done/workflows/resume-project.md` -- reads STATE.md and PROJECT.md generically

## Sources

### Primary (HIGH confidence)

- `get-shit-done/templates/project.md` (185 lines) -- Current template analyzed line-by-line. Brownfield section at lines 146-167, template structure at lines 5-68, guidelines at lines 72-123.
- `get-shit-done/templates/state.md` (177 lines) -- Current template analyzed line-by-line. Template structure at lines 9-74, sections docs at lines 115-163, lifecycle at lines 90-113.
- `agents/gsd-planner.md` (1393 lines) -- Downstream consumer analyzed. load_project_state at lines 1004-1023, load_codebase_context at lines 1025-1044, gather_phase_context at lines 1094-1120, plan context references at lines 421-428.
- `agents/gsd-executor.md` (825 lines) -- Downstream consumer analyzed. load_project_state at lines 19-54, load_plan at lines 57-71, state_updates at lines 721-757.
- `commands/gsd/new-project.md` (1209 lines) -- Phase 2B Step 3 analyzed (lines 249-272) for current brownfield PROJECT.md writing logic. Phase 4 brownfield logic at lines 374-399.
- `get-shit-done/workflows/brownfield-flow.md` (419 lines) -- Analyzed for state writing behavior. Philosophy at line 15 ("does NOT write STATE.md"), generate_roadmap at lines 318-393 writes STATE.md via roadmapper.
- `get-shit-done/templates/brownfield-roadmap.md` (142 lines) -- Analyzed for STATE.md writing instructions (line 129).
- `get-shit-done/templates/planner-subagent-prompt.md` (117 lines) -- Analyzed for context propagation path: passes @.planning/STATE.md and @.planning/PROJECT.md to planner.
- `get-shit-done/templates/phase-prompt.md` (567 lines) -- Analyzed for context propagation path: PLAN.md context section references @.planning/PROJECT.md, @.planning/STATE.md.
- `.planning/STATE.md` (94 lines) -- Current project state analyzed for existing brownfield fields.
- `.planning/PROJECT.md` (62 lines) -- Current project definition analyzed for existing brownfield fields.
- `.planning/ROADMAP.md` (159 lines) -- Phase 5 definition and success criteria at lines 95-107.
- `.planning/REQUIREMENTS.md` (105 lines) -- STATE-01 and STATE-02 requirement definitions at lines 31-32.
- `.planning/phases/04-command-integration/04-02-SUMMARY.md` -- Confirmed Phase 2B Step 3 implementation.
- `.planning/phases/04-command-integration/04-VERIFICATION.md` -- Confirmed greenfield/brownfield path traces end-to-end.
- `.planning/phases/04-command-integration/04-RESEARCH.md` -- Phase 4 research confirming integration points and convergence patterns.

## Metadata

**Confidence breakdown:**
- Template changes needed: HIGH -- direct analysis of template files and downstream consumers confirms minimal, targeted changes
- No agent changes needed: HIGH -- traced full propagation chain through planner, executor, and all workflows; all read files generically
- Validation approach: HIGH -- propagation chain can be traced through file references in planner-subagent-prompt.md and phase-prompt.md
- STATE-01 satisfaction: HIGH -- template guidance + existing Phase 2B Step 3 logic covers the requirement
- STATE-02 satisfaction: HIGH -- file-based propagation through existing @references confirmed for all downstream agents

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (stable -- internal template changes only, no external dependencies)
