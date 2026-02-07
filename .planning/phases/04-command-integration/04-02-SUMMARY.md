---
key-files:
  created: []
  modified:
    - commands/gsd/new-project.md
---

## Summary

Added the complete brownfield pipeline to `commands/gsd/new-project.md`: Phase 2B (4 steps: map-codebase inline, brownfield-flow inline with purpose routing, brownfield PROJECT.md with Validated requirements, jump to Phase 5), brownfield skip guards prepended to Phases 6-8, and a dynamic Phase 10 Done banner that conditionally displays Analysis/Research rows based on file existence. Combined with Plan 04-01's detection and routing, this completes INFRA-04 (brownfield branching integration) so that `/gsd:new-project` on a directory with existing code automatically maps the codebase, runs brownfield analysis + purpose routing, writes PROJECT.md, and converges at Phase 5 -- all in a single command session with no exit-and-return pattern. Greenfield path through Phases 3-10 is completely unchanged (STATE-03).

## Self-Check: PASSED

| Must-Have | Status |
|-----------|--------|
| Brownfield project runs map-codebase inline (no exit-and-return) | PASS |
| Brownfield project runs brownfield-flow inline with purpose routing | PASS |
| Brownfield project writes PROJECT.md with Validated requirements from codebase | PASS |
| Brownfield project skips Phases 3, 4, 6, 7, 8 and converges at Phase 5 | PASS |
| Greenfield project executes Phases 3-10 unchanged (STATE-03 regression safety) | PASS |
| Phase 10 Done banner adapts artifacts dynamically for both paths | PASS |
| commands/gsd/new-project.md contains "Phase 2B: Brownfield Pipeline" | PASS |
| Phase 2 MODE==brownfield routing -> Phase 2B Step 1 map-codebase via control flow | PASS |
| Phase 2B Step 2 brownfield-flow -> Phase 5 via phase jump (skip Phases 3-4, 6-8) | PASS |
| Phase 2B brownfield-flow -> brownfield-analysis.md, ROADMAP.md, STATE.md, REQUIREMENTS.md | PASS |
| Phase 10 Done banner -> dynamic artifact detection (brownfield-analysis.md check) | PASS |
| execution_context unchanged (conditional loading, no brownfield references upfront) | PASS |

## Deliverables

- `commands/gsd/new-project.md` (MODIFIED)
  - Phase 2B: Brownfield Pipeline (4 steps: map-codebase, brownfield-flow, PROJECT.md, jump to Phase 5)
  - Brownfield guard before Phase 3: "If MODE == brownfield: Skip to Phase 5"
  - Brownfield guard at Phase 6: skip (analysis serves as research)
  - Brownfield guard at Phase 7: skip (brownfield-flow produced REQUIREMENTS.md)
  - Brownfield guard at Phase 8: skip (brownfield-flow produced ROADMAP.md)
  - Phase 10: Dynamic artifact table with conditional Analysis/Research rows
  - Objective: updated for greenfield + brownfield flows
  - Creates list: added brownfield-analysis.md and codebase/
  - Output section: added brownfield-specific artifacts
  - Success criteria: added brownfield items

## Decisions

None. All implementation followed the plan exactly. Phase 2B structure matches the 04-RESEARCH.md code examples. Guard format is consistent across all phases. execution_context left unchanged per research recommendation (conditional loading).

## Issues

None.
