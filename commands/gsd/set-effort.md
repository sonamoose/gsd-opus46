---
name: set-effort
description: View recommended effort levels for GSD agents and adjust via /model
arguments: []
---

<objective>
Show recommended effort levels for GSD agents and guide the user to adjust effort via the `/model` command.
</objective>

<process>

## 1. Show current effort level

Display the current effort setting (if detectable).

## 2. Show agent effort recommendations

```
GSD Agent Effort Levels
═══════════════════════

High (deep reasoning):
  gsd-planner            — architecture decisions, task design
  gsd-plan-checker       — multi-dimensional plan verification
  gsd-debugger           — scientific method investigation
  gsd-research-synthesizer — cross-referencing research outputs

Medium (structured execution):
  gsd-codebase-mapper    — structured exploration, template output
  gsd-roadmapper         — requirement mapping, phase breakdown
  gsd-executor           — plan execution, atomic commits
  gsd-verifier           — goal-backward codebase verification

Low (fast, focused):
  gsd-project-researcher — domain research, web search
  gsd-phase-researcher   — phase-specific research
  gsd-integration-checker — checklist-based verification
```

## 3. Guide user to adjust

```
To adjust effort level:
  /model → use left/right arrow keys to set low/medium/high

To set per environment:
  export CLAUDE_CODE_EFFORT_LEVEL=high

To set per project (settings.json):
  { "effortLevel": "medium" }
```

</process>
