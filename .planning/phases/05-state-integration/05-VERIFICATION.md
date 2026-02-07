# Phase 5 Verification

## Must-Haves (8/8 PASSED)

### 1. [PASS] project.md template defines a Codebase Context section for brownfield projects

**Evidence:** `get-shit-done/templates/project.md` lines 51-60 define:

```markdown
## Codebase Context

<!-- For brownfield projects only. Omit entire section for greenfield. -->

**Mode:** brownfield
**Primary Language:** [Language from detection]
**Analysis:** `.planning/brownfield-analysis.md`
**Health:** [Good / Moderate / Concerning]
**Purpose:** [Fix / Improve / Refactor]
**Codebase Map:** `.planning/codebase/`
```

The section is a top-level `## Codebase Context` heading within the template block (lines 7-79), containing all required fields: Mode, Primary Language, Analysis path, Health rating, Purpose, and Codebase Map path.

---

### 2. [PASS] state.md template defines a Codebase Context subsection under Accumulated Context

**Evidence:** `get-shit-done/templates/state.md` lines 69-76 define:

```markdown
### Codebase Context

<!-- For brownfield projects only. Omit for greenfield. -->

**Analysis:** `.planning/brownfield-analysis.md`
**Purpose:** [Fix / Improve / Refactor]
**Health:** [Good / Moderate / Concerning]
```

This is a `### Codebase Context` subsection nested under `## Accumulated Context` (line 47), exactly as required. It includes analysis reference, purpose, and health rating.

---

### 3. [PASS] Brownfield sections include conditional markers so greenfield projects omit them

**Evidence:**

- `project.md` line 53: `<!-- For brownfield projects only. Omit entire section for greenfield. -->`
- `state.md` line 71: `<!-- For brownfield projects only. Omit for greenfield. -->`
- `project.md` guidelines line 119: `"Only present for brownfield projects; omit entirely for greenfield"`
- `state.md` sections line 172: `"Omit entirely for greenfield projects"`
- `state.md` lifecycle line 104: `"If brownfield: populate Codebase Context with analysis reference, purpose, and health from brownfield-flow results"`

Both templates use HTML comment conditional markers instructing agents to omit the sections for greenfield projects. The guidelines sections reinforce this with explicit prose.

---

### 4. [PASS] project.md brownfield guidance instructs inferring Validated requirements from ARCHITECTURE.md and STACK.md

**Evidence:** `project.md` lines 166-198 (`<brownfield>` section) define:

```markdown
2. **Infer Validated requirements** from existing code:
   - Read ARCHITECTURE.md for architecture patterns and key capabilities
   - Read STACK.md for language, framework, and runtime
   - What does the codebase actually do?
   - What patterns are established?
   - What's clearly working and relied upon?
   - Format each inferred capability as `- ✓ [Capability description] — existing` in the Validated section
```

Lines 172-178 explicitly instruct reading ARCHITECTURE.md and STACK.md to infer Validated requirements with a specific format (`- ✓ [Capability description] — existing`).

---

### 5. [PASS] Brownfield PROJECT.md Codebase Context section is reachable by gsd-planner through existing @file references

**Evidence:** The propagation chain to gsd-planner is:

1. `agents/gsd-planner.md` line 1004-1011 (`<step name="load_project_state">`): Reads `.planning/STATE.md` first.
2. `agents/gsd-planner.md` lines 1025-1043 (`<step name="load_codebase_context">`): Checks for `.planning/codebase/*.md` and loads relevant documents based on phase type, including ARCHITECTURE.md and STACK.md.
3. `get-shit-done/templates/planner-subagent-prompt.md` line 16-17: `@.planning/STATE.md` is an explicit @file reference in the planning context.
4. `get-shit-done/templates/phase-prompt.md` lines 47-49: Plan context includes `@.planning/PROJECT.md`, `@.planning/ROADMAP.md`, `@.planning/STATE.md` as @file references.

The gsd-planner reads STATE.md (which contains Codebase Context subsection with analysis reference), and the plan templates reference PROJECT.md (which contains Codebase Context section). Both paths are connected.

---

### 6. [PASS] Brownfield STATE.md Codebase Context subsection is reachable by gsd-executor through existing @file references

**Evidence:** The propagation chain to gsd-executor is:

1. `agents/gsd-executor.md` lines 19-54 (`<step name="load_project_state">`): Reads `.planning/STATE.md` as the **first** step (`priority="first"`), parsing accumulated decisions, blockers/concerns, and alignment status.
2. `agents/gsd-executor.md` lines 57-71 (`<step name="load_plan">`): Reads @-references from the plan file, which includes `@.planning/PROJECT.md` and `@.planning/STATE.md` (from phase-prompt.md template lines 47-49).
3. The executor's `load_project_state` step reads the full STATE.md file including the `### Codebase Context` subsection under `## Accumulated Context`.

Both the executor agent definition and the plan template ensure STATE.md (with Codebase Context) is read.

---

### 7. [PASS] The full propagation chain from brownfield-analysis.md through templates to downstream agents has no gaps

**Evidence:** The complete chain is:

1. **brownfield-flow.md** (lines 67-94): Spawns gsd-brownfield-analyzer which writes `.planning/brownfield-analysis.md`.
2. **brownfield-flow.md** (lines 318-393): generate_roadmap step spawns gsd-roadmapper with `@.planning/brownfield-analysis.md` reference.
3. **project.md template** (line 57): `**Analysis:** .planning/brownfield-analysis.md` links PROJECT.md to the analysis.
4. **project.md template** (lines 172-178): Brownfield guidance instructs reading ARCHITECTURE.md and STACK.md to infer Validated requirements.
5. **state.md template** (line 73): `**Analysis:** .planning/brownfield-analysis.md` links STATE.md to the analysis.
6. **state.md lifecycle** (line 104): `"If brownfield: populate Codebase Context with analysis reference, purpose, and health from brownfield-flow results"`.
7. **planner-subagent-prompt.md** (line 17): `@.planning/STATE.md` in planning context.
8. **phase-prompt.md** (lines 47-49): `@.planning/PROJECT.md`, `@.planning/ROADMAP.md`, `@.planning/STATE.md` in plan context.
9. **gsd-planner.md** (lines 1004-1043): `load_project_state` reads STATE.md, `load_codebase_context` reads codebase documents.
10. **gsd-executor.md** (lines 19-54): `load_project_state` reads STATE.md as first step.

Each link in the chain is verified. No gaps exist between brownfield-analysis.md output and downstream agent consumption.

---

### 8. [PASS] Greenfield projects are unaffected by the new template sections

**Evidence:**

- Both templates use conditional HTML comments: `<!-- For brownfield projects only. Omit entire section for greenfield. -->` (project.md line 53) and `<!-- For brownfield projects only. Omit for greenfield. -->` (state.md line 71).
- project.md guidelines line 119: `"Only present for brownfield projects; omit entirely for greenfield"`.
- state.md sections line 172: `"Omit entirely for greenfield projects"`.
- state.md lifecycle line 104 uses conditional: `"If brownfield: populate..."` — meaning greenfield projects skip this step.
- gsd-planner.md `load_codebase_context` step (line 1025-1043) checks for `.planning/codebase/*.md` existence before loading; greenfield projects have no such directory, so the step is effectively a no-op.
- The Codebase Context sections are additive — no existing template sections were modified or removed.

Greenfield projects omit the sections entirely and no existing functionality is broken.

---

## Success Criteria (3/3 SATISFIED)

### 1. [SATISFIED] Brownfield PROJECT.md records existing capabilities as Validated requirements inferred from ARCHITECTURE.md and STACK.md

**Based on:** Must-haves #1 and #4.

- Must-have #1 confirms the Codebase Context section exists in PROJECT.md template with analysis reference, health, and purpose fields.
- Must-have #4 confirms the `<brownfield>` guidance at lines 172-178 explicitly instructs: "Read ARCHITECTURE.md for architecture patterns and key capabilities" and "Read STACK.md for language, framework, and runtime" to infer Validated requirements, formatted as `- ✓ [Capability description] — existing`.

The mechanism for automatic inference is documented and will be followed by any agent that processes the PROJECT.md template.

---

### 2. [SATISFIED] PROJECT.md Codebase Mode section and analysis references are read by gsd-planner and gsd-executor for planning/execution

**Based on:** Must-haves #5 and #6.

- Must-have #5 confirms gsd-planner reads STATE.md (with Codebase Context) via `load_project_state`, reads codebase documents via `load_codebase_context`, and the planner-subagent-prompt includes `@.planning/STATE.md`.
- Must-have #6 confirms gsd-executor reads STATE.md as its first step via `load_project_state` (priority="first"), and plan templates reference `@.planning/PROJECT.md` and `@.planning/STATE.md`.

Both downstream agents have verified paths to consume the brownfield context.

---

### 3. [SATISFIED] STATE.md records codebase context reference and purpose for cross-session state persistence

**Based on:** Must-haves #2 and #3.

- Must-have #2 confirms STATE.md has a `### Codebase Context` subsection under `## Accumulated Context` with Analysis path, Purpose, and Health fields.
- Must-have #3 confirms the section has conditional markers so it only appears for brownfield projects, and the lifecycle section (line 104) specifies when to populate it.

The STATE.md template provides persistent storage for codebase context that survives across sessions.

---

## Verdict: PASSED

All 8 must-haves pass with specific line-number evidence from the actual source files. All 3 success criteria are satisfied. The full propagation chain from brownfield analysis through PROJECT.md and STATE.md templates to downstream agents (gsd-planner and gsd-executor) is complete and gap-free. Greenfield projects are unaffected by the additions.
