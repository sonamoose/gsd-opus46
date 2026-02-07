---
key-files:
  created: []
  modified: [get-shit-done/templates/project.md, get-shit-done/templates/state.md]
---

## Summary

Updated the project.md and state.md templates to formalize brownfield context sections that downstream agents (planner, executor) can reliably parse. The project.md template now includes a `## Codebase Context` section in its template block with Mode, Primary Language, Analysis, Health, Purpose, and Codebase Map fields, expanded `<brownfield>` guidance with explicit instructions to read ARCHITECTURE.md and STACK.md for Validated requirements inference, and a new Codebase Context entry in the `<guidelines>` section. The state.md template now includes a `### Codebase Context` subsection under Accumulated Context with Analysis, Purpose, and Health fields, updated `<sections>` documentation explaining when and how the subsection is populated, and an updated `<lifecycle>` Creation step for brownfield initialization. These changes ensure that brownfield analysis context written by new-project.md Phase 2B and brownfield-flow is guided by template structure rather than ad hoc command logic, making the content consistent and discoverable across all brownfield projects.

## Self-Check: PASSED

All must_haves verified:
- [x] project.md template defines a Codebase Context section for brownfield projects (line 51)
- [x] state.md template defines a Codebase Context subsection under Accumulated Context (line 69)
- [x] Brownfield sections include conditional markers so greenfield projects omit them (project.md line 53, state.md line 71)
- [x] project.md brownfield guidance instructs inferring Validated requirements from ARCHITECTURE.md and STACK.md (lines 173-178)
- [x] project.md has Codebase Context section in template with all 6 fields (lines 51-60)
- [x] state.md has Codebase Context subsection in template with 3 fields (lines 69-75)
- [x] project.md guidelines document the new section (lines 118-125)
- [x] state.md sections documentation explains Codebase Context (lines 167-172)
- [x] state.md lifecycle includes brownfield initialization step (line 104)

## Deliverables

- `get-shit-done/templates/project.md` -- Added `## Codebase Context` section to template block, expanded `<brownfield>` guidance to 5 steps with ARCHITECTURE.md/STACK.md inference instructions, added Codebase Context entry to `<guidelines>`
- `get-shit-done/templates/state.md` -- Added `### Codebase Context` subsection to template block, added Codebase Context entry to `<sections>` documentation, added brownfield step to `<lifecycle>` Creation

## Decisions

None -- all changes followed the plan specification exactly.

## Issues

None
