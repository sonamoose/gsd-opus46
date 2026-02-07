# Effort Level Profiles

Effort level controls Claude's reasoning depth per agent. Set via `/model` slider or `CLAUDE_CODE_EFFORT_LEVEL` environment variable.

## Profile Definitions

| Agent | Recommended Effort | Rationale |
|-------|-------------------|-----------|
| gsd-planner | high | Architecture decisions, goal decomposition, task design |
| gsd-plan-checker | high | Multi-dimensional plan verification, coverage analysis |
| gsd-debugger | high | Scientific method investigation, hypothesis testing |
| gsd-research-synthesizer | high | Cross-referencing multiple research outputs |
| gsd-codebase-mapper | medium | Structured exploration with template output |
| gsd-roadmapper | medium | Requirement mapping, phase breakdown |
| gsd-executor | medium | Plan execution with atomic commits |
| gsd-verifier | medium | Goal-backward codebase verification |
| gsd-project-researcher | low | Focused domain research, web search |
| gsd-phase-researcher | low | Phase-specific research producing RESEARCH.md |
| gsd-integration-checker | low | Checklist-based cross-phase verification |

## Level Characteristics

**high** — Deep reasoning, thorough analysis
- Complex decision-making and trade-off evaluation
- Multi-step reasoning chains
- Suitable for: planning, debugging, synthesis
- Use when: architecture decisions, critical path work

**medium** — Balanced reasoning, structured execution
- Follows explicit instructions with good judgment
- Handles moderate complexity reliably
- Suitable for: code execution, verification, mapping
- Use when: normal development, structured tasks

**low** — Fast, focused, efficient
- Simple pattern matching and information gathering
- Template-driven output
- Suitable for: research, checklist verification
- Use when: high-volume tasks, information retrieval

## How to Set Effort Level

**Per session:**
Use `/model` command, then adjust with left/right arrow keys.

**Per environment:**
```bash
export CLAUDE_CODE_EFFORT_LEVEL=high  # low | medium | high
```

**Per project (settings.json):**
```json
{
  "effortLevel": "medium"
}
```

## Design Rationale

**Why high for gsd-planner?**
Planning involves architecture decisions, goal decomposition, and task design. Deeper reasoning produces better task breakdown and dependency analysis.

**Why medium for gsd-executor?**
Executors follow explicit PLAN.md instructions. The plan already contains the reasoning; execution is implementation.

**Why low for researchers?**
Research is primarily information gathering. Speed and breadth matter more than reasoning depth.
