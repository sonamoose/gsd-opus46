# Delta Report Template

Template for `.planning/codebase/DELTA-REPORT.md` — comparison between two analysis snapshots showing what changed.

**Purpose:** Compare a previous codebase analysis snapshot against the current analysis to surface improvements, regressions, and new findings. The output helps users and downstream agents (audit-milestone, planner) understand the impact of work done between the two analysis points.

---

## File Template

```markdown
# Delta Report

**Comparison:** {previous_date} → {current_date}
**Previous snapshot:** `.planning/codebase/snapshots/{previous_date}/`
**Current analysis:** `.planning/codebase/`

## Change Summary

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Codebase Health | {Good/Moderate/Concerning} | {Good/Moderate/Concerning} | {↑ Improved / → Unchanged / ↓ Degraded} |
| Critical Concerns | {N} | {M} | {+/-K} |
| Moderate Concerns | {N} | {M} | {+/-K} |
| Minor Concerns | {N} | {M} | {+/-K} |
| Net Concern Change | — | — | {+/-total} |

## Concerns Tracker

### Resolved

[Concerns present in the previous snapshot but no longer found in current analysis]

| Concern | Previous Severity | Evidence of Resolution |
|---------|------------------|----------------------|
| {Concern title} | {critical/moderate/minor} | {What changed — file path or pattern that confirms resolution} |

### New

[Concerns not present in the previous snapshot but found in current analysis]

| Concern | Severity | Details |
|---------|----------|---------|
| {Concern title} | {critical/moderate/minor} | {One-line description with affected file path} |

### Persisting

[Concerns present in both snapshots — note severity changes if any]

| Concern | Previous Severity | Current Severity | Change |
|---------|------------------|------------------|--------|
| {Concern title} | {severity} | {severity} | {↑ Escalated / → Same / ↓ De-escalated} |

## Dimension Changes

[Compare each of the 7 dimensions between snapshots. Only include dimensions where meaningful changes occurred.]

### {Dimension Name}

**Before:** {Key finding from previous snapshot}
**After:** {Key finding from current analysis}
**Change:** {What specifically changed — be concrete}

## Impact Assessment

**Overall trajectory:** {Improving / Stable / Declining}
**Key improvements:** {1-3 bullet points of most impactful positive changes}
**Areas of concern:** {1-3 bullet points of regressions or persistent issues, or "None" if all improving}

---

*Delta report generated: {YYYY-MM-DD}*
*Previous snapshot: .planning/codebase/snapshots/{date}/*
*Current analysis: .planning/codebase/*.md*
```

<guidelines>
**What belongs in DELTA-REPORT.md:**
- Factual comparisons between two specific analysis snapshots
- Concern status tracking (resolved, new, persisting with severity changes)
- Concrete dimension-level changes with evidence from both snapshots
- Impact assessment grounded in the comparison data
- File paths from both snapshots for traceability

**What does NOT belong here:**
- Recommendations or action items (those come from planner/audit agents)
- Analysis of code changes themselves (this compares analysis documents, not code)
- Information not present in either snapshot
- Predictions about future trajectory beyond what the data shows

**Concern matching strategy:**
Match concerns between snapshots by semantic similarity, not exact string match. A concern titled "N+1 query in courses" in the old snapshot and "N+1 query pattern resolved" in current maps to the same concern. Use file paths as the primary matching key when concern titles differ.

**When dimensions are unchanged:**
If a dimension shows no meaningful change between snapshots, omit it from the Dimension Changes section. Only include dimensions with actual changes. If NO dimensions changed, write: "No significant dimension changes detected between snapshots."

**Severity change tracking:**
If a persisting concern changed severity (e.g., critical → moderate), note it as "De-escalated" with evidence. This is valuable for tracking partial improvements.

**Section length guidelines:**
- Change Summary table: exactly 5 rows
- Resolved/New/Persisting: variable, depends on actual changes
- Dimension Changes: only changed dimensions, 3 lines each (before/after/change)
- Impact Assessment: 2-6 bullet points total
- Total document target: 40-80 lines
</guidelines>
