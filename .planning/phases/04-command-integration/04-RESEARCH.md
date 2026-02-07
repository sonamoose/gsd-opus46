# Phase 4: Command Integration - Research

**Researched:** 2026-02-08
**Domain:** Integration of brownfield branching logic into the main `new-project.md` command (Markdown command definition editing, flow control design, greenfield regression safety)
**Confidence:** HIGH

## Summary

Phase 4 modifies the single most important file in the GSD brownfield project: `commands/gsd/new-project.md` (991 lines, 10 phases). The goal is to integrate brownfield detection and workflow delegation so that when a user runs `/gsd:new-project` on a directory with existing code, the system automatically runs `map-codebase` + `brownfield-flow` (with purpose routing) instead of the greenfield questioning flow. When no code is detected, the existing greenfield flow must remain byte-identical.

The research analyzed all three input files line-by-line: `new-project.md` (the file to modify), `brownfield-detection.md` (the detection logic to embed), and `brownfield-flow.md` (the workflow to invoke). It also cross-referenced the `map-codebase.md` command, all Phase 1-3 research documents, the project ROADMAP.md, REQUIREMENTS.md, and STATE.md.

The key finding is that the integration is surgically precise: only 3 of the 10 phases in `new-project.md` need modification (Phase 1, Phase 2, and a new conditional branch between Phase 2 and Phase 3). Phases 3-10 of the greenfield path remain untouched. The brownfield path diverges at Phase 2 and rejoins at Phase 5 (Workflow Preferences / config.json), because `brownfield-flow.md` Step 9 already produces ROADMAP.md, STATE.md, and REQUIREMENTS.md -- replacing greenfield Phases 3, 4, 6, 7, and 8.

**Primary recommendation:** Replace Phase 1 Step 3 detection with the complete brownfield-detection.md script. Replace Phase 2 binary offer with MODE-based three-way routing (greenfield/scaffolded/brownfield). Add a new "Phase 2B: Brownfield Pipeline" that runs map-codebase + brownfield-flow + PROJECT.md writing, then jumps to Phase 5. Keep Phases 3-10 greenfield path completely unchanged.

## Standard Stack

This phase involves **no external libraries or code**. All work is editing one Markdown command definition file (`commands/gsd/new-project.md`). The "stack" is the GSD command/workflow/agent convention system.

### Core

| Component | Location | Purpose | How Phase 4 Uses It |
|-----------|----------|---------|---------------------|
| `new-project.md` | `commands/gsd/new-project.md` | Main entry point command (991 lines) | The file being modified -- detection upgrade + brownfield branch |
| `brownfield-detection.md` | `get-shit-done/references/brownfield-detection.md` | Multi-signal detection script (55 lines Bash) | Embedded in Phase 1 Step 3, replacing basic detection |
| `brownfield-flow.md` | `get-shit-done/workflows/brownfield-flow.md` | Analysis + purpose routing (9 steps) | Invoked via inline orchestration after map-codebase |
| `map-codebase.md` | `commands/gsd/map-codebase.md` | Parallel codebase mapper | Invoked before brownfield-flow (produces .planning/codebase/) |

### Supporting (Already Exist, Read-Only)

| Component | Location | How Phase 4 Uses It |
|-----------|----------|---------------------|
| `brownfield-questioning.md` | `get-shit-done/references/brownfield-questioning.md` | Referenced by brownfield-flow (not directly by new-project.md) |
| `brownfield-roadmap.md` | `get-shit-done/templates/brownfield-roadmap.md` | Used by roadmapper inside brownfield-flow (not directly by new-project.md) |
| `brownfield-summary.md` | `get-shit-done/templates/brownfield-summary.md` | Used by analyzer inside brownfield-flow (not directly by new-project.md) |
| `gsd-brownfield-analyzer.md` | `agents/gsd-brownfield-analyzer.md` | Spawned by brownfield-flow (not directly by new-project.md) |

### Alternatives Considered

| Recommended | Alternative | Why Not Alternative |
|-------------|-------------|---------------------|
| Inline brownfield-detection.md script in Phase 1 | Reference detection document at runtime | Commands can't dynamically include references at execution time. The detection script (55 lines) must be embedded directly in the command's Bash block. |
| Single-file modification (new-project.md only) | Split new-project.md into greenfield/brownfield commands | Out of scope per REQUIREMENTS.md: "별도 커맨드 분리 -- /gsd:new-project 하나에서 내부 분기로 처리" |
| Brownfield-flow inline orchestration | Spawn brownfield-flow as separate Task() agent | brownfield-flow uses AskUserQuestion (interactive). Task() agents cannot use AskUserQuestion. The workflow must execute inline within the new-project.md command context. |
| Rejoin at Phase 5 (config.json) | Rejoin at Phase 8 (roadmap) or Phase 10 (done) | brownfield-flow already produces ROADMAP.md, STATE.md, and REQUIREMENTS.md. Rejoining at Phase 5 lets brownfield projects still get config.json preferences (shared concern). Skipping past Phase 8 would miss the roadmap approval UX. |

## Architecture Patterns

### Pattern 1: Phase Flow Map (Greenfield vs Brownfield)

This is the critical architecture diagram. It shows exactly which phases are shared, divergent, and where convergence occurs.

```
new-project.md Phase Flow (AFTER Phase 4 modification):

Phase 1: Setup (MODIFIED)
  ├── Step 1: Abort if project exists          [SHARED - unchanged]
  ├── Step 2: Initialize git repo              [SHARED - unchanged]
  └── Step 3: Detect existing code             [MODIFIED - replace basic detection
                                                 with brownfield-detection.md script]
        ↓
        MODE = greenfield | scaffolded | brownfield
        ↓
Phase 2: Mode Routing (MODIFIED - was "Brownfield Offer")
  ├── IF MODE == "greenfield":
  │     → Continue to Phase 3 (no message shown)
  │
  ├── IF MODE == "scaffolded":
  │     → Show info message, continue to Phase 3
  │     ("Scaffolded project detected. Treating as greenfield.")
  │
  └── IF MODE == "brownfield":
        → Continue to Phase 2B (brownfield pipeline)

--- BROWNFIELD-ONLY PATH ---

Phase 2B: Brownfield Pipeline (NEW)
  ├── Step 1: Run map-codebase (if not already mapped)
  │     Execute map-codebase workflow inline
  │     Produces .planning/codebase/*.md (7 documents)
  │
  ├── Step 2: Run brownfield-flow (with purpose_routing: true)
  │     Execute brownfield-flow.md inline (Steps 1-9)
  │     Produces .planning/brownfield-analysis.md
  │     User selects purpose, answers questions
  │     Produces .planning/ROADMAP.md, STATE.md, REQUIREMENTS.md
  │
  ├── Step 3: Write PROJECT.md (brownfield version)
  │     Infer Validated requirements from .planning/codebase/
  │     Use existing Phase 4 brownfield PROJECT.md logic
  │     Commit PROJECT.md
  │
  └── Step 4: JUMP to Phase 5 (Workflow Preferences)
        Skip Phases 3, 4 (greenfield questioning + PROJECT.md)
        Skip Phases 6, 7, 8 (research, requirements, roadmap)
        These were handled by brownfield-flow

--- GREENFIELD-ONLY PATH (UNCHANGED) ---

Phase 3: Deep Questioning                      [GREENFIELD ONLY - unchanged]
Phase 4: Write PROJECT.md                      [GREENFIELD ONLY - unchanged]

--- SHARED PATH (BOTH) ---

Phase 5: Workflow Preferences (config.json)    [SHARED - unchanged]
Phase 5.5: Effort Level                        [SHARED - unchanged]
Phase 6: Research Decision                     [GREENFIELD ONLY - brownfield skips]
Phase 7: Define Requirements                   [GREENFIELD ONLY - brownfield skips]
Phase 8: Create Roadmap                        [GREENFIELD ONLY - brownfield skips]
Phase 10: Done                                 [SHARED - unchanged]
```

**Key insight:** The convergence point is Phase 5 (Workflow Preferences). After brownfield-flow completes, the brownfield path has already produced ROADMAP.md, STATE.md, and REQUIREMENTS.md. The only remaining shared concerns are config.json preferences (Phase 5) and the completion banner (Phase 10). The brownfield path must SKIP Phases 6, 7, 8 because those are greenfield-specific (research, requirements scoping, roadmap generation).

### Pattern 2: Detection Upgrade (Phase 1 Step 3)

**What:** Replace the current 3-line basic detection with the full brownfield-detection.md script.

**Current detection (new-project.md lines 61-65):**
```bash
CODE_FILES=$(find . -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.swift" -o -name "*.java" 2>/dev/null | grep -v node_modules | grep -v .git | head -20)
HAS_PACKAGE=$([ -f package.json ] || [ -f requirements.txt ] || [ -f Cargo.toml ] || [ -f go.mod ] || [ -f Package.swift ] && echo "yes")
HAS_CODEBASE_MAP=$([ -d .planning/codebase ] && echo "yes")
```

**Replacement detection (from brownfield-detection.md):**
The complete 55-line Bash script with:
- Signal 1: Code files (33 extensions across 6 families, 12 exclusion directories)
- Signal 2: Package manager (17 manifest files)
- Signal 3: Git history depth
- Signal 4: Directory structure complexity
- Signal 5: Codebase map existence
- Language detection function
- Mode determination tree (greenfield / scaffolded / brownfield)
- 7 diagnostic variables output

**What changes:**
- `CODE_FILES` and `HAS_PACKAGE` variables still exist but are more comprehensive
- NEW variables: `CODE_FILE_COUNT`, `PRIMARY_LANG`, `GIT_COMMIT_COUNT`, `SRC_DIR_COUNT`, `MODE`
- `HAS_CODEBASE_MAP` now outputs "yes"/"no" instead of "yes"/empty

**Compatibility consideration:** The rest of Phase 1 and Phase 2 reference `CODE_FILES`, `HAS_PACKAGE`, and `HAS_CODEBASE_MAP`. The new script preserves these variable names. Phase 2 needs updating to use `MODE` instead of checking raw variables.

### Pattern 3: Mode Routing (Phase 2 Replacement)

**What:** Replace the current Phase 2 binary "Brownfield Offer" with MODE-based three-way routing.

**Current Phase 2 behavior (lines 69-91):**
- IF code detected AND no codebase map: Ask user "Map codebase first?" or "Skip mapping"
- IF "Map codebase first": Tell user to run `/gsd:map-codebase`, exit command
- IF "Skip mapping" or no code: Continue to Phase 3

**New Phase 2 behavior:**
- IF `MODE == "greenfield"`: Continue to Phase 3 silently (no message)
- IF `MODE == "scaffolded"`: Show informational message, continue to Phase 3
- IF `MODE == "brownfield"`: Continue to Phase 2B (brownfield pipeline)
  - No more "exit command and come back" -- the pipeline runs inline

**Critical change:** The current Phase 2 exits the command and tells the user to run map-codebase separately. The new Phase 2 runs map-codebase inline within the same command session. This is better UX (single command does everything) but requires the map-codebase workflow logic to be invoked inline rather than as a separate command.

### Pattern 4: Brownfield Pipeline (Phase 2B -- New)

**What:** A new phase block that orchestrates the full brownfield pipeline: map-codebase, brownfield-flow, PROJECT.md writing, then jump to Phase 5.

**Step 1: map-codebase invocation:**
```
IF HAS_CODEBASE_MAP == "no":
  Display: "Mapping codebase..."
  Execute map-codebase workflow inline (spawn 4 parallel mapper agents)
  Wait for completion
  Verify .planning/codebase/*.md exists (7 documents)
ELSE:
  Display: "Codebase already mapped. Using existing analysis."
  Skip mapping
```

**Step 2: brownfield-flow invocation:**
```
Execute brownfield-flow.md workflow inline:
  - Steps 1-5: Analysis pipeline (check prerequisites, scope, analyze, present dashboard, return result)
  - Steps 6-9: Purpose routing (select purpose, questioning, debug bridge, generate roadmap)

NOTE: brownfield-flow uses AskUserQuestion which requires inline execution.
It CANNOT be spawned as a Task() agent because Task() agents cannot use AskUserQuestion.

The workflow needs these references loaded:
  @get-shit-done/workflows/brownfield-flow.md
  @get-shit-done/references/brownfield-questioning.md
  @get-shit-done/templates/brownfield-summary.md
  @get-shit-done/templates/brownfield-roadmap.md
  @agents/gsd-brownfield-analyzer.md
```

**Step 3: Write PROJECT.md (brownfield version):**
Uses the existing brownfield PROJECT.md logic from current Phase 4 (lines 177-202):
- Read .planning/codebase/ARCHITECTURE.md and STACK.md
- Infer Validated requirements from existing code
- Write PROJECT.md with Validated + Active requirements sections
- Commit PROJECT.md

**Step 4: Jump to Phase 5:**
After brownfield pipeline completes, skip directly to Phase 5 (Workflow Preferences).
The brownfield-flow already produced:
- `.planning/brownfield-analysis.md` (analysis summary)
- `.planning/ROADMAP.md` (purpose-aware roadmap)
- `.planning/STATE.md` (with purpose recorded)
- `.planning/REQUIREMENTS.md` (with item-to-phase mapping)

So greenfield Phases 3 (questioning), 4 (PROJECT.md is handled in Step 3 above), 6 (research), 7 (requirements), and 8 (roadmap) are ALL skipped.

### Pattern 5: Convergence at Phase 5 and Beyond

**What:** After the brownfield pipeline, the flow rejoins at Phase 5 (Workflow Preferences).

**Shared phases analysis:**

| Phase | Greenfield | Brownfield | Shared? | Notes |
|-------|-----------|------------|---------|-------|
| 1: Setup | Yes | Yes (modified detection) | Partially | Detection upgraded, git init unchanged |
| 2: Mode Routing | Yes | Yes (new routing) | Partially | Different routing logic but same decision point |
| 2B: Brownfield Pipeline | No | Yes | Brownfield only | New phase |
| 3: Deep Questioning | Yes | No | Greenfield only | Brownfield uses purpose_questioning in brownfield-flow |
| 4: Write PROJECT.md | Yes | No | Greenfield only | Brownfield writes PROJECT.md in Phase 2B Step 3 |
| 5: Workflow Preferences | Yes | Yes | YES | Both paths need config.json |
| 5.5: Effort Level | Yes | Yes | YES | Both paths need effort level info |
| 6: Research Decision | Yes | No | Greenfield only | Brownfield analysis replaces domain research |
| 7: Define Requirements | Yes | No | Greenfield only | Brownfield-flow produces requirements |
| 8: Create Roadmap | Yes | No | Greenfield only | Brownfield-flow produces roadmap |
| 10: Done | Yes | Yes | YES | Both paths show completion banner |

**Brownfield's Phase 10 adjustment:** The Done banner (lines 913-948) shows artifacts. Brownfield projects have different artifacts:
- `.planning/brownfield-analysis.md` instead of `.planning/research/`
- Purpose-aware ROADMAP.md instead of standard ROADMAP.md
- The banner text can be the same structure; the file list adapts dynamically.

### Pattern 6: execution_context References

**What:** The `new-project.md` file has an `<execution_context>` section (lines 30-37) that lists reference files loaded at command start. For the brownfield pipeline to work, additional references must be added.

**Current execution_context (lines 30-37):**
```
@~/.claude/get-shit-done/references/questioning.md
@~/.claude/get-shit-done/references/ui-brand.md
@~/.claude/get-shit-done/templates/project.md
@~/.claude/get-shit-done/templates/requirements.md
```

**Additional references needed for brownfield path:**
```
@~/.claude/get-shit-done/references/brownfield-detection.md
@~/.claude/get-shit-done/workflows/brownfield-flow.md
@~/.claude/get-shit-done/references/brownfield-questioning.md
@~/.claude/get-shit-done/templates/brownfield-summary.md
@~/.claude/get-shit-done/templates/brownfield-roadmap.md
@~/.claude/agents/gsd-brownfield-analyzer.md
@~/.claude/get-shit-done/workflows/map-codebase.md
```

**Token impact consideration:** Adding 7 references increases the initial context loading. However, these references are only needed when the brownfield path is taken. There are two approaches:

1. **Load all upfront** (simpler): Add all references to execution_context. Every invocation loads brownfield references even for greenfield. The brownfield references total ~1,800 lines which adds ~5-8K tokens.

2. **Conditional loading** (more efficient): Only reference the detection module upfront. If brownfield mode is detected, explicitly read the remaining brownfield references within Phase 2B. This saves tokens for greenfield invocations.

**Recommendation:** Use approach 2 (conditional loading). The detection reference (brownfield-detection.md) is already embedded as Bash, so no reference needed for it. Add only `brownfield-flow.md` and `map-codebase.md` workflow references conditionally within Phase 2B instructions. This follows the principle of not wasting tokens on unused context.

### Anti-Patterns to Avoid

- **Anti-Pattern: Modifying greenfield phases.** Phases 3, 4, 6, 7, 8, 10 must remain byte-identical for greenfield paths. Any modification to these phases risks STATE-03 (greenfield regression). The brownfield branch jumps OVER these phases; it never touches them.

- **Anti-Pattern: Spawning brownfield-flow as Task() agent.** brownfield-flow.md uses AskUserQuestion (interactive questioning in Steps 6-7). Task() agents cannot interact with users. The workflow must execute inline within the command's context.

- **Anti-Pattern: Exiting and re-entering the command.** Current Phase 2 says "Run `/gsd:map-codebase` first, then return to `/gsd:new-project`". This breaks the single-command UX goal. The new implementation runs map-codebase inline.

- **Anti-Pattern: Duplicating brownfield-flow logic in new-project.md.** The command should reference/invoke brownfield-flow, not copy its 419 lines inline. The command orchestrates; the workflow defines the flow.

- **Anti-Pattern: Brownfield path producing different artifacts than greenfield.** Both paths must produce the same set of planning artifacts (.planning/PROJECT.md, config.json, ROADMAP.md, STATE.md, REQUIREMENTS.md). The content differs but the file set should be consistent for downstream commands.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Brownfield detection | New detection logic | Embed brownfield-detection.md script verbatim | 55-line script already tested, covers 33 extensions, handles edge cases |
| Codebase mapping | New mapping step | Invoke map-codebase workflow | 4 parallel mapper agents already defined and tested |
| Analysis + purpose routing | New analysis pipeline | Invoke brownfield-flow.md workflow | 9-step workflow handles analysis, dashboard, purpose selection, questioning, roadmap |
| Brownfield PROJECT.md | New template | Reuse existing Phase 4 brownfield logic (lines 177-202) | Current new-project.md already has brownfield PROJECT.md creation logic |
| Config.json creation | New config step | Reuse existing Phase 5 | Same config preferences apply to both paths |
| Roadmap generation | New roadmap step | Already done by brownfield-flow Step 9 | Brownfield-flow spawns gsd-roadmapper with purpose-aware context |

**Key insight:** Phase 4 is almost entirely an ORCHESTRATION task. Every building block already exists. The work is wiring them together in the right order within new-project.md's phase flow.

## Common Pitfalls

### Pitfall 1: Breaking Greenfield Flow with Detection Changes

**What goes wrong:** Replacing Phase 1 Step 3 detection changes variable names or behavior that downstream greenfield phases depend on.

**Why it happens:** The new detection script has different variable semantics (e.g., `HAS_CODEBASE_MAP` returns "yes"/"no" instead of "yes"/empty).

**How to avoid:**
- Map variable name changes carefully between old and new detection scripts
- Phase 2's greenfield routing check must use `MODE == "greenfield"` (new) not `CODE_FILES is empty AND HAS_PACKAGE is empty` (old)
- The `MODE` variable is the single source of truth after detection. Downstream phases should check `MODE`, not re-derive from raw signals
- Test: Empty directory must produce `MODE=greenfield` and reach Phase 3 unchanged

**Warning signs:** Greenfield projects trigger brownfield detection messages or skip questioning.

### Pitfall 2: Brownfield-Flow Interaction Model Mismatch

**What goes wrong:** Trying to spawn brownfield-flow as a Task() agent, which fails because the workflow uses AskUserQuestion for interactive purpose selection and questioning.

**Why it happens:** Other workflows (like map-codebase) are spawned via Task(). brownfield-flow is different because it has interactive steps.

**How to avoid:** Execute brownfield-flow inline within the new-project.md command context. The command definition should instruct the executing agent to follow the brownfield-flow.md workflow steps directly, not delegate to a sub-agent. This is similar to how new-project.md currently executes its questioning phase (Phase 3) inline rather than delegating it.

**Warning signs:** "AskUserQuestion not available" errors during brownfield-flow execution.

### Pitfall 3: Missing Artifacts at Convergence Point

**What goes wrong:** The brownfield path arrives at Phase 5 but is missing artifacts that Phase 5+ expects. For example, Phase 10 (Done) references REQUIREMENTS.md but the brownfield path wrote requirements in a different format.

**Why it happens:** Brownfield-flow produces REQUIREMENTS.md with purpose-based IDs (CONCERN-01, IMPROVE-01) instead of category-based IDs (AUTH-01, CONT-02). Downstream tools that expect category IDs may fail.

**How to avoid:**
- Verify that brownfield-flow's output artifacts match the file names and locations expected by Phase 5+ phases
- Phase 10 Done banner dynamically reads artifact files rather than assuming a specific format
- STATE.md must record that this is a brownfield project so downstream commands handle both formats

**Warning signs:** Phase 10 shows "No roadmap found" or "0 requirements" for brownfield projects.

### Pitfall 4: Double Execution of Shared Steps

**What goes wrong:** Brownfield path writes PROJECT.md in Phase 2B Step 3, then greenfield Phase 4 (Write PROJECT.md) also tries to write it, overwriting the brownfield version.

**Why it happens:** The jump from Phase 2B to Phase 5 is not properly implemented, and the flow falls through to Phase 3/4.

**How to avoid:** Use a clear branching construct. After Phase 2B completes, the flow must explicitly jump to Phase 5 with a clear "Skip to Phase 5" instruction. Consider using a variable like `IS_BROWNFIELD=true` set during Phase 2B that Phase 3 checks: "IF IS_BROWNFIELD: skip to Phase 5."

**Warning signs:** PROJECT.md is written twice (first brownfield version, then overwritten by greenfield questioning).

### Pitfall 5: Codebase-Map-Then-Exit Legacy Pattern

**What goes wrong:** The current Phase 2 exits the command after suggesting map-codebase. If the new Phase 2B forgets to run map-codebase inline and instead preserves the exit pattern, the user still has a two-command workflow.

**Why it happens:** Copy-pasting the existing Phase 2 and adding brownfield-flow without removing the "exit command" instruction.

**How to avoid:** Phase 2B must explicitly state: "Do NOT exit the command. Run map-codebase workflow inline, wait for completion, then continue to brownfield-flow." Remove all references to "Exit command" in the brownfield path.

**Warning signs:** User sees "Run /gsd:map-codebase first, then return to /gsd:new-project" for brownfield projects.

## Code Examples

These are Markdown command definition patterns showing exactly what the modified sections should look like.

### Phase 1 Step 3: Detection Replacement

The Bash block in Phase 1 Step 3 should be replaced with the full brownfield-detection.md script. The current 3-line detection:

```bash
# CURRENT (to be replaced):
CODE_FILES=$(find . -name "*.ts" -o -name "*.js" ...
HAS_PACKAGE=$([ -f package.json ] || ...
HAS_CODEBASE_MAP=$([ -d .planning/codebase ] && echo "yes")
```

Becomes the 55-line multi-signal script from brownfield-detection.md, ending with:

```bash
# Output variables available after detection:
# MODE         = greenfield | scaffolded | brownfield
# CODE_FILE_COUNT = integer
# PRIMARY_LANG = language name
# HAS_PACKAGE  = manifest filename or empty
# GIT_COMMIT_COUNT = integer
# SRC_DIR_COUNT = integer
# HAS_CODEBASE_MAP = yes | no
```

### Phase 2: Mode Routing (Replacement)

```markdown
## Phase 2: Mode Routing

Check the MODE variable from Phase 1 detection:

**If MODE == "greenfield":**
No existing code detected. Continue directly to Phase 3 (Deep Questioning).

**If MODE == "scaffolded":**
Display informational message:
"This appears to be a scaffolded project ({CODE_FILE_COUNT} files, {GIT_COMMIT_COUNT} commits).
 Treating as a new project."
Continue to Phase 3 (Deep Questioning).

**If MODE == "brownfield":**
Display detection summary:
"Existing codebase detected: {CODE_FILE_COUNT} files, {PRIMARY_LANG}, {GIT_COMMIT_COUNT} commits."
Continue to Phase 2B (Brownfield Pipeline).
```

### Phase 2B: Brownfield Pipeline (New)

```markdown
## Phase 2B: Brownfield Pipeline

**This phase runs ONLY when MODE == "brownfield".**

### Step 1: Map Codebase

Check if codebase is already mapped:
- If HAS_CODEBASE_MAP == "yes": Skip mapping, display "Using existing codebase map."
- If HAS_CODEBASE_MAP == "no":

Display banner:
GSD > MAPPING CODEBASE

Execute the map-codebase workflow inline:
@get-shit-done/workflows/map-codebase.md

[Spawn 4 parallel mapper agents, wait for completion, verify 7 documents]

### Step 2: Run Brownfield Analysis + Purpose Routing

Display banner:
GSD > ANALYZING CODEBASE

Execute the brownfield-flow workflow inline:
@get-shit-done/workflows/brownfield-flow.md

[Steps 1-5: Analysis pipeline]
[Steps 6-9: Purpose routing (purpose selection, questioning, debug bridge, roadmap)]

After brownfield-flow completes, the following artifacts exist:
- .planning/brownfield-analysis.md
- .planning/ROADMAP.md
- .planning/STATE.md
- .planning/REQUIREMENTS.md

### Step 3: Write PROJECT.md (Brownfield)

Read .planning/codebase/ARCHITECTURE.md and STACK.md.
Infer Validated requirements from existing code.

[Use the existing brownfield PROJECT.md logic from Phase 4 lines 177-202]

Commit PROJECT.md.

### Step 4: Continue to Phase 5

Brownfield pipeline complete. Skip to Phase 5 (Workflow Preferences).
Do NOT execute Phase 3 (Deep Questioning), Phase 4 (Write PROJECT.md),
Phase 6 (Research), Phase 7 (Requirements), or Phase 8 (Roadmap).
These have been handled by brownfield-flow.
```

### Phase 5+ Guard Condition

The brownfield path skips Phases 6-8 but still needs Phase 5 and Phase 10. Add a guard to Phases 6-8:

```markdown
## Phase 6: Research Decision

**If brownfield project (MODE == "brownfield"):** Skip this phase.
Brownfield analysis serves as the domain research. Continue to Phase 10.

**If greenfield project:** [existing Phase 6 logic unchanged]
```

Same pattern for Phases 7 and 8.

## State of the Art

| Current Approach | New Approach | Change | Impact |
|------------------|-------------|--------|--------|
| Basic 3-variable detection | Multi-signal 7-variable detection | Phase 1 Step 3 | More accurate brownfield/greenfield/scaffolded classification |
| Binary brownfield offer (map or skip) | Three-way MODE routing | Phase 2 | Eliminates exit-and-return pattern, adds scaffolding awareness |
| Exit command for map-codebase | Inline map-codebase execution | Phase 2B | Single-command UX from start to finish |
| No brownfield pipeline | Full analysis + purpose routing | Phase 2B | Complete brownfield workflow integrated |
| Greenfield-only progression | Conditional phase skipping | Phases 6-8 | Brownfield bypasses greenfield-specific phases |

## Open Questions

### 1. How Should map-codebase Be Invoked Inline?

**What we know:** The `map-codebase.md` command spawns 4 parallel Task() agents. When run as a separate command, it works normally. When invoked inline from new-project.md, the executing agent needs to follow the map-codebase workflow directly.

**What's unclear:** Should new-project.md reference `@get-shit-done/workflows/map-codebase.md` and execute it as a sub-workflow? Or should it duplicate the key orchestration steps (spawn 4 mappers, verify 7 docs)?

**Recommendation:** Reference the map-codebase workflow via `@` reference and instruct the executing agent to follow it. This avoids duplication and ensures any future map-codebase improvements automatically apply. The workflow is designed to be followed by any agent with Task() capability, which the new-project.md command has.

**Confidence:** MEDIUM -- the inline invocation pattern is used elsewhere (new-project.md Phase 8 spawns gsd-roadmapper via Task()) but map-codebase's full 4-agent orchestration is more complex.

### 2. Should Brownfield Projects Get the Research Phase (Phase 6)?

**What we know:** Greenfield Phase 6 spawns 4 parallel researchers for domain discovery. Brownfield projects already have analysis via brownfield-flow (which is domain-specific). The analysis covers stack, architecture, concerns, testing -- overlapping with research dimensions.

**What's unclear:** Is there value in running domain research AFTER brownfield analysis? For example, a brownfield project using an outdated stack might benefit from research showing the current ecosystem state.

**Recommendation:** Skip Phase 6 for brownfield projects. The brownfield analysis + purpose routing already captures the domain-specific context needed for planning. If users want additional domain research, they can run it separately. This simplifies the flow and avoids token waste.

**Confidence:** HIGH -- brownfield-flow produces analysis, purpose-specific questioning, and a purpose-aware roadmap. Adding generic domain research on top would be redundant.

### 3. How Does Phase 10 (Done) Adapt for Brownfield?

**What we know:** Phase 10 displays a completion banner with artifact locations and next steps. The banner references specific files like `.planning/research/` and `.planning/REQUIREMENTS.md`.

**What's unclear:** Should the Done banner have brownfield-specific content? Or should it dynamically detect which artifacts exist?

**Recommendation:** Make the Done banner dynamic. Check which files exist and display accordingly:
- If `.planning/brownfield-analysis.md` exists: Show "Analysis" row
- If `.planning/research/` exists: Show "Research" row
- ROADMAP.md, REQUIREMENTS.md, STATE.md, PROJECT.md, config.json are always present

This approach requires minimal code changes and works for both paths.

**Confidence:** HIGH -- the banner is purely presentational and easy to make conditional.

### 4. Token Budget for execution_context References

**What we know:** Adding brownfield references to execution_context increases initial token load by ~5-8K tokens. Greenfield invocations would pay this cost unnecessarily.

**What's unclear:** Is 5-8K tokens significant enough to warrant conditional loading? Claude Code's context window is large (200K+).

**Recommendation:** Use conditional loading (Pattern 6 approach 2). Do NOT add brownfield references to execution_context. Instead, within Phase 2B instructions, explicitly tell the agent to read the brownfield workflow and reference files. This keeps greenfield invocations lean. The brownfield path already involves multiple agent spawns that consume significant tokens, so the incremental context loading cost is negligible in comparison.

**Confidence:** HIGH -- conditional loading is a trivial implementation (read files within the phase instruction) and saves tokens for the common greenfield case.

### 5. What Exactly Does "Inline Workflow Execution" Mean for brownfield-flow?

**What we know:** brownfield-flow.md is a 9-step workflow with interactive steps (AskUserQuestion). It cannot be spawned as Task(). The new-project.md command must execute it "inline."

**What's unclear:** In the GSD convention system, what does "inline execution" mean concretely? Does the command include `@get-shit-done/workflows/brownfield-flow.md` as a reference and instruct the agent to follow its steps? Or does the command embed a summary of the workflow steps?

**Recommendation:** Use the `@` reference pattern. In Phase 2B, the command says: "Follow the brownfield-flow workflow: `@get-shit-done/workflows/brownfield-flow.md`". This instructs the executing agent to read and follow the workflow document step by step. The workflow's own instructions handle all the branching, agent spawning, and user interaction. This is the same pattern used when new-project.md references `@get-shit-done/references/questioning.md` for Phase 3 -- the agent reads the reference and follows its guidance.

For the non-interactive Task()-compatible steps (Steps 1-5: analysis), those can be delegated to sub-agents via Task(). For the interactive steps (Steps 6-7: purpose selection and questioning), the executing agent handles them directly. Step 8 (debug bridge) is conditional. Step 9 (roadmap) spawns gsd-roadmapper via Task().

**Confidence:** HIGH -- this follows established patterns in new-project.md (Phase 3 references questioning.md, Phase 8 spawns roadmapper).

## Greenfield Regression Testing Scenarios

This section directly addresses research question 5 (STATE-03 requirement).

### Scenario Matrix

| # | Scenario | Setup | Expected Behavior | What Could Break |
|---|----------|-------|-------------------|------------------|
| G1 | Empty directory | `mkdir test && cd test` | MODE=greenfield, Phase 3 starts, "What do you want to build?" | Detection change produces wrong MODE |
| G2 | Only .git | `git init` | MODE=greenfield, Phase 3 starts | GIT_COMMIT_COUNT=0 + no code should still be greenfield |
| G3 | Only .planning/ | `mkdir .planning` | MODE=greenfield, Phase 3 starts (no code, no package) | .planning directory should not affect detection |
| G4 | Only .git + .planning/ | `git init && mkdir .planning` | MODE=greenfield | Combined presence should not trigger brownfield |
| G5 | package.json only | `npm init -y` | MODE=greenfield (no code files, just manifest) | Package-only should not be brownfield |
| G6 | 3 files, 1 commit | Small manual project | MODE=scaffolded, flows to Phase 3 | Scaffolded should downgrade to greenfield path |
| G7 | create-next-app output | ~10 files, 1 commit | MODE=scaffolded | CRA/Next scaffolds should not trigger brownfield |
| G8 | Full greenfield flow | Empty dir, answer all questions | All 10 phases execute in order, all artifacts created | Phase skip logic incorrectly activating |
| G9 | Greenfield with "Skip research" | Empty dir, skip Phase 6 | Phases 3->4->5->7->8->10, no research/ dir | Phase skip guard wrong |
| G10 | Greenfield with codebase map | `mkdir .planning/codebase` + files, but empty otherwise | Depends on MODE detection (likely greenfield if no code) | HAS_CODEBASE_MAP should not override MODE |

### Regression Test Protocol

For each scenario:
1. Set up the directory state
2. Run `/gsd:new-project`
3. Verify MODE output matches expected
4. Verify the correct phase flow executes
5. Verify no brownfield messages appear (for greenfield scenarios)
6. Verify all greenfield artifacts are created correctly

**Critical assertion:** For scenarios G1-G5, the user should see EXACTLY the same experience as before Phase 4 changes. No new messages, no brownfield mentions, no detection output shown.

### Brownfield Detection Scenarios (for completeness)

| # | Scenario | Setup | Expected Behavior |
|---|----------|-------|-------------------|
| B1 | Mature Node.js | 50+ .ts files, package.json, 20+ commits | MODE=brownfield, Phase 2B executes |
| B2 | Python project | 30+ .py files, requirements.txt, 15 commits | MODE=brownfield, Phase 2B executes |
| B3 | Already-mapped | .planning/codebase/ exists | MODE=brownfield, map-codebase skipped |
| B4 | 5 files, 10 commits, package.json | Small but active | MODE=brownfield (HAS_PACKAGE + GIT_COMMIT_COUNT > 10) |

## Sources

### Primary (HIGH confidence)

- `commands/gsd/new-project.md` (lines 1-991) -- The file being modified. Every phase analyzed for brownfield impact. Phase 1 detection (lines 60-67), Phase 2 offer (lines 69-91), Phase 4 brownfield PROJECT.md (lines 177-202), Phase 5 config (lines 238-376), Phase 8 roadmap (lines 771-911), Phase 10 done (lines 913-948).
- `get-shit-done/references/brownfield-detection.md` (lines 1-541) -- Detection logic to embed. Complete Bash script (lines 306-427), integration guide (lines 436-481), testing scenarios (lines 482-539).
- `get-shit-done/workflows/brownfield-flow.md` (lines 1-419) -- Workflow to invoke. 9 steps: check_prerequisites, determine_scope, run_analysis, present_dashboard, return_result, select_purpose, purpose_questioning, bridge_to_debug, generate_roadmap.
- `commands/gsd/map-codebase.md` (lines 1-93) -- Codebase mapping command. Spawn 4 parallel agents, verify 7 documents, commit results.
- `.planning/ROADMAP.md` (lines 76-88) -- Phase 4 definition: goal, requirements (INFRA-04, STATE-03), success criteria.
- `.planning/REQUIREMENTS.md` (lines 40-41, 33) -- INFRA-04 and STATE-03 requirement definitions.
- `.planning/STATE.md` (lines 1-93) -- Current project state, prior decisions (especially 03-03: purpose routing defaults to true).
- `.planning/phases/03-purpose-routing/03-RESEARCH.md` (lines 1-892) -- Phase 3 research with Open Question 4 (integration sequence with Phase 4) and Pattern 5 (backward compatibility).

### Secondary (MEDIUM confidence)

- `get-shit-done/references/brownfield-questioning.md` (lines 1-216) -- Purpose-specific questioning reference. Read for understanding brownfield-flow's questioning behavior but not directly modified by Phase 4.
- `get-shit-done/templates/brownfield-roadmap.md` (lines 1-142) -- Purpose-aware roadmap template. Used by brownfield-flow internally.
- `get-shit-done/templates/brownfield-summary.md` (lines 1-325) -- Analysis output template. Used by brownfield analyzer internally.

### Tertiary (LOW confidence)

- None. All findings are grounded in direct file analysis of the artifacts involved.

## Metadata

**Confidence breakdown:**
- Integration point analysis: HIGH -- direct line-by-line analysis of new-project.md's 10 phases identified exact modification points
- Detection upgrade design: HIGH -- brownfield-detection.md explicitly includes integration guide section describing how to replace Phase 1 Step 3
- Brownfield-flow invocation: HIGH -- interaction model analysis (AskUserQuestion = inline, not Task) matches established GSD patterns (questioning in Phase 3 is inline)
- Convergence point: HIGH -- artifact analysis shows brownfield-flow produces ROADMAP.md, STATE.md, REQUIREMENTS.md, making Phases 6-8 redundant for brownfield
- Greenfield regression: HIGH -- complete scenario matrix with 10 greenfield + 4 brownfield test cases, derived from brownfield-detection.md testing scenarios section
- Token optimization: MEDIUM -- conditional loading recommendation is based on general best practices, not measured impact

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (stable -- no external dependency changes; only internal GSD convention evolution)
