# Plan 03-02 Summary

## Result
Completed successfully.

## Artifact
- `get-shit-done/templates/brownfield-roadmap.md` (NEW, ~142 lines)

## What Was Built
The brownfield-roadmap.md template with purpose-aware ordering rules for fix (severity), improve (dependency), and refactor (impact/effort) modes. The template defines the ROADMAP.md file structure including ordering rationale per phase and a coverage table.

## Key Decisions
- Fix mode: severity order (critical → moderate → minor)
- Improve mode: dependency order (foundations → features)
- Refactor mode: impact/effort ratio (quick wins → deep restructuring)
- Requirement ID prefixes: CONCERN-, IMPROVE-, REFACTOR- (purpose-specific)
- Coverage table includes severity/priority column for traceability

## Must-Have Verification
| # | Truth | Status |
|---|-------|--------|
| 1 | Fix mode roadmap orders phases by severity | ✓ |
| 2 | Improve mode roadmap orders phases by dependency | ✓ |
| 3 | Refactor mode roadmap orders phases by impact/effort ratio | ✓ |
| 4 | Template includes purpose-specific requirement ID prefixes | ✓ |
| 5 | Template includes coverage table with severity/priority | ✓ |
| 6 | Template provides ordering rationale for each phase | ✓ |

## Requirement Coverage
- ROUTE-04: Purpose-aware roadmap generation structure — Foundation laid
