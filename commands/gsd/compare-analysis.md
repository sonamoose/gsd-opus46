---
name: gsd:compare-analysis
description: Compare codebase analysis snapshots to generate a delta report showing improvements and regressions
argument-hint: "[snapshot-date, e.g., '2025-01-15']"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Write
  - Task
---

<objective>
Compare a previous codebase analysis snapshot against the current analysis to identify what changed. Spawns gsd-delta-analyzer agent to produce DELTA-REPORT.md.

Snapshots are created automatically by `/gsd:map-codebase` when refreshing or updating existing codebase documents.

Output: `.planning/codebase/DELTA-REPORT.md` showing resolved/new/persisting concerns and dimension changes.
</objective>

<execution_context>
<!-- Spawns gsd-delta-analyzer agent which reads both snapshot and current analysis documents -->
</execution_context>

<context>
Snapshot date: $ARGUMENTS (optional — if omitted, list available snapshots and ask)

**Current analysis:**
@.planning/codebase/ (7 codebase documents)
@.planning/brownfield-analysis.md (if exists)

**Snapshots:**
Glob: .planning/codebase/snapshots/*/snapshot-meta.md
</context>

<process>

## 1. Discover Available Snapshots

```bash
ls -d .planning/codebase/snapshots/*/ 2>/dev/null | sort -r
```

**If no snapshots exist:**

```
No analysis snapshots found.

Snapshots are created automatically when you re-run /gsd:map-codebase on an existing codebase map (Refresh or Update mode).

To create your first snapshot:
1. Run /gsd:map-codebase
2. Choose "Refresh" to re-analyze (this archives the current analysis as a snapshot)
3. Run /gsd:compare-analysis to see what changed
```

Exit command.

**If snapshots exist and no argument provided:**

```
Available analysis snapshots:

{For each snapshot directory:}
- {date} — {read trigger from snapshot-meta.md} ({N} documents archived)

Which snapshot do you want to compare against the current analysis?
```

Wait for user to select a snapshot date.

**If argument provided:**
Validate the snapshot directory exists at `.planning/codebase/snapshots/{argument}/`.

## 2. Read Snapshot Metadata

```bash
cat .planning/codebase/snapshots/{selected_date}/snapshot-meta.md
```

Confirm the snapshot contents match expectations.

## 3. Verify Current Analysis Exists

```bash
ls .planning/codebase/*.md 2>/dev/null | grep -v snapshots
```

**If no current analysis documents:**

```
No current codebase analysis found. Run /gsd:map-codebase first to generate the current analysis.
```

Exit command.

## 4. Spawn Delta Analyzer

```
Task(
  prompt="Compare codebase analysis snapshots.

Previous snapshot: .planning/codebase/snapshots/{selected_date}/
Current analysis: .planning/codebase/

Read all documents in both directories. Compare concerns (resolved/new/persisting), dimension changes, and health trajectory.

Write delta report to .planning/codebase/DELTA-REPORT.md using the delta-report template.

Return confirmation with change summary only.",
  subagent_type="gsd-delta-analyzer"
)
```

## 5. Present Results

Read the delta analyzer's confirmation and present to the user:

```
## Delta Analysis: {previous_date} → {current_date}

**Overall trajectory:** {Improving / Stable / Declining}

### Change Summary
- Concerns resolved: {N}
- New concerns: {M}
- Net change: {+/-K}

### Key Changes
{top 3 changes from delta analyzer confirmation}

───────────────────────────────────────────────────────────────

## ▶ Full Report

cat .planning/codebase/DELTA-REPORT.md

───────────────────────────────────────────────────────────────

**Also available:**
- /gsd:map-codebase — refresh analysis and create new snapshot
- /gsd:audit-milestone — audit milestone with delta context

───────────────────────────────────────────────────────────────
```

</process>

<success_criteria>
- [ ] Available snapshots discovered and listed
- [ ] Snapshot selected (from argument or user choice)
- [ ] Current analysis verified to exist
- [ ] gsd-delta-analyzer agent spawned with correct snapshot path
- [ ] DELTA-REPORT.md created
- [ ] Results presented with change summary and next steps
</success_criteria>
