# Phase 3: Purpose Routing - Research

**Researched:** 2026-02-08
**Domain:** Purpose routing, adaptive questioning, problem-debug bridging, and roadmap generation for brownfield codebase workflows (Markdown-defined agents/workflows, not library code)
**Confidence:** HIGH

## Summary

Phase 3 extends the existing `brownfield-flow.md` workflow (completed in Phase 2) with purpose routing: after the analysis dashboard is presented, the user selects a purpose (fix, improve, refactor), receives purpose-specific questioning, gets CONCERNS.md findings bridged into debug sessions when applicable, and receives an auto-generated roadmap ordered by their purpose (severity-first for fix, dependency-first for improve).

The primary challenge is **conversation flow design**: how to branch the workflow after analysis presentation, what questions to ask in each branch, how to carry analysis findings forward into debug or planning contexts, and how to generate a purpose-aware roadmap. All artifacts are Markdown workflow/agent definitions -- no external libraries.

**Key design insight:** Phase 3 operates at the intersection of three existing GSD patterns: (1) `brownfield-flow.md` analysis pipeline (Phase 2 output), (2) `discuss-phase.md` adaptive questioning pattern, and (3) `gsd:debug` + `gsd-roadmapper` for downstream consumption. Purpose routing is the bridge between analysis (what IS) and action (what to DO), and the design must respect the existing 3-layer architecture (commands -> workflows -> agents).

**Primary recommendation:** Extend `brownfield-flow.md` with 4 new steps after `return_result`. Create a new `get-shit-done/references/brownfield-questioning.md` reference file for purpose-specific questioning patterns. Create a new `get-shit-done/templates/brownfield-roadmap.md` template for purpose-aware roadmap generation. Do NOT create a new agent -- the workflow itself handles purpose selection and questioning (lightweight, interactive), and delegates roadmap generation to the existing `gsd-roadmapper` agent with purpose-aware context.

## Standard Stack

This phase involves **no external libraries or code**. All artifacts are Markdown workflow/agent/reference definitions consumed by Claude Code's agent system.

### Core (New or Modified)

| Component | Type | Action | Purpose |
|-----------|------|--------|---------|
| `brownfield-flow.md` | Workflow | EXTEND | Add steps 6-9: purpose selection, questioning, debug bridging, roadmap generation |
| `brownfield-questioning.md` | Reference | NEW | Purpose-specific questioning patterns (fix/improve/refactor) |
| `brownfield-roadmap.md` | Template | NEW | Purpose-aware roadmap structure with severity/dependency ordering |

### Supporting (Already Exist)

| Component | Type | Purpose | How Phase 3 Uses It |
|-----------|------|---------|---------------------|
| `brownfield-flow.md` (Phase 2) | Workflow | Analysis pipeline, steps 1-5 | Extended with new steps after `return_result` |
| `brownfield-analysis.md` output | Data | Synthesized analysis with severity-tagged concerns | Read by purpose routing to inform questions and roadmap |
| `questioning.md` | Reference | Greenfield questioning philosophy | Reuse philosophy, adapt techniques for brownfield context |
| `discuss-phase.md` workflow | Workflow | Gray area identification + adaptive questioning | Pattern model for brownfield questioning structure |
| `gsd:debug` command | Command | Debug session orchestration with symptom gathering | Target for CONCERNS.md bridging (pre-fill symptoms) |
| `gsd-debugger.md` agent | Agent | Scientific method debugging with persistent state | Receives bridged findings as pre-filled symptoms |
| `gsd-roadmapper.md` agent | Agent | Roadmap creation with phase/requirement mapping | Receives purpose-aware context for ordering logic |
| `brownfield-summary.md` template | Template | Analysis output structure | Defines data structure that purpose routing reads |
| `gsd-planner.md` agent | Agent | Phase plan creation | Downstream consumer of purpose-aware roadmap |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Extending brownfield-flow.md | New separate workflow (e.g., purpose-routing-flow.md) | Separate workflow means brownfield-flow returns, caller invokes another workflow -- extra orchestration overhead. Single workflow maintains continuity from analysis to purpose routing. |
| New reference file for questioning | Inline questioning logic in brownfield-flow.md | Inline makes the workflow file too large (Phase 2 already ~160 lines). Reference file follows established pattern (questioning.md exists for greenfield). |
| New template for roadmap | Reuse existing roadmap.md template | Brownfield roadmap needs different ordering logic (severity vs dependency) and different phase derivation (from concerns vs from requirements). Template specialization is warranted. |
| New agent for purpose routing | Workflow handles questioning inline | Purpose routing is interactive (user selects purpose, answers questions). Agents are for autonomous work. The workflow pattern (like discuss-phase.md) is the right fit for interactive questioning. |
| Separate debug bridging command | Inline bridging in brownfield-flow.md | Bridging logic is a single step: read CONCERNS.md -> generate debug context. Creating a separate command adds unnecessary complexity. |

## Architecture Patterns

### Recommended Structure: brownfield-flow.md Extension

The workflow extends the existing Phase 2 file by adding steps after `return_result`:

```
brownfield-flow.md (workflow) — EXTENDED
    |
    |--- Phase 2 Steps (existing, unchanged) ---
    |
    +-- Step 1: check_prerequisites (exists)
    +-- Step 2: determine_scope (exists)
    +-- Step 3: run_analysis (exists)
    +-- Step 4: present_dashboard (exists)
    +-- Step 5: return_result (exists, MODIFIED to continue instead of end)
    |
    |--- Phase 3 Steps (new) ---
    |
    +-- Step 6: select_purpose
    |   +-- Read analysis health rating and top concerns
    |   +-- Present purpose options: Fix / Improve / Refactor / Other
    |   +-- Suggest most likely purpose based on analysis
    |   +-- Store selected purpose for downstream steps
    |
    +-- Step 7: purpose_questioning
    |   +-- Load brownfield-questioning.md reference
    |   +-- Branch to fix / improve / refactor questioning thread
    |   +-- Gather purpose-specific context through adaptive questioning
    |   +-- Output: purpose context (symptoms, goals, constraints)
    |
    +-- Step 8: bridge_to_debug (fix mode only, conditional)
    |   +-- If purpose is "fix" AND concerns have critical severity:
    |   |   +-- Offer to start debug session with pre-filled findings
    |   |   +-- Generate debug session context from CONCERNS.md
    |   |   +-- Spawn /gsd:debug with pre-filled symptoms
    |   +-- If not fix mode: skip to Step 9
    |
    +-- Step 9: generate_roadmap
        +-- Spawn gsd-roadmapper with purpose-aware context
        +-- Fix mode: sort phases by severity (critical first)
        +-- Improve mode: sort phases by dependency (foundations first)
        +-- Refactor mode: sort phases by impact/effort ratio
        +-- Return roadmap for user approval
```

### Pattern 1: Purpose Selection from Analysis Context (ROUTE-01)

**What:** After the analysis dashboard is presented, the user selects their purpose. The system suggests the most likely purpose based on analysis findings.

**When to use:** Immediately after analysis dashboard presentation (Step 4/5 boundary).

**Design:**

The purpose selection uses `AskUserQuestion` with intelligent defaults. The analysis health rating and top concerns inform the suggestion:

```
Suggestion logic:
  IF health == "Concerning" AND critical_count >= 2:
    suggest "Fix" ("Your codebase has critical issues that should be addressed first")
  ELIF health == "Moderate" AND moderate_count >= 3:
    suggest "Improve" ("Several areas could be strengthened")
  ELIF health == "Good":
    suggest "Improve" or "Refactor" ("Codebase is healthy - good time to enhance or restructure")
  ELSE:
    no suggestion (present all options equally)
```

**Purpose options:**

| Purpose | Label | Description | When Appropriate |
|---------|-------|-------------|-----------------|
| Fix | "Fix issues" | Address bugs, security issues, broken functionality | Critical concerns present, things are broken |
| Improve | "Add/improve features" | Enhance existing capabilities, add new features | Working codebase, want to extend |
| Refactor | "Refactor/restructure" | Improve code quality, architecture, patterns | Tech debt accumulation, architecture pain |
| Other | "Something else" | Custom purpose, user explains | None of above fit |

**Evidence from existing patterns:**
- `new-project.md` Phase 2 (Brownfield Offer) uses AskUserQuestion for binary choice -- this extends to 4 choices
- `discuss-phase.md` uses AskUserQuestion for gray area selection -- same interaction model
- The analysis dashboard (Step 4) already shows health + concerns -- purpose selection follows naturally

**Step 5 modification:**

The existing `return_result` step ends the workflow. In Phase 3, it is modified to either:
- End workflow (if called in standalone analysis mode, backward compatible)
- Continue to `select_purpose` (if called within the brownfield pipeline)

This is controlled by a caller-provided parameter: `purpose_routing: true|false`. When `new-project.md` invokes brownfield-flow in Phase 4, it passes `purpose_routing: true`. Standalone invocations default to `false` (analysis only, no routing). This preserves backward compatibility.

### Pattern 2: Purpose-Specific Adaptive Questioning (ROUTE-02)

**What:** After purpose selection, the workflow asks different questions depending on whether the user wants to fix, improve, or refactor. Each questioning thread is specialized for its purpose.

**When to use:** Immediately after purpose selection.

**Design approach -- brownfield-questioning.md reference file:**

This file follows the pattern of `questioning.md` (greenfield questioning reference) but is specialized for brownfield contexts. The workflow loads this reference file and uses the relevant section.

**Fix Mode questioning thread:**

Fix mode focuses on narrowing down which problems to address and gathering reproduction context. The analysis already identified concerns -- fix mode questioning helps the user prioritize and provide context for debugging.

```
Fix mode questions (adaptive, not checklist):

1. Scope: "The analysis found N concerns. Which area do you want to focus on?"
   - Present top concerns from analysis as options
   - User selects 1-3 concerns to address

2. For each selected concern:
   a. Symptom check: "Have you observed [concern description] in practice?"
      - Yes, and here's what happens: [gather reproduction details]
      - Yes, but I'm not sure how to reproduce it
      - No, but the analysis flagged it as risky

   b. Impact: "How does this affect your users/development?"
      - Options based on concern severity (blocks users, degrades experience, slows development, etc.)

   c. Priority: "How urgently does this need fixing?"
      - Immediately (blocking production)
      - Soon (affecting users)
      - When convenient (tech debt)

3. Decision gate: "Ready to create a fix roadmap based on these priorities?"
```

**Improve Mode questioning thread:**

Improve mode focuses on what capabilities to add or enhance. The analysis provides the architecture and constraints context.

```
Improve mode questions (adaptive):

1. Vision: "What do you want this codebase to do that it doesn't do now?"
   - Freeform response, then follow-up probing (like greenfield questioning)

2. Architecture fit: "Based on the analysis, the codebase uses [architecture pattern].
   Your improvement would [extend existing patterns / require new patterns]."
   - Confirm understanding, clarify constraints

3. Affected areas: "This would touch [areas from analysis]. Any concerns about these areas?"
   - Present relevant concerns from analysis that intersect with improvement scope

4. Constraints: "Any performance targets, compatibility requirements, or deadlines?"
   - Options adapted from analysis (e.g., "Existing test coverage is N% -- maintain or improve?")

5. Decision gate: "Ready to create an improvement roadmap?"
```

**Refactor Mode questioning thread:**

Refactor mode focuses on identifying pain points and target state. The analysis provides the current state; refactor mode captures the desired future state.

```
Refactor mode questions (adaptive):

1. Pain points: "The analysis found these structural concerns. Which cause the most pain?"
   - Present moderate/minor concerns from analysis as options
   - Also ask: "Any pain points not captured in the analysis?"

2. Target state: "What should this codebase look like after refactoring?"
   - Architecture: "Keep current [pattern] or move toward [alternative]?"
   - Conventions: "Standardize on [identified patterns] or introduce new ones?"
   - Testing: "Current coverage is [N%]. Target?"

3. Risk tolerance: "How much disruption is acceptable?"
   - Options: "Small, safe changes" / "Moderate restructuring" / "Significant rewrite"

4. Decision gate: "Ready to create a refactoring roadmap?"
```

**Evidence from existing patterns:**
- `questioning.md` philosophy applies: "thinking partner, not interviewer" + "follow the thread"
- `discuss-phase.md` workflow shows how to conduct adaptive questioning in GSD: identify areas, let user select, deep-dive each area, capture decisions
- Key difference: brownfield questioning starts from OBSERVED state (analysis findings), while greenfield questioning starts from IMAGINED state (user's vision)

**Anti-pattern: Question checklist.** Do NOT walk through all questions regardless of answers. Each answer should inform the next question. If the user says "the auth system is completely broken," do not ask about performance targets -- dive into the auth problem.

### Pattern 3: Problem-Debug Session Bridging (ROUTE-03)

**What:** When the user selects "Fix" purpose and chooses specific concerns to address, the workflow can optionally bridge those findings into a `/gsd:debug` session with pre-filled symptoms. This eliminates the user having to re-describe problems that the analysis already identified.

**When to use:** Fix mode, after questioning identifies specific concerns to debug.

**Design:**

The bridging works by reading the relevant CONCERNS.md findings and translating them into the debug session's symptom format. The existing `gsd:debug` command already supports `symptoms_prefilled: true` mode (see `gsd-debugger.md` modes section).

**Bridging data transformation:**

```
CONCERNS.md finding:
  "N+1 query pattern — /api/courses endpoint runs separate query per course
  for lessons, 1.2s p95 with 50+ courses (app/api/courses/route.ts)
  (severity: critical)"

Translates to debug session symptoms:
  expected: "Course listing API should return all courses with lessons efficiently"
  actual: "N+1 query pattern — separate query per course, 1.2s p95 with 50+ courses"
  errors: "No error — performance degradation"
  reproduction: "Load /api/courses with 50+ courses in database"
  started: "Detected during codebase analysis — may have been present since implementation"
  files: ["app/api/courses/route.ts"]
```

**Integration with gsd:debug:**

The workflow generates a bridging context block and offers the user a choice:

```
AskUserQuestion:
  header: "Debug Bridge"
  question: "Start debug sessions for selected concerns?"
  options:
    - "Debug now" — Start /gsd:debug with pre-filled analysis findings
    - "Add to roadmap" — Include fixes in the roadmap (plan first, fix later)
    - "Both" — Create roadmap AND start debugging the most critical issue
```

If "Debug now":
```
The workflow generates the debug prompt and displays:

"Starting debug session for: [concern title]

Symptoms pre-filled from codebase analysis.
Type `/gsd:debug [concern-slug]` to begin.

Pre-filled context:
  Expected: [from analysis]
  Actual: [from analysis]
  Files: [from analysis]"
```

Alternatively, the workflow can write a `.planning/debug/[concern-slug].md` file directly in the debug file format (see `gsd-debugger.md` debug_file_protocol section), with status: `gathering` and symptoms pre-filled. The `/gsd:debug` command will then detect this active session and offer to continue it.

**Recommended approach:** Write the debug file directly. This is the cleanest integration:

1. Workflow creates `.planning/debug/[concern-slug].md` with pre-filled symptoms
2. Status set to `investigating` (skip gathering since symptoms are pre-filled)
3. User runs `/gsd:debug` which detects the active session
4. Debug agent resumes with symptoms already filled, jumps to investigation

This follows the established debug file protocol exactly. The file IS the bridge.

**Evidence:**
- `gsd-debugger.md` has `symptoms_prefilled: true` mode that skips symptom gathering
- `gsd:debug` Step 1 checks for active sessions: `ls .planning/debug/*.md`
- The debug file protocol is well-defined: frontmatter (status, trigger), Symptoms section, Evidence section
- This is NOT a new protocol -- it reuses the existing debug session format

### Pattern 4: Purpose-Aware Roadmap Generation (ROUTE-04)

**What:** After questioning, the workflow generates a roadmap that is ordered according to the user's purpose. Fix mode sorts by severity (critical first). Improve mode sorts by dependency (foundations first). Refactor mode sorts by impact/effort ratio.

**When to use:** After purpose questioning is complete.

**Design:**

The roadmap generation reuses the existing `gsd-roadmapper` agent but passes purpose-specific context that changes how it derives phases and orders them.

**Fix mode roadmap logic:**

```
Input: Selected concerns with severity tags + user priorities from questioning
Ordering: Severity (critical -> moderate -> minor), then user priority within each level
Phase derivation:
  - Phase 1: Critical fixes (concerns tagged critical)
  - Phase 2: Moderate fixes (concerns tagged moderate)
  - Phase 3: Minor fixes (concerns tagged minor, if user included them)
  - Each concern becomes a requirement (CONCERN-01, CONCERN-02, etc.)

Success criteria (per concern/phase):
  - "The [concern description] no longer occurs"
  - "[Affected file path] handles [scenario] correctly"
  - "Test confirms [expected behavior]"
```

**Improve mode roadmap logic:**

```
Input: Desired improvements from questioning + analysis architecture context
Ordering: Dependency order (foundations first, features that depend on them later)
Phase derivation:
  - Phase 1: Foundation changes needed to support improvements
  - Phase 2-N: Feature improvements, ordered by dependency graph
  - Each improvement becomes requirements (IMPROVE-01, IMPROVE-02, etc.)

The dependency ordering uses the architecture analysis:
  - If improvement touches core modules -> earlier phase
  - If improvement depends on another improvement -> later phase
  - If improvement is independent -> can be parallelized
```

**Refactor mode roadmap logic:**

```
Input: Pain points from questioning + target architecture from discussion
Ordering: Impact/effort ratio (high impact + low effort first)
Phase derivation:
  - Phase 1: Quick wins (high impact, low effort -- naming, conventions, small patterns)
  - Phase 2: Structural changes (moderate effort, high impact -- module reorganization)
  - Phase 3: Deep restructuring (high effort -- architecture changes)
  - Each refactor area becomes requirements (REFACTOR-01, REFACTOR-02, etc.)

Impact assessment (from analysis):
  - Number of files affected by the concern
  - Cross-document references (affects multiple dimensions)
  - Downstream dependency (blocks other improvements)

Effort assessment (heuristic):
  - Single file change -> low effort
  - Multiple files, same module -> moderate effort
  - Cross-module changes -> high effort
  - Architecture change -> very high effort
```

**Integration with gsd-roadmapper:**

The workflow passes purpose-aware context to the roadmapper agent:

```
Task(prompt="
<planning_context>

**Project:**
@.planning/PROJECT.md

**Codebase Analysis:**
@.planning/brownfield-analysis.md

**Purpose:** {fix | improve | refactor}

**Purpose Context:**
{Questioning output: selected concerns, priorities, constraints, target state}

**Ordering Rule:**
{fix: severity_desc | improve: dependency_asc | refactor: impact_effort_ratio_desc}

</planning_context>

<instructions>
Create a purpose-aware roadmap for a brownfield project:
1. Derive phases from {concerns | improvements | refactoring areas}
2. Order phases by {severity | dependency | impact/effort ratio}
3. Map each item to exactly one phase
4. Derive 2-5 success criteria per phase
5. Write ROADMAP.md, STATE.md, REQUIREMENTS.md
6. Return ROADMAP CREATED with summary
</instructions>
", subagent_type="gsd-roadmapper", description="Create purpose-aware roadmap")
```

The roadmapper agent receives this context and uses its existing methodology (phase identification, coverage validation, goal-backward criteria) but applies the purpose-specific ordering logic.

**New template: brownfield-roadmap.md**

A specialized template is needed because brownfield roadmaps differ from greenfield ones:

| Aspect | Greenfield Roadmap | Brownfield Roadmap |
|--------|-------------------|-------------------|
| Phase source | Requirements from user questioning | Concerns/improvements from analysis + user purpose |
| Ordering logic | Dependency-based (foundation first) | Purpose-dependent (severity, dependency, or impact/effort) |
| Requirement IDs | Category-based (AUTH-01, CONT-02) | Purpose-based (CONCERN-01, IMPROVE-01, REFACTOR-01) |
| Success criteria | "User can X" (new capability) | "X no longer occurs" (fix) or "User can now X" (improve) |
| Baseline | None (building from scratch) | Existing codebase (brownfield-analysis.md) |

The template defines these differences while reusing the ROADMAP.md section structure.

### Pattern 5: Workflow Extension Without Breaking Backward Compatibility

**What:** Phase 3 extends `brownfield-flow.md` by adding steps after the current `return_result` step. The extension is conditional: purpose routing only runs when the caller requests it.

**When to use:** When adding new capabilities to an existing workflow.

**Design:**

The `return_result` step (Step 5) is modified to check a parameter:

```markdown
<step name="return_result">
{Existing return logic -- UNCHANGED}

Check purpose_routing parameter:
  - If purpose_routing is true (or not explicitly false):
    Continue to select_purpose.
  - If purpose_routing is false (explicit opt-out):
    End workflow here. (Backward compatible with standalone analysis)
</step>
```

**Default behavior:** When `brownfield-flow.md` is invoked without explicit parameters (e.g., during manual testing or standalone use), it defaults to ending at `return_result` -- preserving Phase 2 behavior. When `new-project.md` invokes it in Phase 4, it passes `purpose_routing: true` to enable the full pipeline.

**Evidence:**
- STATE.md decision: "Analysis-only with explicit Phase 3 extension point" -- this is that extension point
- The workflow already says: "Ready for purpose routing (Phase 3)." in its return_result step

### Anti-Patterns to Avoid

- **Anti-Pattern: Creating a new agent for purpose questioning.** Purpose questioning is interactive (requires AskUserQuestion). Agents are for autonomous work. The workflow handles questioning inline, same as `discuss-phase.md` does.

- **Anti-Pattern: Hardcoding question lists.** Each question should adapt based on previous answers and analysis findings. A rigid question checklist ignores context.

- **Anti-Pattern: Re-reading codebase documents for purpose routing.** Purpose routing reads `brownfield-analysis.md` (the synthesis output). It does NOT re-read `.planning/codebase/*.md`. The synthesis was Phase 2's job.

- **Anti-Pattern: Making the debug bridge mandatory.** Not all fix-mode users want to debug immediately. Some want to plan first. Always offer both options.

- **Anti-Pattern: Purpose routing that ignores the analysis.** Every question and roadmap item should reference specific analysis findings. "What do you want to fix?" is bad. "The analysis found 2 critical and 4 moderate concerns -- which do you want to focus on?" is good.

- **Anti-Pattern: Overwriting brownfield-flow.md Phase 2 content.** Phase 3 EXTENDS by appending new steps. The existing steps 1-5 and their success criteria are preserved verbatim. Only `return_result` gets a small modification (conditional continuation).

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Interactive questioning | New questioning system | Adapt existing `questioning.md` philosophy + `discuss-phase.md` pattern | Both are proven patterns for adaptive questioning in GSD |
| Debug session creation | New debug protocol | Existing `gsd-debugger.md` debug file protocol | Write `.planning/debug/*.md` in the established format; debug command picks it up |
| Roadmap generation | New roadmap generator | Existing `gsd-roadmapper` agent with purpose-aware context | Agent already handles phase derivation, coverage validation, goal-backward criteria |
| Purpose selection UI | Custom selection mechanism | `AskUserQuestion` tool (same as used throughout GSD) | Consistent with every other GSD interactive step |
| Concern data structure | New concern format | Existing `brownfield-summary.md` template output format | Top Concerns and Detailed Concerns sections already have severity tags and file paths |

**Key insight:** Phase 3 is primarily an ORCHESTRATION challenge, not a creation challenge. All the building blocks exist (analysis data, questioning patterns, debug infrastructure, roadmap generator). Phase 3 wires them together with purpose-aware logic.

## Common Pitfalls

### Pitfall 1: Purpose Selection That Ignores Analysis Context

**What goes wrong:** The purpose selection presents generic options without connecting to the analysis findings. User sees "Fix / Improve / Refactor" but does not know which option fits their situation.

**Why it happens:** Treating purpose selection as a simple menu instead of a contextual recommendation.

**How to avoid:** The purpose selection step MUST reference the analysis dashboard. When health is "Concerning" with 2+ critical concerns, suggest "Fix" with a specific reason: "Your codebase has 2 critical issues (auth bypass, N+1 queries). Addressing these first is recommended." When health is "Good," suggest "Improve" or "Refactor."

**Warning signs:** User asks "which should I pick?" after seeing the options.

### Pitfall 2: Questioning That Becomes a Checklist

**What goes wrong:** The workflow walks through every question in the fix/improve/refactor thread regardless of what the user says. User gets asked about "performance targets" even though they just said the auth system is broken.

**Why it happens:** Implementing the questioning thread as a sequential checklist instead of adaptive conversation.

**How to avoid:** Follow `questioning.md` philosophy: "follow the thread." Each answer should inform the next question. If user selects a critical auth concern, dive into auth-specific questions. Do not pivot to unrelated areas. The question list in `brownfield-questioning.md` should be structured as a REFERENCE (available questions by category), not a SCRIPT (mandatory sequence).

**Warning signs:** User skips questions or gives one-word answers because the questions are irrelevant to their stated focus.

### Pitfall 3: Debug Bridge That Creates Orphaned Sessions

**What goes wrong:** The workflow creates `.planning/debug/*.md` files for multiple concerns, but the user only pursues one. Remaining files sit as phantom "active sessions" that clutter future `/gsd:debug` invocations.

**Why it happens:** Eagerly creating debug files for all selected concerns instead of one at a time.

**How to avoid:** Create at most ONE debug file at a time -- the most critical concern (or user's top choice). After that session resolves, the user can run the bridging step again for the next concern. Alternative: create all files but with status `pending` (not `investigating`), and only mark the first one as `investigating`. The debug command would show pending sessions as available, not active.

**Warning signs:** `ls .planning/debug/*.md` shows 5+ files, user gets confused about which session to resume.

**Recommendation:** Create ONE debug file for the user's top-priority concern. Include the remaining concerns as a "queue" in the roadmap. This keeps the debug space clean.

### Pitfall 4: Roadmap That Doesn't Connect to Analysis

**What goes wrong:** The purpose-aware roadmap generates phases but they are generic ("Phase 1: Fix critical issues") instead of specific ("Phase 1: Fix auth bypass in admin pages + N+1 query in course listing").

**Why it happens:** The roadmapper receives purpose context but not the specific findings from the analysis.

**How to avoid:** Pass the FULL analysis context (or at least the Tier 1 executive summary + Detailed Concerns section) to the roadmapper. Each roadmap phase should reference specific concerns/improvements by name and include file paths from the analysis.

**Warning signs:** Roadmap phases do not mention specific file paths or concern names from the analysis.

### Pitfall 5: Refactor Mode Without Clear Target State

**What goes wrong:** Refactor questioning captures pain points but not the desired end state. The roadmap becomes "fix tech debt" without a coherent architectural vision.

**Why it happens:** It is easier to identify problems than to articulate solutions. Questioning stops at "what hurts" without asking "what should it look like."

**How to avoid:** Refactor mode questioning MUST include target state questions: "What should the architecture look like after refactoring?" and "What patterns do you want to adopt?" Without a target state, the roadmap cannot define success criteria.

**Warning signs:** Refactor roadmap success criteria are all negative ("X is no longer duplicated") instead of positive ("Y uses a shared service pattern").

## Code Examples

These are Markdown workflow/reference definition patterns.

### Workflow Step: Purpose Selection (Step 6)

```markdown
<step name="select_purpose">
Read the analysis dashboard from present_dashboard (health rating, top concerns).

Determine suggestion based on analysis:
  - If health is "Concerning" AND analysis has >= 2 critical concerns:
    Suggest "Fix" with reason
  - If health is "Moderate":
    Suggest "Improve" with reason
  - If health is "Good":
    Suggest "Improve" or "Refactor" with reason

Use AskUserQuestion:
  header: "Purpose"
  question: "{Suggestion context}. What do you want to do with this codebase?"
  options:
    - "Fix issues" — Address bugs, security issues, broken functionality
    - "Add/improve features" — Enhance existing capabilities, add new ones
    - "Refactor/restructure" — Improve code quality, architecture, patterns
    - "Something else" — I'll explain my goal

If "Something else": Ask freeform, then map their response to the closest mode
(fix/improve/refactor) or proceed with custom questioning.

Store selected purpose. Continue to purpose_questioning.
</step>
```

### Workflow Step: Purpose-Specific Questioning (Step 7)

```markdown
<step name="purpose_questioning">
Load questioning reference: get-shit-done/references/brownfield-questioning.md

Branch based on selected purpose:

**If purpose == "fix":**
  1. Present top concerns from analysis as selectable options
     Use AskUserQuestion (multiSelect: true):
       header: "Focus"
       question: "Which concerns do you want to address?"
       options: [top 3-5 concerns from analysis with severity tags]

  2. For each selected concern, ask 2-3 follow-up questions:
     - Observed in practice? (yes/no + details)
     - Impact severity (from user's perspective, may differ from analysis)
     - Priority (immediate / soon / when convenient)

  3. Decision gate: Ready to create fix roadmap?

**If purpose == "improve":**
  1. Ask: "What do you want this codebase to do that it doesn't do now?"
     (Freeform, then follow-up like greenfield questioning)

  2. Present analysis architecture context:
     "Your codebase uses [architecture from analysis]. How does your
     improvement fit within this?"

  3. Ask about constraints from analysis:
     - Test coverage expectations
     - Affected areas and concerns intersection
     - Performance targets

  4. Decision gate: Ready to create improvement roadmap?

**If purpose == "refactor":**
  1. Present moderate/minor concerns + structural findings as pain point options
     Use AskUserQuestion (multiSelect: true):
       header: "Pain Points"
       question: "Which areas cause the most pain?"
       options: [concerns + structural issues from analysis]

  2. Target state questions:
     - Architecture: Keep current or move toward [alternative]?
     - Conventions: Standardize on what?
     - Testing: Coverage target?

  3. Risk tolerance: Small/safe vs moderate vs significant changes

  4. Decision gate: Ready to create refactoring roadmap?

Store questioning output as purpose_context. Continue to bridge_to_debug or
generate_roadmap.
</step>
```

### Workflow Step: Debug Bridge (Step 8)

```markdown
<step name="bridge_to_debug">
**Conditional:** Only if purpose is "fix" AND user selected specific concerns.

If purpose is NOT "fix": Skip to generate_roadmap.

If no specific concerns selected: Skip to generate_roadmap.

For the user's highest-priority selected concern:

Use AskUserQuestion:
  header: "Debug"
  question: "Start debugging [concern title] now, or plan first?"
  options:
    - "Debug now" — Start with pre-filled analysis findings
    - "Plan first" — Create roadmap, debug later
    - "Both" — Create roadmap AND start debugging top issue

If "Debug now" or "Both":
  1. Create .planning/debug/ directory (mkdir -p)
  2. Generate debug file:

     Write .planning/debug/{concern-slug}.md:
     ```
     ---
     status: investigating
     trigger: "[Concern title from analysis]"
     created: [timestamp]
     updated: [timestamp]
     ---

     ## Current Focus

     hypothesis: [Inferred from analysis finding]
     test: [Suggested first test based on file paths from analysis]
     expecting: [Expected behavior from analysis]
     next_action: Verify concern in code at [file path from analysis]

     ## Symptoms

     expected: [Inferred expected behavior]
     actual: [Concern description from analysis]
     errors: [Error details if available from analysis, else "See analysis"]
     reproduction: [Inferred from file paths and concern description]
     started: Detected during codebase analysis [date]

     ## Eliminated

     (none yet)

     ## Evidence

     - timestamp: [analysis date]
       checked: Codebase analysis (brownfield-analysis.md)
       found: [Full concern description with severity]
       implication: [Impact assessment from analysis]

     ## Resolution

     root_cause:
     fix:
     verification:
     files_changed: []
     ```

  3. Present to user:
     "Debug session created: .planning/debug/{concern-slug}.md

     Run `/gsd:debug` to continue. Symptoms pre-filled from analysis."

If "Plan first": Continue to generate_roadmap only.
If "Both": Continue to generate_roadmap after creating debug file.
</step>
```

### Reference File: brownfield-questioning.md Structure

```markdown
# Brownfield Questioning Guide

Purpose-specific questioning patterns for brownfield codebase workflows.

<philosophy>
You are a diagnostic partner, not an interviewer.

The analysis already identified what IS. Your job is to help the user articulate
what they want to DO about it. Start from observed state, navigate toward action.

Key difference from greenfield questioning:
- Greenfield: "What do you want to build?" (imagined state)
- Brownfield: "What do you want to change?" (observed state -> desired state)

The analysis is your anchor. Every question should reference specific findings.
</philosophy>

<fix_thread>
## Fix Mode

Start from concerns. Help user prioritize and provide reproduction context.

Context anchor: Top Concerns from brownfield-analysis.md
Goal: Narrow scope to specific, actionable fixes

Questions flow:
1. Selection — Which concerns to address?
2. Validation — Have you observed this? Can you reproduce?
3. Prioritization — What order? What's most urgent?
4. Scope — Fix root cause or patch symptom?
</fix_thread>

<improve_thread>
## Improve Mode

Start from user's vision. Constrain by analysis findings.

Context anchor: Architecture + Stack from brownfield-analysis.md
Goal: Define improvements that fit existing architecture

Questions flow:
1. Vision — What new capability do you want?
2. Fit — How does it relate to existing architecture?
3. Constraints — What does the analysis say about affected areas?
4. Scope — Minimum viable improvement?
</improve_thread>

<refactor_thread>
## Refactor Mode

Start from pain points. Navigate toward target architecture.

Context anchor: Concerns + Conventions from brownfield-analysis.md
Goal: Define target state and safe transformation path

Questions flow:
1. Pain — What hurts most? (confirm or extend analysis findings)
2. Target — What should it look like?
3. Risk — How much change is acceptable?
4. Strategy — Incremental or big-bang?
</refactor_thread>
```

### Template: brownfield-roadmap.md Structure

```markdown
# Brownfield Roadmap Template

Template for purpose-aware roadmap generation from brownfield analysis.

Purpose: Guide gsd-roadmapper agent to create roadmaps that are ordered by the
user's purpose (fix: severity, improve: dependency, refactor: impact/effort).

## File Template

# Roadmap: [Project Name] — [Purpose] Mode

**Purpose:** [Fix Issues | Add/Improve Features | Refactor/Restructure]
**Analysis Health:** [from brownfield-analysis.md]
**Ordering:** [Severity (critical first) | Dependency (foundations first) | Impact/Effort (quick wins first)]

## Phases

### Phase 1: [Name]
**Goal:** [Outcome, not task]
**Items:** [CONCERN-01, CONCERN-02 | IMPROVE-01 | REFACTOR-01]
**Ordering rationale:** [Why this is first — highest severity / foundational dependency / best ratio]
**Files affected:** [from analysis]

**Success Criteria:**
1. [Observable behavior that confirms the phase goal is met]
2. [Observable behavior]

### Phase 2: [Name]
...

## Coverage

| Item | Phase | Severity/Priority | Status |
|------|-------|--------------------|--------|
| [Item from analysis or questioning] | 1 | critical | Pending |
| ... | | | |
```

## Open Questions

### 1. Should "Other" Purpose Merge into Greenfield Questioning?

**What we know:** When a user selects "Something else" as purpose, they have a goal that does not fit fix/improve/refactor. This might be "I want to understand this codebase better" or "I need to add documentation."

**What's unclear:** Should "Other" route to greenfield-style questioning (open-ended "What do you want to build?"), or should it have its own minimal thread?

**Recommendation:** Route "Other" to a minimal thread that asks: (1) "What's your goal?", (2) "How does the existing codebase relate to this goal?", (3) "What from the analysis is relevant?" This keeps the user in brownfield context rather than switching to greenfield mode. Store the responses and pass to roadmapper as custom context.

### 2. How Many Concerns Should Be Selectable for Fix Mode?

**What we know:** The analysis produces 3-5 top concerns. Fix mode lets the user select which to address.

**What's unclear:** Should the user be able to select ALL concerns? If they select 5 concerns with 3 severities, the roadmap could become large.

**Recommendation:** Allow selecting 1-5 concerns (no limit). The roadmap generator handles grouping -- if 5 concerns are selected, they might result in only 2-3 phases (grouped by severity). The user can always defer lower-priority fixes to v2. Present all concerns but visually distinguish severity (critical items listed first, with clear severity tags).

### 3. Should the Roadmap Template Be Separate or Embedded in brownfield-flow.md?

**What we know:** Greenfield roadmaps use `gsd-roadmapper` which reads from `templates/roadmap.md`. Brownfield roadmaps need different ordering and item sourcing.

**What's unclear:** Whether to create a separate `brownfield-roadmap.md` template or embed the purpose-aware logic directly in the workflow prompt to the roadmapper.

**Recommendation:** Create a separate `brownfield-roadmap.md` template. The template provides structure that the roadmapper agent fills. Embedding logic in the workflow prompt makes the prompt too complex and harder to iterate. The template also enables Phase 4 integration: when `new-project.md` chooses which template to pass to the roadmapper, it selects based on mode (greenfield -> roadmap.md, brownfield -> brownfield-roadmap.md).

### 4. Integration Sequence with Phase 4

**What we know:** Phase 4 modifies `new-project.md` to integrate the brownfield pipeline. Phase 3 extends `brownfield-flow.md`.

**What's unclear:** After purpose routing completes and the roadmap is generated, does the flow return to `new-project.md` for standard continuation (config, research, etc.), or does brownfield-flow handle everything through to completion?

**Recommendation:** After roadmap generation, `brownfield-flow.md` returns a structured result to its caller (like it does now in Step 5). The result includes: purpose, roadmap path, analysis path, and state. The caller (`new-project.md` in Phase 4) then handles the remaining standard steps (config, STATE.md updates). This keeps the workflow focused on brownfield-specific logic and reuses the existing new-project.md pipeline for shared steps. The exact handoff is a Phase 4 design decision, but Phase 3 should ensure the return value contains everything the caller needs.

### 5. How Does Purpose Context Flow to Downstream Planner?

**What we know:** The `gsd-planner` agent reads ROADMAP.md, STATE.md, CONTEXT.md, and RESEARCH.md when planning a phase. Brownfield projects will have `brownfield-analysis.md` as an additional context source.

**What's unclear:** Should purpose context be stored in STATE.md (as a decision), in CONTEXT.md (as discussion output), or in a new file?

**Recommendation:** Store purpose in STATE.md under Decisions: `| Phase 3 | Purpose: Fix — 2 critical, 1 moderate concern | Analysis showed critical auth bypass and N+1 query |`. The planner already reads STATE.md decisions. The specific concern details are in ROADMAP.md (which the planner also reads). No new file needed. Additionally, write the purpose-questioning output to `{phase}-CONTEXT.md` so the planner can read detailed questioning context (same pattern as discuss-phase output).

## Sources

### Primary (HIGH confidence)

- `get-shit-done/workflows/brownfield-flow.md` — The Phase 2 workflow to extend. Steps 1-5 analysis pipeline, return_result as extension point. Lines 1-158.
- `agents/gsd-brownfield-analyzer.md` — Agent that produces the analysis document read by purpose routing. Severity classification, Top Concerns, Detailed Concerns structure. Lines 1-279.
- `get-shit-done/templates/brownfield-summary.md` — Template defining the data structure purpose routing reads. Executive Summary + Top Concerns + Detailed Concerns with severity tags. Lines 1-325.
- `commands/gsd/debug.md` — Debug command showing symptom gathering, active session detection, continuation spawning. Key integration point for ROUTE-03 bridging. Lines 1-155.
- `agents/gsd-debugger.md` — Debugger agent defining debug file protocol, symptom format, modes including `symptoms_prefilled: true`. Lines 1-1205.
- `get-shit-done/references/questioning.md` — Greenfield questioning philosophy to adapt for brownfield. "Thinking partner" approach, question types, anti-patterns. Lines 1-142.
- `get-shit-done/workflows/discuss-phase.md` — Adaptive questioning workflow pattern: gray area identification, multiSelect for user choice, deep-dive per area, CONTEXT.md output. Lines 1-432.
- `commands/gsd/discuss-phase.md` — Command definition for discuss-phase showing gray area analysis and scope guardrail. Lines 1-87.
- `agents/gsd-roadmapper.md` — Roadmap generation agent: phase derivation from requirements, coverage validation, goal-backward success criteria. Will receive purpose-aware context. Lines 1-607.
- `agents/gsd-planner.md` — Downstream consumer of roadmap output. Reads CONTEXT.md, RESEARCH.md, STATE.md decisions. Understanding its needs informs what Phase 3 must output. Lines 1-1393.
- `commands/gsd/new-project.md` — The command that will integrate brownfield flow in Phase 4. Understanding Phase 2 (Brownfield Offer) and Phase 8 (Create Roadmap) informs the handoff design. Lines 1-991.
- `.planning/ROADMAP.md` — Phase 3 requirements and success criteria. Lines 1-148.
- `.planning/REQUIREMENTS.md` — ROUTE-01 through ROUTE-04 requirement definitions. Lines 1-105.
- `.planning/STATE.md` — Current project state, Phase 2 decisions including "Analysis-only with explicit Phase 3 extension point." Lines 1-88.
- `.planning/phases/02-analysis-pipeline/02-RESEARCH.md` — Phase 2 research establishing the patterns Phase 3 extends. Open Question 2 decision: "Phase 3 EXTENDS the same file." Lines 1-453.

### Secondary (MEDIUM confidence)

- `get-shit-done/references/brownfield-detection.md` — Detection logic reference. Not directly consumed by Phase 3, but informs understanding of how brownfield mode is determined upstream. Lines 1-541.

### Tertiary (LOW confidence)

- None. All findings are grounded in direct codebase analysis.

## Metadata

**Confidence breakdown:**
- Purpose selection UX: HIGH — directly follows existing AskUserQuestion patterns (discuss-phase, new-project), with analysis-informed suggestion logic
- Purpose-specific questioning: HIGH — adapts proven greenfield questioning philosophy (questioning.md) and adaptive questioning pattern (discuss-phase.md) for brownfield context
- Debug bridging: HIGH — reuses existing debug file protocol exactly (gsd-debugger.md debug_file_protocol section); writes standard format file that debug command detects
- Roadmap generation: HIGH — delegates to existing gsd-roadmapper with purpose-aware context; only the ordering logic is new
- File placement decisions: HIGH — follows established GSD conventions (references/ for question guides, templates/ for output structures, workflows/ for orchestration)
- Phase 4 handoff design: MEDIUM — exact integration point is a Phase 4 decision; Phase 3 ensures return value contains sufficient context

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (stable — no external dependency changes; only internal GSD convention evolution)
