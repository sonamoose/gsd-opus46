# Brownfield Questioning Guide

Purpose-specific questioning patterns for brownfield codebase workflows. Used by `brownfield-flow.md` Step 7 (purpose_questioning) to guide adaptive conversation after the user selects their purpose.

**Key difference from greenfield questioning:**
- Greenfield: "What do you want to build?" (imagined state → project definition)
- Brownfield: "What do you want to change?" (observed state → desired state)

The analysis is your anchor. Every question should reference specific findings from brownfield-analysis.md.

---

## Philosophy

**You are a diagnostic partner, not an interviewer.**

The analysis already identified what IS. Your job is to help the user articulate what they want to DO about it. Start from observed state, navigate toward action.

**Follow the thread:** Each answer informs the next question. Do NOT walk through all questions regardless of answers.

**These question flows are REFERENCES** (available questions by category), **not SCRIPTS** (mandatory sequences). Skip irrelevant questions. Dive deeper where the user shows energy. 2-3 questions may be enough if the user has clear priorities.

---

## Fix Mode

Start from concerns. Help user prioritize and provide reproduction context.

**Context anchor:** Top Concerns from brownfield-analysis.md
**Goal:** Narrow scope to specific, actionable fixes

**Question flow:**

### 1. Scope Selection
Present top concerns from analysis as selectable options.
Use AskUserQuestion (multiSelect: true):
  header: "Focus"
  question: "The analysis found these concerns. Which do you want to address?"
  options: [top 3-5 concerns from analysis, each with severity tag]

If user selects none: Ask what issue they want to address instead (freeform).
If user selects all: Note that the roadmap will prioritize by severity.

### 2. Concern Validation (for each selected concern)
For each selected concern, ask 1-2 adaptive follow-ups:

a. Observation check:
   "Have you seen [concern description] in practice?"
   - "Yes — here's what happens: [gather reproduction details]"
   - "Yes, but I can't reliably reproduce it"
   - "No — the analysis flagged it but I haven't noticed it"

   If yes with details: Capture reproduction steps. These feed into debug bridging (Step 8).
   If no: Note as analysis-only finding. Lower priority unless severity is critical.

b. Impact from user perspective (may differ from analysis severity):
   "How does this affect you?"
   - "Blocks users / breaks functionality"
   - "Degrades experience but workarounds exist"
   - "Slows development / causes confusion"
   - "Minor annoyance"

### 3. Priority Confirmation
After validating all selected concerns:
  "Based on your input, here's the priority order: [re-ranked list].
   Does this look right, or should anything move up/down?"

### 4. Scope Decision
  "Fix root causes or patch symptoms first?"
  - "Root cause — proper fix even if it takes longer"
  - "Quick patch — stop the bleeding, fix properly later"
  - "Mix — root cause for critical, patch for others"

### 5. Decision Gate
  "Ready to create a fix roadmap based on these priorities?"
  - "Yes, create roadmap"
  - "I want to debug the top issue first" (routes to Step 8: bridge_to_debug)
  - "Let me add more context"

---

## Improve Mode

Start from user's vision. Constrain by analysis findings.

**Context anchor:** Architecture + Stack from brownfield-analysis.md
**Goal:** Define improvements that fit existing architecture

**Question flow:**

### 1. Vision
  "What do you want this codebase to do that it doesn't do now?"
  Freeform response. Then follow-up probing (like greenfield questioning):
  - "Walk me through using that."
  - "What does that actually look like?"
  - "Who benefits from this?"

### 2. Architecture Fit
  Present analysis architecture context:
  "Your codebase uses [architecture pattern from analysis]. Your improvement would
  [extend existing patterns / require new patterns / need evaluation]."

  Ask: "Does this fit within the current architecture, or are you open to changes?"

### 3. Affected Areas
  Cross-reference improvement scope with analysis findings:
  "This would touch [areas from analysis]. The analysis noted these concerns in those areas: [relevant concerns]."

  Ask: "Are you aware of these? Should we address them as part of the improvement?"

### 4. Constraints
  Adapted from analysis context:
  - "Test coverage in affected areas is [N% from analysis]. Maintain or improve?"
  - "Any performance targets for the new capability?"
  - "Timeline or deadline considerations?"

  Skip constraints that don't apply. Don't ask about test coverage if the codebase has no tests.

### 5. Decision Gate
  "Ready to create an improvement roadmap?"
  - "Yes, create roadmap"
  - "Let me refine the scope"

---

## Refactor Mode

Start from pain points. Navigate toward target architecture.

**Context anchor:** Concerns + Conventions from brownfield-analysis.md
**Goal:** Define target state and safe transformation path

**Question flow:**

### 1. Pain Point Selection
  Present moderate/minor concerns + structural findings as pain point options.
  Use AskUserQuestion (multiSelect: true):
    header: "Pain Points"
    question: "Which areas cause the most development pain?"
    options: [concerns + structural issues from analysis]

  Also ask: "Any pain points not captured in the analysis?"

### 2. Target State
  For each major pain point area, ask about the desired end state:

  a. Architecture:
     "Keep current [pattern from analysis] or move toward something else?"
     If moving: "What pattern? [suggest based on codebase size and concerns]"

  b. Conventions:
     "The analysis found [convention patterns]. Standardize on these or introduce new ones?"

  c. Testing:
     "Current test coverage is [from analysis]. What's your target?"
     Skip if user hasn't mentioned testing as a pain point.

### 3. Risk Tolerance
  "How much disruption is acceptable?"
  - "Small, safe changes — incremental improvement"
  - "Moderate restructuring — some temporary breakage OK"
  - "Significant rewrite — willing to rebuild sections"

### 4. Strategy
  Based on risk tolerance, confirm approach:
  - Low risk: "We'll focus on quick wins — naming, conventions, small patterns"
  - Moderate: "We'll restructure modules and clean up architecture"
  - High risk: "We'll plan a phased rewrite of the most painful areas"

### 5. Decision Gate
  "Ready to create a refactoring roadmap?"
  - "Yes, create roadmap"
  - "Let me reconsider the scope"

---

## Other / Custom Purpose

Minimal thread for goals that don't fit fix/improve/refactor categories.

**Context anchor:** Full brownfield-analysis.md
**Goal:** Understand user's goal and connect to analysis findings

**Question flow:**

### 1. Goal
  "What's your goal for this codebase?"
  Freeform response.

### 2. Analysis Relevance
  "How does the existing codebase relate to this goal?"
  - "It's the foundation I'm building on"
  - "It needs changes to support my goal"
  - "I'm trying to understand it better"
  - "Other — let me explain"

### 3. Relevant Findings
  "Which findings from the analysis are relevant to your goal?"
  Present top findings, let user select or describe.

### 4. Decision Gate
  "Ready to create a roadmap for this goal?"
  - "Yes, create roadmap"
  - "Let me explain more"

---

## Anti-Patterns

- **Checklist walking** — Going through all questions regardless of what the user said. If they selected one critical concern, don't ask about conventions and testing targets.
- **Ignoring analysis context** — Asking "What's wrong?" when the analysis already identified 5 concerns. Start from findings, not from zero.
- **Generic questions** — "What do you want to do?" is bad. "The analysis found 2 critical issues in your auth system. Want to fix those first?" is good.
- **Premature roadmapping** — Jumping to roadmap creation before understanding priorities and constraints. The questioning phase exists to gather context the analysis couldn't.
- **Over-questioning** — If user has clear priorities and just wants to proceed, let them. 2-3 questions may be enough. Don't pad to fill a template.
- **Scope creep across modes** — Fix mode should not drift into refactoring discussions. If the user starts talking about restructuring, suggest switching to refactor mode.
