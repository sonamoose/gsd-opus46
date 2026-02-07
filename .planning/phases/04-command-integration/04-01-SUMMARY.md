---
key-files:
  created: []
  modified:
    - commands/gsd/new-project.md
---

## Summary

Replaced the basic 3-line detection in Phase 1 Step 3 of `new-project.md` with the complete 55-line multi-signal brownfield detection script from `brownfield-detection.md`, and replaced the binary Phase 2 "Brownfield Offer" (AskUserQuestion + exit-and-return pattern) with MODE-based three-way routing. The MODE variable (greenfield/scaffolded/brownfield) is now the single routing decision point. Greenfield projects pass silently to Phase 3, scaffolded projects show an informational message then continue to Phase 3, and brownfield projects display a detection summary and route to Phase 2B (placeholder for Plan 02). Phase 3 and all subsequent phases are completely unchanged, preserving greenfield regression safety (STATE-03).

## Self-Check: PASSED

| Must-Have | Status |
|-----------|--------|
| Empty directory produces MODE=greenfield and reaches Phase 3 unchanged | PASS |
| Scaffolded project (<=10 files, <=3 commits) produces MODE=scaffolded and reaches Phase 3 with info message | PASS |
| Mature codebase (>10 files OR package+>10 commits) produces MODE=brownfield | PASS |
| MODE variable is the single source of truth for routing (raw signals not re-checked) | PASS |
| Greenfield Phase 3+ is byte-identical to pre-modification state | PASS |
| commands/gsd/new-project.md contains "MODE=greenfield" | PASS |
| Phase 1 Step 3 detection -> Phase 2 MODE routing via MODE variable | PASS |

## Deliverables

- `commands/gsd/new-project.md` (MODIFIED)
  - Phase 1 Step 3: Full brownfield detection module (5 signals, language detection, mode determination, 7 diagnostic variables)
  - Phase 2: MODE-based three-way routing (greenfield/scaffolded/brownfield)
  - Phase 2B placeholder comment for Plan 02

## Decisions

None. All implementation followed the plan exactly. The detection script was copied verbatim from `brownfield-detection.md` (minus the shebang line as specified). The Phase 2 routing text follows the 04-RESEARCH.md code examples.

## Issues

None.
