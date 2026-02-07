# Research Summary: GSD-Opus46 Brownfield Mode Branching

**Domain:** AI-driven CLI workflow tool with intelligent brownfield codebase analysis and mode branching
**Researched:** 2026-02-08
**Overall confidence:** HIGH (stack/architecture) / MEDIUM (pitfall mitigations, external validation unavailable)

## Executive Summary

GSD-Opus46's brownfield mode branching project adds intelligent detection and analysis of existing codebases to the `/gsd:new-project` command, enabling automatic routing into purpose-specific workflows (fix bugs, add features, or refactor). The research across four dimensions confirms this is architecturally sound: the existing 3-layer commands-workflows-agents pattern already contains most of the infrastructure needed, with the `gsd-codebase-mapper` agent and `map-codebase` workflow providing a proven foundation for parallel codebase analysis. The project requires 3 new components (brownfield-analyzer agent, brownfield-flow workflow, brownfield-summary template) while reusing 7 existing ones unchanged.

The recommended approach uses a four-dimension parallel analysis pipeline (structure, stack, problems, tests) driven by signal-based file reading rather than exhaustive scanning. Tier 1 deterministic heuristics (Bash file detection) feed into Tier 2 targeted agent exploration (reading 10-15 key "signal files" per dimension), which feeds into Tier 3 LLM inference (pattern recognition and severity assessment). This layered approach keeps token budgets manageable (~55-75K input tokens across 4 agents) while producing comprehensive output in 7 structured documents. The feature landscape identifies 6 table stakes, 7 differentiators, and 7 anti-features, with a clear MVP of 7 features (6 table stakes + intent-aware questioning) that delivers end-to-end brownfield value.

The most significant risks center on analysis quality, not architecture. Pitfall research catalogued 12 pitfalls (5 critical, 5 moderate, 2 minor), with the top concerns being: (1) agent hallucination reporting nonexistent issues that poison downstream workflows, (2) brittle mode detection thresholds that false-positive on scaffolded projects, and (3) context loss where analysis findings fail to reach executor agents. All three have concrete mitigations -- confidence-gated findings, multi-signal detection, and mandatory codebase context loading -- but they require deliberate design attention during implementation.

The architecture research confirms that mode branching belongs inside `new-project.md` as conditional workflow delegation, not as a separate command. The brownfield path diverges at Phase 2 (detection and analysis) through Phase 4 (purpose-aware questioning and PROJECT.md creation), then converges with the greenfield path at Phase 5 (config, research, requirements, roadmap). This design preserves the existing greenfield flow with zero behavioral regression while adding brownfield intelligence through a clean Analysis-Decision-Execution pipeline.

## Key Findings

**Stack:** AI-driven signal-based codebase analysis using 3-tier approach (deterministic heuristics, targeted agent file reading, LLM inference) through Claude Code's native tools -- no external dependencies required.

**Architecture:** 3-layer brownfield flow with Analysis-Decision-Execution pipeline: 3 new components (brownfield-analyzer agent, brownfield-flow workflow, brownfield-summary template) + 7 reused components (mapper agent, map-codebase workflow, planner, executor, researcher, templates, questioning reference).

**Critical pitfall:** Agent hallucination -- reporting nonexistent issues from pattern-matching against training data expectations (e.g., flagging test fixtures as "empty stubs") poisons downstream planning/execution and erodes user trust faster than any other failure mode.

## Implications for Roadmap

Based on research, the implementation should follow a 4-phase build order with clear dependency gates:

**Phase 1 -- Foundation (no dependencies):** Create the brownfield-summary template and brownfield-analyzer agent definition. These are leaf nodes that can be built and tested in isolation. Simultaneously, harden mode detection heuristics in `new-project.md` Phase 1 with multi-signal detection, expanded language coverage, and generated/vendor directory exclusions. Detection accuracy is the gate for everything downstream.

**Phase 2 -- Workflow (depends on Phase 1):** Create the brownfield-flow workflow that orchestrates analysis synthesis, user presentation, purpose selection, and purpose-aware questioning. This is where the Analysis-Decision-Execution pipeline takes shape. The fix-vs-improve fork should use a "shared core with late forking" strategy (Pitfall 7 mitigation) rather than two parallel workflows.

**Phase 3 -- Command Integration (depends on Phase 2):** Modify `new-project.md` to auto-detect brownfield, auto-invoke map-codebase when needed, delegate to brownfield-flow, and write brownfield-enriched PROJECT.md. This is the integration phase where the user-facing flow comes together. Greenfield regression testing is critical here (TS-6).

**Phase 4 -- State Integration (depends on Phase 3):** Ensure brownfield context propagates through STATE.md to downstream agents (planner, executor). Add staleness detection for codebase documents. Validate end-to-end context flow from analysis through execution.

**Rationale:** This order was derived from the architecture research's build dependency graph and prioritizes detection accuracy (the trust foundation) before analysis quality (the value layer) before integration (the user experience).

## Confidence Assessment

| Research Area | Confidence | Rationale |
|---------------|------------|-----------|
| Stack approach (signal-based analysis) | HIGH | Proven by existing `map-codebase` workflow; extends established patterns |
| Architecture (3-layer integration) | HIGH | Direct analysis of existing codebase; follows established delegation model |
| Feature prioritization (MVP scope) | HIGH | Grounded in existing component availability and clear dependency chain |
| Pitfall identification | MEDIUM | Based on codebase analysis and domain expertise; no external validation (WebSearch unavailable) |
| Pitfall mitigations | MEDIUM | Logical mitigations but untested; some (anti-hallucination guardrails) are inherently difficult to guarantee |
| Token budget estimates | MEDIUM | Extrapolated from existing mapper agent usage; actual usage will vary by codebase size |
| Competitor analysis | MEDIUM | Based on domain knowledge of tool landscape; not externally verified |
| Scaling to large codebases (>500 files) | LOW | Progressive sampling strategy is theoretical; needs empirical validation |

## Gaps to Address

1. **External validation unavailable.** WebSearch was unavailable during research. Community experience with AI-powered codebase analysis tools, failure modes of similar systems (CodeScene, Sourcegraph AI, GitHub Copilot workspace), and best practices for LLM-based code understanding should be researched when connectivity is available.

2. **Large codebase behavior unquantified.** The progressive sampling strategy for codebases >500 files is a design recommendation without empirical data. Needs benchmarking against real codebases of varying sizes (50, 200, 500, 2000+ files) to validate token budgets and analysis quality.

3. **Anti-hallucination effectiveness unknown.** Confidence-gated findings and template-guided output are proposed mitigations for agent hallucination, but their effectiveness cannot be measured until agents are built and tested against real codebases with known issues.

4. **Multi-language coverage depth.** Analysis exploration strategies are heavily JS/TS-centric. Python, Go, Rust, Java/Kotlin exploration strategies are outlined at a high level but need language-specific signal file identification and testing.

5. **User experience for analysis presentation.** The "executive summary first, progressive disclosure" recommendation for presenting analysis to users is untested. The right level of detail, summary length, and actionable framing needs user feedback.

6. **Fix-as-milestone vs fix-as-mode.** Pitfall 7 recommends treating bug fixes as a milestone within the standard flow rather than a separate mode. This architectural decision has significant downstream implications and needs explicit design discussion before implementation.

---
*Research summary synthesized from: STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md*
*Synthesized: 2026-02-08*
