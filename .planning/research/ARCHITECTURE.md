# Architecture Research: Intelligent Mode Branching for Brownfield Analysis

**Domain:** CLI workflow tool with intelligent mode branching
**Researched:** 2026-02-08
**Confidence:** HIGH (based on direct analysis of existing GSD-Opus46 codebase architecture)

## Standard Architecture

### System Overview — Current vs. Proposed

```
CURRENT FLOW (new-project.md Phase 1-2):

[User runs /gsd:new-project]
    │
    ├─ Detect code files? ──YES──→ "Map codebase first?" ──YES──→ /gsd:map-codebase ──→ EXIT
    │                                                       └─NO──→ Phase 3: Questioning
    └─ NO code ──→ Phase 3: Questioning (greenfield)
                       │
                       └──→ (same flow for both paths)


PROPOSED FLOW (mode branching at Phase 2):

[User runs /gsd:new-project]
    │
    ├─ Phase 1: Setup (unchanged)
    │
    ├─ Phase 2: Mode Detection ──→ CODE FOUND + NO MAP?
    │       │                            │
    │       │                      ┌─────┴─────┐
    │       │                      │            │
    │       │                 MAP EXISTS    NO MAP
    │       │                      │            │
    │       │                      │    Auto-run map-codebase
    │       │                      │            │
    │       │                      └─────┬──────┘
    │       │                            │
    │       │                   Phase 2B: Brownfield Analysis
    │       │                            │
    │       │                   ┌────────┼────────┐
    │       │                   │        │        │
    │       │              Summarize  Ask Purpose  Branch
    │       │              Findings   (fix/enhance) to Mode
    │       │                   │        │        │
    │       │                   └────────┼────────┘
    │       │                            │
    │       │                   Phase 3B: Purpose-Aware Questioning
    │       │                            │
    │       │                   Phase 4B: Write PROJECT.md (brownfield-aware)
    │       │                            │
    │       └─ NO CODE ──→ Phase 3: Greenfield Questioning (unchanged)
    │                            │
    │                       Phase 4: Write PROJECT.md (greenfield)
    │
    ├─ Phase 5+: Shared path (config → research → requirements → roadmap)
    │
    └─ DONE
```

### Component Responsibilities

| Component | Responsibility | Location | New/Modified |
|-----------|----------------|----------|-------------|
| **new-project.md** (command) | Entry point, mode detection, orchestration | `commands/gsd/new-project.md` | MODIFIED |
| **brownfield-analyzer** (agent) | Synthesizes codebase map into user-facing summary, identifies purpose candidates | `agents/gsd-brownfield-analyzer.md` | NEW |
| **brownfield-flow.md** (workflow) | Analysis → summary → purpose → questioning pipeline for brownfield | `get-shit-done/workflows/brownfield-flow.md` | NEW |
| **gsd-codebase-mapper** (agent) | Explores codebase for 4 focus areas (unchanged) | `agents/gsd-codebase-mapper.md` | UNCHANGED |
| **map-codebase.md** (workflow) | Orchestrates parallel mapper agents (unchanged) | `get-shit-done/workflows/map-codebase.md` | UNCHANGED |
| **project.md** (template) | PROJECT.md template with brownfield sections | `get-shit-done/templates/project.md` | MINOR UPDATE |
| **brownfield-summary.md** (template) | Template for codebase analysis summary presented to user | `get-shit-done/templates/brownfield-summary.md` | NEW |

## Recommended Architecture: Where Mode Branching Lives

### Decision: Branch at Command Level, Not Workflow Level

The mode branching decision point belongs in `new-project.md` (the command), not in a workflow. Here is why:

1. **Commands own user interaction.** The command's `allowed-tools` include `AskUserQuestion`. Presenting the brownfield summary and asking purpose is a user-facing decision that belongs in the command layer.

2. **Workflows own execution logic.** The brownfield analysis pipeline (synthesize map, present, branch) is execution logic that belongs in a workflow file that the command delegates to.

3. **Agents own isolated work.** The brownfield-analyzer agent does one focused job: read codebase map documents, produce a synthesis. No user interaction.

**The pattern:**

```
new-project.md (command)
    │
    ├─ Detects brownfield condition (Phase 1-2, already exists)
    │
    ├─ IF brownfield:
    │   ├─ Ensures map-codebase has run (auto-invoke if needed)
    │   ├─ Delegates to brownfield-flow.md (workflow)
    │   │   ├─ Spawns brownfield-analyzer (agent)
    │   │   │   └─ Reads .planning/codebase/*.md → writes analysis summary
    │   │   ├─ Presents summary to user (via command's AskUserQuestion)
    │   │   ├─ Asks purpose (fix bug / add feature / refactor / other)
    │   │   └─ Returns: { summary, purpose, user_answers }
    │   │
    │   ├─ Phase 3B: Purpose-aware questioning
    │   │   (different question threads based on purpose)
    │   │
    │   └─ Phase 4B: Write PROJECT.md with brownfield context
    │
    └─ IF greenfield:
        └─ Phase 3-4 unchanged
```

This matches how existing commands work. For example, `execute-phase.md` (command) delegates to `execute-phase.md` (workflow) which spawns `gsd-executor` (agent). Same three-layer pattern.

### Why NOT a Separate Command

The project constraint says: "Must fit within commands -> workflows -> agents pattern. Can add new agents/workflows but not change the pattern itself." And specifically: "/gsd:new-project one command with internal branching — no separate command."

A separate `/gsd:new-brownfield-project` would:
- Force users to know which mode they need before running a command
- Defeat the purpose of automatic detection
- Create maintenance burden (two entry points doing similar things)

Internal branching inside `new-project.md` is correct.

## Architectural Patterns

### Pattern 1: Analysis-Decision-Execution Pipeline

**What:** A three-stage pipeline where automated analysis informs a user decision, which then determines the execution path.

**When to use:** When the system can gather intelligence that should influence the user's choices, and those choices determine different downstream workflows.

**How it maps to brownfield:**

```
STAGE 1: ANALYSIS (automated, no user interaction)
┌─────────────────────────────────────────────────────┐
│  Input: .planning/codebase/{7 documents}            │
│                                                     │
│  brownfield-analyzer agent:                         │
│  - Read ARCHITECTURE.md → extract system patterns   │
│  - Read STACK.md → extract tech + versions          │
│  - Read CONCERNS.md → extract top issues            │
│  - Read TESTING.md → extract coverage state         │
│  - Read STRUCTURE.md → extract organization         │
│  - Read INTEGRATIONS.md → extract external deps     │
│  - Read CONVENTIONS.md → extract code patterns      │
│                                                     │
│  Output: .planning/brownfield-analysis.md           │
│  (structured synthesis for user presentation)       │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
STAGE 2: DECISION (user interaction required)
┌─────────────────────────────────────────────────────┐
│  Present: Codebase summary (from analysis)          │
│                                                     │
│  "Here's what I found in this codebase:             │
│   - [Architecture summary]                          │
│   - [Tech stack summary]                            │
│   - [Key concerns]                                  │
│   - [Test coverage state]"                          │
│                                                     │
│  Ask: "What's your goal with this codebase?"        │
│  Options:                                           │
│   - Fix bugs / resolve issues                       │
│   - Add new features / capabilities                 │
│   - Refactor / improve quality                      │
│   - Other (freeform)                                │
│                                                     │
│  Output: purpose = { type, user_description }       │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
STAGE 3: EXECUTION (purpose-aware pipeline)
┌─────────────────────────────────────────────────────┐
│  Route by purpose:                                  │
│                                                     │
│  FIX BUGS:                                          │
│  - Ask: which issues from CONCERNS.md?              │
│  - Ask: what symptoms are you seeing?               │
│  - Ask: what's the expected behavior?               │
│  → PROJECT.md with fix-oriented requirements        │
│                                                     │
│  ADD FEATURES:                                      │
│  - Ask: what capability do you want to add?         │
│  - Show: where it fits in current architecture      │
│  - Ask: any constraints from existing code?         │
│  → PROJECT.md with feature-oriented requirements    │
│                                                     │
│  REFACTOR:                                          │
│  - Show: top concerns from CONCERNS.md              │
│  - Ask: which areas to prioritize?                  │
│  - Ask: any risk boundaries?                        │
│  → PROJECT.md with refactor-oriented requirements   │
│                                                     │
│  Output: PROJECT.md with brownfield context          │
└─────────────────────────────────────────────────────┘
```

**Trade-offs:**
- Pro: User makes informed decisions based on actual codebase analysis
- Pro: Downstream agents (planner, executor) get purpose-specific context
- Con: Adds one agent spawn + one user interaction step vs. current flow
- Con: Analysis quality depends on codebase map quality

### Pattern 2: Conditional Workflow Delegation

**What:** A command conditionally delegates to different workflows based on detected state, while maintaining a shared downstream path.

**When to use:** When the same command needs fundamentally different early-stage behavior but converges to the same later stages.

**How GSD already uses this:**

```
execute-phase.md (command):
    ├─ --gaps-only flag? → filter to gap_closure plans only
    ├─ Agent Teams available? → use Agent Teams instead of Task()
    └─ Normal → standard wave execution

plan-phase.md (command):
    ├─ --gaps flag? → gap_closure_mode in planner
    ├─ CONTEXT.md exists? → honor locked decisions
    └─ Normal → standard planning
```

**How brownfield uses the same pattern:**

```
new-project.md (command):
    ├─ Code detected + no map? → auto-map → brownfield-flow.md → purpose-questioning
    ├─ Code detected + map exists? → brownfield-flow.md → purpose-questioning
    ├─ No code? → greenfield questioning (unchanged)
    └─ After questioning (both paths) → shared Phase 5+ (config → research → roadmap)
```

The key insight: Phases 5-10 of `new-project.md` are IDENTICAL for both modes. The divergence is only in Phases 2-4 (detection, analysis, questioning). After questioning, both paths produce PROJECT.md and converge.

### Pattern 3: Agent-Written Synthesis with Template

**What:** An agent reads multiple source documents, synthesizes findings, and writes a structured output using a template. The orchestrator never sees the raw data — only the synthesis.

**Existing example:** `gsd-codebase-mapper` reads codebase files and writes to `.planning/codebase/`. The `map-codebase` workflow orchestrator never receives document contents — only confirmations.

**For brownfield-analyzer:**

```
brownfield-analyzer reads:
  .planning/codebase/ARCHITECTURE.md
  .planning/codebase/STACK.md
  .planning/codebase/CONCERNS.md
  .planning/codebase/TESTING.md
  .planning/codebase/STRUCTURE.md
  .planning/codebase/INTEGRATIONS.md
  .planning/codebase/CONVENTIONS.md

brownfield-analyzer writes:
  .planning/brownfield-analysis.md
  (using template: get-shit-done/templates/brownfield-summary.md)

brownfield-analyzer returns:
  ## ANALYSIS COMPLETE
  **Health:** [good/moderate/concerning]
  **Top concerns:** [3 items]
  **Architecture:** [one-liner]
  **Suggested purposes:** [fix/enhance/refactor based on findings]
```

This keeps the orchestrator context lean. The command reads `brownfield-analysis.md` to present to the user, not the raw 7 documents.

## Data Flow

### Complete Data Flow: Brownfield Path

```
[User: /gsd:new-project]
         │
         ▼
Phase 1: Setup (detect code files, package manifests)
         │
    CODE FOUND
         │
         ▼
Phase 2A: Auto-map (if .planning/codebase/ missing)
         │
    [map-codebase workflow]
    [4 parallel codebase-mapper agents]
         │
         ▼
    .planning/codebase/
    ├── STACK.md
    ├── ARCHITECTURE.md
    ├── STRUCTURE.md
    ├── CONVENTIONS.md
    ├── TESTING.md
    ├── INTEGRATIONS.md
    └── CONCERNS.md
         │
         ▼
Phase 2B: Analysis Synthesis
         │
    [brownfield-analyzer agent]
         │
         ▼
    .planning/brownfield-analysis.md
         │
         ▼
Phase 2C: Present & Ask Purpose
         │
    [AskUserQuestion: "What's your goal?"]
    [User selects: fix / add features / refactor / other]
         │
         ▼
Phase 3B: Purpose-Aware Questioning
         │
    [Different question threads per purpose]
    [Informed by brownfield-analysis.md]
         │
         ▼
Phase 4B: Write PROJECT.md (brownfield-enriched)
         │
    .planning/PROJECT.md
    (includes: codebase_mode, purpose, existing_capabilities)
         │
         ▼
Phase 5+: SHARED PATH (identical for greenfield/brownfield)
    ├── config.json
    ├── Research (milestone-aware, uses "subsequent" context)
    ├── REQUIREMENTS.md
    ├── ROADMAP.md
    └── STATE.md
```

### State Management: How Brownfield Differs from Greenfield in .planning/

**Greenfield PROJECT.md:**
```markdown
## Requirements
### Validated
(None yet — ship to validate)
### Active
- [ ] [Requirement 1]
```

**Brownfield PROJECT.md:**
```markdown
## Codebase Mode
**Type:** brownfield
**Purpose:** [fix-bugs | add-features | refactor]
**Analysis:** .planning/brownfield-analysis.md
**Codebase map:** .planning/codebase/

## Requirements
### Validated
- check [Existing capability 1] — existing (inferred from ARCHITECTURE.md)
- check [Existing capability 2] — existing (inferred from STACK.md)
### Active
- [ ] [New requirement based on purpose]
```

**Greenfield STATE.md:**
```markdown
## Project Reference
**Core value:** [from questioning]
**Current focus:** Phase 1
```

**Brownfield STATE.md:**
```markdown
## Project Reference
**Core value:** [from purpose-aware questioning]
**Current focus:** Phase 1
**Codebase context:** .planning/codebase/ (mapped [date])
**Purpose:** [fix-bugs | add-features | refactor]
```

The key difference: Brownfield state includes references to the codebase map and analysis. This ensures downstream agents (planner, executor) know to consult codebase documents when creating plans.

### Data Flow: How Brownfield Context Reaches Downstream Agents

```
brownfield-analysis.md ──→ PROJECT.md (Codebase Mode section)
                                │
                                ▼
                    plan-phase reads PROJECT.md
                                │
                    ┌───────────┼───────────┐
                    │           │           │
              gsd-planner   gsd-phase-     gsd-executor
              reads:        researcher     reads:
              - PROJECT.md  reads:         - PLAN.md
              - codebase/   - PROJECT.md   - codebase/
                ARCH.md     - codebase/      CONVENTIONS.md
                STACK.md      relevant     - codebase/
                              docs           STRUCTURE.md
```

This already works. The `gsd-planner` agent's `load_codebase_context` step (line 1026-1044 of gsd-planner.md) already loads relevant codebase documents based on phase keywords. The brownfield flow just ensures these documents exist before planning begins.

## New Components Needed

### 1. NEW AGENT: gsd-brownfield-analyzer

**Purpose:** Synthesize 7 codebase map documents into a user-facing analysis summary.

**Why a separate agent (not inline in command):**
- The 7 codebase documents total 200-1000+ lines. Reading them all in the command's context would consume significant tokens.
- The agent has isolated context, reads all 7 documents, produces a focused synthesis.
- Matches the existing pattern: mappers write documents, agents synthesize.

**Inputs:**
- `.planning/codebase/*.md` (7 documents)

**Outputs:**
- `.planning/brownfield-analysis.md` (structured synthesis)
- Return: structured summary for command to present

**Tools needed:** Read, Write, Glob, Grep

**Template needed:** `get-shit-done/templates/brownfield-summary.md`

### 2. NEW WORKFLOW: brownfield-flow.md

**Purpose:** Orchestrate the analysis-decision-execution pipeline for brownfield projects.

**Why a workflow (not inline in command):**
- Keeps the command lean. `new-project.md` is already ~950 lines.
- Separates brownfield-specific logic from shared logic.
- Follows the pattern: `execute-phase.md` command delegates to `execute-phase.md` workflow.

**Steps:**
1. Check if codebase map exists; if not, invoke map-codebase
2. Spawn brownfield-analyzer agent
3. Present analysis summary to user
4. Ask purpose (fix / add features / refactor / other)
5. Conduct purpose-aware questioning
6. Return structured context for PROJECT.md creation

**Important:** This workflow does NOT write PROJECT.md. It returns findings to the command, which writes PROJECT.md (maintaining the command's responsibility for artifact creation).

### 3. NEW TEMPLATE: brownfield-summary.md

**Purpose:** Structure for the brownfield analysis summary presented to user.

**Sections:**
- Codebase Health (good/moderate/concerning)
- Architecture Overview (pattern, layers, key abstractions)
- Tech Stack Summary (language, framework, key deps, versions)
- Top Concerns (from CONCERNS.md, prioritized)
- Test Coverage State (framework, coverage level, gaps)
- External Integrations (services, APIs)
- Suggested Focus Areas (based on analysis)

### 4. MODIFIED: new-project.md

**Changes:**
- Phase 2: Replace current "Map codebase first?" offer with automatic mode detection
- Phase 2B: Add delegation to brownfield-flow.md
- Phase 3B: Add purpose-aware questioning branch
- Phase 4B: Add brownfield-enriched PROJECT.md writing

**Phases 5-10: UNCHANGED.** The research, requirements, and roadmap creation path is identical. The only difference is that brownfield projects enter research with "subsequent milestone" context (which already exists in the research agent prompts).

### 5. MODIFIED: project.md (template)

**Changes:**
- Add optional `## Codebase Mode` section for brownfield projects
- Existing `<brownfield>` section already exists in the template (lines 147-167) — this just needs to be invoked by the brownfield flow

### Components NOT Needed (Reuse Existing)

| Component | Why Reusable |
|-----------|-------------|
| **gsd-codebase-mapper** | Already produces the 7 documents brownfield-analyzer needs |
| **map-codebase workflow** | Already orchestrates parallel mapping. Just invoke it. |
| **gsd-project-researcher** | Already has "subsequent milestone" mode that focuses on NEW features |
| **gsd-roadmapper** | Already creates roadmaps from requirements — brownfield or greenfield |
| **gsd-planner** | Already loads codebase context via `load_codebase_context` step |
| **gsd-executor** | Already follows codebase conventions via CONVENTIONS.md |
| **questioning.md reference** | Question techniques apply to both modes |

## Anti-Patterns

### Anti-Pattern 1: Mode Flag Instead of Auto-Detection

**What people do:** Add a `--brownfield` flag to the command, requiring users to declare the mode.

**Why it is wrong:** Users should not need to know the terminology. The system detects code — the system decides the mode. This is the core value proposition.

**Do this instead:** Auto-detect in Phase 1 (already implemented). Branch silently in Phase 2.

### Anti-Pattern 2: Separate Brownfield Command

**What people do:** Create `/gsd:new-brownfield-project` as a separate entry point.

**Why it is wrong:** Two commands that do similar things. Users must choose. Maintenance burden doubles. And it violates the project constraint.

**Do this instead:** Single command (`/gsd:new-project`) with internal branching. Users never see the branching logic — they just get the right flow.

### Anti-Pattern 3: Analyzing Inside the Command

**What people do:** Read all 7 codebase documents inside `new-project.md` and synthesize inline.

**Why it is wrong:** Commands should orchestrate, not do heavy lifting. Reading 7 documents (potentially 1000+ lines total) in the command's context wastes tokens and violates the pattern.

**Do this instead:** Spawn `brownfield-analyzer` agent (isolated context). Receive structured summary. Present to user.

### Anti-Pattern 4: Skipping the Summary Step

**What people do:** Go directly from codebase mapping to purpose question without showing the user what was found.

**Why it is wrong:** The user needs to see what the system understands about their codebase before deciding purpose. Without the summary, the purpose question is uninformed.

**Do this instead:** Always present the analysis summary. Let the user see the system's understanding. Then ask purpose.

## Build Order and Dependencies

### Phase 1: Foundation (No Dependencies)

Create the new template and agent definition files. These are leaf nodes with no dependencies on other changes.

| Artifact | Type | Dependencies |
|----------|------|-------------|
| `get-shit-done/templates/brownfield-summary.md` | Template | None |
| `agents/gsd-brownfield-analyzer.md` | Agent definition | Template above |

### Phase 2: Workflow (Depends on Phase 1)

Create the brownfield workflow that orchestrates the agent.

| Artifact | Type | Dependencies |
|----------|------|-------------|
| `get-shit-done/workflows/brownfield-flow.md` | Workflow | brownfield-analyzer agent, brownfield-summary template |

### Phase 3: Command Integration (Depends on Phase 2)

Modify `new-project.md` to detect mode and delegate to the brownfield workflow.

| Artifact | Type | Dependencies |
|----------|------|-------------|
| `commands/gsd/new-project.md` (modified) | Command | brownfield-flow workflow |
| `get-shit-done/templates/project.md` (minor update) | Template | None (can be done in Phase 1) |

### Phase 4: State Integration (Depends on Phase 3)

Ensure brownfield context propagates to STATE.md and is consumed by downstream agents.

| Artifact | Type | Dependencies |
|----------|------|-------------|
| `get-shit-done/templates/state.md` (minor update) | Template | PROJECT.md brownfield sections |

### Build Order Rationale

```
Phase 1: Templates + Agent def   (independent, can build first)
    │
    ▼
Phase 2: Workflow                 (needs agent to exist)
    │
    ▼
Phase 3: Command modification    (needs workflow to delegate to)
    │
    ▼
Phase 4: State propagation       (needs command to produce brownfield PROJECT.md)
```

Each phase can be tested independently:
- Phase 1: Agent can be tested by manually spawning it
- Phase 2: Workflow can be tested by manually invoking it
- Phase 3: Full integration test via `/gsd:new-project` on a brownfield codebase
- Phase 4: Verify downstream agents receive brownfield context

## Integration Points

### Internal Boundaries

| Boundary | Communication | Direction | Notes |
|----------|---------------|-----------|-------|
| new-project.md -> brownfield-flow.md | @reference in execution_context | Command -> Workflow | Workflow reads inline, command delegates |
| brownfield-flow.md -> brownfield-analyzer | Task() spawn | Workflow -> Agent | Agent writes file, returns confirmation |
| brownfield-analyzer -> .planning/brownfield-analysis.md | Write tool | Agent -> Filesystem | Persistent artifact, read by command |
| new-project.md -> PROJECT.md | Write tool | Command -> Filesystem | Enriched with brownfield context |
| PROJECT.md -> gsd-planner | @reference in context | Artifact -> Agent | Planner reads Codebase Mode section |
| PROJECT.md -> gsd-project-researcher | Prompt context | Artifact -> Agent | "subsequent milestone" mode triggered by Validated requirements |

### Trigger Conditions for Mode Branching

```
MODE DETECTION LOGIC (in new-project.md Phase 2):

has_code_files = (find code files returns non-empty)
has_package_manifest = (package.json OR requirements.txt OR Cargo.toml OR go.mod exists)
has_codebase_map = (.planning/codebase/ directory exists with documents)

IF (has_code_files OR has_package_manifest):
    mode = "brownfield"
    IF NOT has_codebase_map:
        auto_run_map_codebase()     # NEW: auto-invoke instead of asking
    run_brownfield_flow()
ELSE:
    mode = "greenfield"
    run_greenfield_questioning()    # unchanged
```

**Key change from current behavior:** Instead of ASKING "Would you like to map the codebase first?", the system AUTO-MAPS and then AUTO-ANALYZES. The first user interaction in brownfield mode is seeing the analysis summary and choosing purpose.

This removes one decision point from the user while adding more value (they see analysis instead of being asked whether to analyze).

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Current (1 project type) | Greenfield only, no branching needed |
| Target (2 modes: green/brown) | Mode detection + brownfield flow as described above |
| Future (N modes: green/brown/migration/audit) | Consider mode registry pattern — each mode registers detection logic + workflow |

### Future Extension Point

If more modes are added later, the Phase 2 detection logic in `new-project.md` could evolve from if/else to a mode resolver:

```
# Future pattern (not needed now):
modes = [
    { name: "greenfield", detect: no_code, workflow: "greenfield-flow.md" },
    { name: "brownfield", detect: has_code, workflow: "brownfield-flow.md" },
    { name: "migration", detect: has_migration_markers, workflow: "migration-flow.md" },
]
resolved_mode = first_match(modes)
delegate(resolved_mode.workflow)
```

This is noted for awareness but should NOT be built now. Two modes (green/brown) with simple if/else is correct for current scope.

## Sources

- Direct analysis of GSD-Opus46 codebase (HIGH confidence — primary source)
  - `commands/gsd/new-project.md` — current brownfield detection logic (lines 62-88)
  - `agents/gsd-codebase-mapper.md` — mapper agent pattern
  - `get-shit-done/workflows/map-codebase.md` — orchestrator pattern
  - `get-shit-done/workflows/execute-phase.md` — wave execution pattern (delegation model)
  - `get-shit-done/workflows/discuss-phase.md` — gray area analysis pattern
  - `get-shit-done/templates/project.md` — existing brownfield section (lines 147-167)
  - `agents/gsd-planner.md` — codebase context loading (lines 1026-1044)
  - `agents/gsd-roadmapper.md` — requirement-driven phase creation
  - `.planning/codebase/CODEMAP.md` — architecture overview

---
*Architecture research for: CLI workflow tool with intelligent mode branching*
*Researched: 2026-02-08*
