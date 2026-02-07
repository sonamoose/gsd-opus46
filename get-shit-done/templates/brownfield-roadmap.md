# Brownfield Roadmap Template

Template for purpose-aware roadmap generation from brownfield analysis. Used by `brownfield-flow.md` Step 9 (generate_roadmap) to guide the `gsd-roadmapper` agent in creating roadmaps ordered by the user's purpose.

**Key difference from greenfield roadmap:**

| Aspect | Greenfield | Brownfield |
|--------|-----------|------------|
| Phase source | Requirements from user questioning | Concerns/improvements from analysis + user purpose |
| Ordering logic | Dependency-based (foundation first) | Purpose-dependent (see below) |
| Requirement IDs | Category-based (AUTH-01, CONT-02) | Purpose-based (CONCERN-01, IMPROVE-01, REFACTOR-01) |
| Success criteria | "User can X" (new capability) | "X no longer occurs" (fix) or "User can now X" (improve) |
| Baseline | None (building from scratch) | Existing codebase (brownfield-analysis.md) |

---

## Ordering Rules

### Fix Mode — Severity Order
Phases ordered by concern severity: critical first, then moderate, then minor.

**Phase derivation:**
- Group selected concerns by severity level
- Phase 1: All critical concerns (if any)
- Phase 2: All moderate concerns (if any)
- Phase 3: All minor concerns (if any)
- Within each phase, order concerns by scope of impact (more files affected = earlier)
- If only one severity level has concerns, split into 2-3 phases by functional area

**Requirement ID format:** CONCERN-01, CONCERN-02, ... (sequential, severity tagged)
**Success criteria pattern:** "[Concern description] no longer occurs" / "[Affected file] handles [scenario] correctly"

### Improve Mode — Dependency Order
Phases ordered by architectural dependency: foundations first, features that depend on them later.

**Phase derivation:**
- Identify foundation changes needed to support improvements
- Phase 1: Foundation/infrastructure changes (shared modules, APIs, data models)
- Phase 2+: Feature improvements ordered by dependency graph
- Independent improvements can be parallelized (noted in phase description)
- If improvement touches core modules, it goes in an earlier phase

**Requirement ID format:** IMPROVE-01, IMPROVE-02, ... (sequential, dependency ordered)
**Success criteria pattern:** "User can now [new capability]" / "[System] supports [new behavior]"

### Refactor Mode — Impact/Effort Ratio Order
Phases ordered by impact/effort ratio: high-impact low-effort first (quick wins).

**Phase derivation:**
- Phase 1: Quick wins — high impact, low effort (naming, conventions, small patterns)
- Phase 2: Structural changes — moderate effort, high impact (module reorganization)
- Phase 3: Deep restructuring — high effort (architecture changes)
- Impact = number of files affected + cross-document references + downstream dependencies
- Effort = single file (low) / same module (moderate) / cross-module (high) / architecture (very high)

**Requirement ID format:** REFACTOR-01, REFACTOR-02, ... (sequential, ratio ordered)
**Success criteria pattern:** "[Area] follows [target pattern]" / "[Code] uses [convention] consistently"

---

## File Template

The roadmapper agent fills this template to produce `.planning/ROADMAP.md`:

```
# Roadmap: [Project Name] — [Purpose] Mode

**Version:** v1.0
**Purpose:** [Fix Issues | Add/Improve Features | Refactor/Restructure]
**Analysis Health:** [Good / Moderate / Concerning — from brownfield-analysis.md]
**Ordering:** [Severity (critical first) | Dependency (foundations first) | Impact/Effort (quick wins first)]
**Phases:** [N]
**Items:** [N] mapped

## Milestone 1: v1.0 — [Purpose-specific milestone name]

### Phase 1: [Name]
**Goal:** [Outcome, not task — what is TRUE when this phase completes]
**Items:** [CONCERN-01, CONCERN-02 | IMPROVE-01 | REFACTOR-01, REFACTOR-02]
**Ordering rationale:** [Why this phase is first — highest severity / foundational dependency / best impact-effort ratio]
**Files affected:** [file paths from analysis]

**Success Criteria:**
1. [Observable behavior confirming the phase goal is met]
2. [Observable behavior]

Plans:
- [ ] TBD (created by /gsd:plan-phase)

---

### Phase 2: [Name]
...

## Coverage

| Item | Description | Phase | Severity/Priority | Status |
|------|-------------|-------|--------------------|--------|
| CONCERN-01 | [From analysis or questioning] | 1 | critical | Pending |
| CONCERN-02 | [From analysis or questioning] | 1 | critical | Pending |
| CONCERN-03 | [From analysis or questioning] | 2 | moderate | Pending |

**Coverage:** [N]/[N] items mapped. 0 unmapped.

## Build Dependencies

[ASCII dependency graph showing phase order]
```

---

## Guidance for Roadmapper Agent

When creating a brownfield roadmap:

1. **Read the purpose context** passed by brownfield-flow.md Step 9. This contains:
   - Selected purpose (fix/improve/refactor)
   - Questioning output (selected concerns, priorities, constraints, target state)
   - Analysis reference (brownfield-analysis.md path)

2. **Apply the ordering rule** matching the purpose (see Ordering Rules above).

3. **Derive phases from items, not from a template.** Let the concerns/improvements/refactoring areas determine the number and structure of phases. Don't impose "every project needs N phases."

4. **Use analysis file paths in success criteria.** Reference specific files from brownfield-analysis.md in success criteria and files-affected sections. This gives downstream planners concrete targets.

5. **Cross-check coverage.** Every item from the questioning output must map to exactly one phase. No orphans.

6. **Write ROADMAP.md, STATE.md, and update REQUIREMENTS.md** following the existing roadmapper protocol.

7. **Include ordering rationale for every phase.** The user should understand WHY this phase is sequenced where it is — not just what it contains.

---

## Anti-Patterns

- **Generic phase names** — "Phase 1: Fix critical issues" is too vague. "Phase 1: Fix auth bypass + N+1 query in course listing" references specific analysis findings.
- **Ignoring the ordering rule** — If purpose is "fix" but phases are ordered by dependency instead of severity, the roadmap contradicts the user's intent.
- **Success criteria without file paths** — "Auth is secure" is unverifiable. "Admin route in app/api/admin/route.ts validates session tokens" is verifiable.
- **Mixing purposes** — A fix roadmap should not include refactoring phases. If the user wants both, they should run purpose routing twice or use "Other" mode.
- **Over-splitting** — 2 concerns should not become 5 phases. Group by severity level or functional area.
