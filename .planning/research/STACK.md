# Stack Research: Brownfield Codebase Analysis Mode

**Domain:** AI-driven codebase analysis within a Claude Code prompt-engineering framework
**Researched:** 2026-02-08
**Confidence:** HIGH (core approaches) / MEDIUM (specific patterns for parallel agent execution)

---

## Executive Context

GSD-Opus46 needs to add intelligent brownfield analysis that runs automatically when existing code is detected. This is NOT a traditional static analysis tool — it is a **prompt-engineered analysis pipeline** that leverages Claude Code's native file access tools (Read, Grep, Glob, Bash) through coordinated markdown-defined agents.

The "stack" here is not libraries to install. It is **analysis approaches, prompt patterns, and agent coordination strategies** that work within the existing commands-workflows-agents 3-layer architecture.

---

## Recommended Approach: Four-Dimension Parallel Analysis

### Core Strategy

| Approach | Purpose | Why Recommended | Confidence |
|----------|---------|-----------------|------------|
| **Tool-based heuristic detection** | Identify code presence, languages, frameworks | Fast, deterministic, no LLM tokens needed for detection phase. Glob/Bash patterns are 100% reliable for file existence checks. | HIGH |
| **Parallel isolated agents** (existing pattern) | Analyze 4 dimensions simultaneously | Already proven by `map-codebase` workflow. Each agent gets isolated context, writes directly to `.planning/`, no cross-contamination. Token-efficient because agents don't pass findings back through orchestrator. | HIGH |
| **Template-guided output** | Structure agent findings into consistent documents | Existing template system ensures every agent produces comparable output. Templates act as implicit prompts — their structure tells the agent what to look for. | HIGH |
| **Signal-based analysis over exhaustive scanning** | Focus on high-signal indicators rather than reading every file | An LLM cannot meaningfully analyze a 500-file codebase line by line. Instead, identify key signal files (entry points, configs, package manifests, test directories) and infer the whole from the parts. | HIGH |
| **Layered confidence scoring** | Tag every finding with evidence quality | Prevents hallucination from propagating into planning phases. Downstream consumers (planner, executor) can weight recommendations appropriately. | MEDIUM |

### Four Analysis Dimensions

Each dimension maps to a specific concern and uses specific tool strategies:

| Dimension | What It Answers | Primary Tools | Signal Files | Output |
|-----------|----------------|---------------|--------------|--------|
| **1. Structure/Architecture** | "How is this codebase organized?" | Glob (directory tree), Read (entry points, imports) | `index.*`, `main.*`, `app.*`, `server.*`, directory layout | ARCHITECTURE.md, STRUCTURE.md |
| **2. Tech Stack** | "What technologies run this code?" | Bash (package manifests), Grep (import patterns) | `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, config files | STACK.md, INTEGRATIONS.md |
| **3. Problems/Tech Debt** | "What's broken or fragile?" | Grep (TODO/FIXME/HACK), Bash (file sizes, complexity heuristics) | Large files, TODO comments, empty stubs, test gaps | CONCERNS.md |
| **4. Test State** | "How well tested is this?" | Glob (test file discovery), Grep (test patterns), Bash (coverage commands) | `*.test.*`, `*.spec.*`, test config files, coverage reports | TESTING.md, CONVENTIONS.md |

---

## Analysis Techniques That Work With Claude Code's Tool Access

### Tier 1: Deterministic Heuristics (No LLM Required)

These should run first, as Bash commands in the orchestrator, before spawning any agents.

**Code existence detection (already partially implemented in `new-project.md`):**

```bash
# Language detection by file extension
CODE_FILES=$(find . -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" \
  -o -name "*.rs" -o -name "*.swift" -o -name "*.java" -o -name "*.rb" \
  -o -name "*.php" -o -name "*.c" -o -name "*.cpp" -o -name "*.cs" \
  2>/dev/null | grep -v node_modules | grep -v .git | grep -v vendor | head -50)

# Package manager detection
HAS_PACKAGE=$(ls package.json requirements.txt Cargo.toml go.mod \
  pyproject.toml Gemfile composer.json *.csproj 2>/dev/null | head -1)

# Framework detection from config files
HAS_NEXT=$([ -f next.config.js ] || [ -f next.config.mjs ] || [ -f next.config.ts ] && echo "nextjs")
HAS_VITE=$([ -f vite.config.ts ] || [ -f vite.config.js ] && echo "vite")
HAS_DJANGO=$([ -f manage.py ] && grep -q django requirements.txt 2>/dev/null && echo "django")

# Monorepo detection
HAS_MONOREPO=$(ls pnpm-workspace.yaml lerna.json nx.json turbo.json 2>/dev/null | head -1)

# Test infrastructure detection
HAS_TESTS=$(find . -name "*.test.*" -o -name "*.spec.*" -o -name "__tests__" \
  2>/dev/null | grep -v node_modules | head -1)
TEST_COUNT=$(find . -name "*.test.*" -o -name "*.spec.*" \
  2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')

# Codebase size estimation (for effort calibration)
TOTAL_CODE_FILES=$(find . -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" \
  2>/dev/null | grep -v node_modules | grep -v .git | wc -l | tr -d ' ')
```

**Why deterministic first:** These checks cost zero LLM tokens and provide the agent-spawning orchestrator with enough context to craft targeted prompts. An agent told "This is a Next.js 14 app with 47 TypeScript files and 12 test files" will analyze far more effectively than one told "Analyze this codebase."

**Confidence: HIGH** — This is the existing pattern in `new-project.md` Phase 1, just expanded.

### Tier 2: Targeted File Reading (Agent-Level)

Each agent reads specific "signal files" rather than scanning everything.

**Structure/Architecture agent strategy:**

| Signal | What to Read | What It Reveals |
|--------|-------------|-----------------|
| Entry points | `src/index.*`, `src/main.*`, `app/page.*`, `server.*` | Application type, bootstrap flow |
| Import graph (top 20 most-imported files) | `grep -rh "^import\|^from" src/ \| sort \| uniq -c \| sort -rn \| head -20` | Core modules, dependency hotspots |
| Directory depth | `find . -type d \| awk -F/ '{print NF-1}' \| sort -rn \| head -5` | Nesting complexity |
| Route/command definitions | Framework-specific: `app/` for Next.js, `routes/` for Express, `commands/` for CLI | Public API surface |

**Tech Stack agent strategy:**

| Signal | What to Read | What It Reveals |
|--------|-------------|-----------------|
| Package manifest | `package.json` (dependencies section) | Direct dependencies |
| Lock file existence | `ls package-lock.json yarn.lock pnpm-lock.yaml` | Package manager choice |
| TypeScript config | `tsconfig.json` (target, module, paths) | TS strictness, module system |
| CI config | `.github/workflows/*.yml`, `Dockerfile` | Build/deploy pipeline |
| Runtime version | `.nvmrc`, `.python-version`, `rust-toolchain.toml` | Runtime constraints |

**Problems/Tech Debt agent strategy:**

| Signal | What to Read | What It Reveals |
|--------|-------------|-----------------|
| Comment markers | `grep -rn "TODO\|FIXME\|HACK\|XXX\|WORKAROUND" src/` | Known debt |
| Large files (>300 lines) | `find src/ -name "*.ts" \| xargs wc -l \| sort -rn \| head -10` | Complexity hotspots |
| Duplicated patterns | `grep -rh "catch.*console\|catch.*{}" src/ \| head -20` | Swallowed errors |
| Dependency age | `npm outdated 2>/dev/null \| head -20` | Stale dependencies |
| Any-type usage | `grep -rn ": any\|as any" src/ --include="*.ts" \| wc -l` | Type safety gaps |
| Dead code indicators | `grep -rn "// eslint-disable\|@ts-ignore\|@ts-expect-error" src/` | Suppressed warnings |

**Test State agent strategy:**

| Signal | What to Read | What It Reveals |
|--------|-------------|-----------------|
| Test file count vs source count | `find . -name "*.test.*" \| wc -l` vs `find src/ -name "*.ts" \| wc -l` | Coverage ratio |
| Test config | `jest.config.*`, `vitest.config.*` | Test framework and settings |
| Sample test files (3-5) | First few `.test.*` files | Test patterns, assertion style |
| Coverage config | `"coverage"` in config files | Whether coverage is tracked |
| CI test commands | `"test"` in `package.json` scripts | How tests are run |

**Confidence: HIGH** — This is exactly what the existing `gsd-codebase-mapper` agent does. We are extending the same proven pattern.

### Tier 3: LLM-Powered Inference (Agent Interpretation)

After reading signal files, each agent applies LLM reasoning to infer higher-level properties.

**Architecture inference from import patterns:**
- Circular import detection (A imports B imports A) signals tight coupling
- Single-direction imports (all flows toward `index`) signals clean layering
- "God module" detection (one file imported by >50% of files) signals centralization risk

**Tech debt severity estimation:**
- TODO count alone is not tech debt measurement
- Agent should classify: (1) acknowledged debt (TODO with context), (2) silent debt (patterns that look fragile), (3) missing capability (no error handling, no logging)
- Severity = Impact * Likelihood-of-breakage, estimated from file centrality and test coverage

**Test quality assessment (beyond count):**
- Ratio of assertion lines to setup lines (high setup = fragile tests)
- Test file naming match to source files (1:1 = good coverage targeting)
- Presence of mocking patterns (over-mocking = tests don't test real behavior)
- Presence of integration/E2E tests vs only unit tests

**Confidence: MEDIUM** — LLM inference is powerful but can hallucinate patterns. The template-guided output helps constrain this.

---

## Agent Coordination: How to Structure Parallel Execution

### Orchestrator Responsibilities (the brownfield workflow)

The orchestrator (workflow markdown) should:

1. **Run Tier 1 heuristics** in Bash to gather deterministic context
2. **Craft targeted prompts** using heuristic results (don't send generic "analyze this")
3. **Spawn 4 agents** via `Task()` with `run_in_background: true`
4. **Wait and verify** all 7 output documents exist
5. **Synthesize summary** from agent outputs (read first 10-20 lines of each document)
6. **Present to user** with routing options (fix vs improve)

### Agent Prompt Design

**Critical pattern:** Each agent prompt should include:

```
You are analyzing a [LANGUAGE] [FRAMEWORK] codebase with approximately [N] files.

Focus: [dimension]

Key context from initial scan:
- Package manager: [detected]
- Framework: [detected]
- Test files found: [count]
- [Other heuristic findings]

Explore using the strategies below, then write your document(s) to .planning/codebase/.

Strategy:
1. Read [specific signal files]
2. Run [specific grep/glob patterns]
3. Infer [specific properties]
4. Write findings using template
```

**Why this matters:** A prompt saying "analyze codebase tech stack" produces generic output. A prompt saying "This is a Next.js 14 app using TypeScript. Read package.json, tsconfig.json, and next.config.ts. Document the stack." produces precise, actionable output.

**Confidence: HIGH** — The existing `map-codebase` workflow already demonstrates this pattern with the 4 mapper agents.

### Context Budget Management

| Agent | Estimated Input Tokens | Estimated Output Tokens | Rationale |
|-------|----------------------|------------------------|-----------|
| Structure/Architecture | ~15K (directory tree + 5-8 file reads) | ~3-5K (2 documents) | Needs to read entry points and trace imports |
| Tech Stack | ~8K (manifests + configs) | ~2-3K (2 documents) | Package manifests are dense but small |
| Problems/Tech Debt | ~20K (grep results + file samples) | ~4-6K (1 document) | Grep results can be verbose; agent must prioritize |
| Test State | ~12K (test samples + config) | ~3-4K (2 documents) | Needs to read actual test files to assess patterns |

**Total estimated: ~55-75K input tokens across 4 agents.** This is well within Claude Code's parallel agent budget and comparable to the existing `map-codebase` workflow.

---

## What NOT to Do When Analyzing Codebases with AI

### Anti-Pattern 1: Exhaustive File Reading

**What goes wrong:** Agent tries to read every file to "understand everything."
**Why it fails:** Context window fills with low-signal code. Agent loses ability to synthesize.
**Prevention:** Use signal-based analysis. Read 10-15 key files, not 100.
**Confidence: HIGH**

### Anti-Pattern 2: Unstructured Output

**What goes wrong:** Agent returns free-form prose about findings.
**Why it fails:** Downstream consumers (planner, executor) can't parse it. Inconsistent between runs.
**Prevention:** Template-guided output. Agent fills in structured markdown, not creative writing.
**Confidence: HIGH**

### Anti-Pattern 3: Passing Analysis Results Through Orchestrator

**What goes wrong:** Agents return findings to orchestrator, which then writes documents.
**Why it fails:** Context explosion. Orchestrator's context fills with 4 agents' worth of findings. This is the exact problem the existing `map-codebase` workflow already solved.
**Prevention:** Agents write directly to `.planning/codebase/`. Orchestrator only receives confirmation.
**Confidence: HIGH** — This is already the proven GSD pattern.

### Anti-Pattern 4: Generic Prompts

**What goes wrong:** Agent spawned with "Analyze the codebase for problems."
**Why it fails:** Without knowing it's a Python Django app vs a Rust CLI, the agent wastes tokens on irrelevant patterns. It may look for `package.json` in a Go project.
**Prevention:** Tier 1 heuristics feed into agent prompts. Each agent knows the language, framework, and approximate size before it starts.
**Confidence: HIGH**

### Anti-Pattern 5: Treating Analysis as Compilation

**What goes wrong:** Trying to build/run/compile the code to understand it.
**Why it fails:** Build environments may not be set up. Dependencies may not be installed. Build failures are noisy and uninformative for understanding structure.
**Prevention:** Static analysis only. Read files, don't execute them. If `npm test` fails, that's a finding ("tests don't pass"), not a blocker for analysis.
**Confidence: HIGH**

### Anti-Pattern 6: Analyzing Generated/Vendor Code

**What goes wrong:** Agent spends tokens analyzing `node_modules/`, `vendor/`, build output, or generated code.
**Why it fails:** These are not the developer's code. Findings about them are not actionable.
**Prevention:** Always exclude: `node_modules/`, `.git/`, `vendor/`, `dist/`, `build/`, `.next/`, `__pycache__/`, `target/` (Rust), `bin/` (Go).
**Confidence: HIGH**

### Anti-Pattern 7: Confidence Theater

**What goes wrong:** Agent states all findings as HIGH confidence.
**Why it fails:** Planner trusts a guess as much as a verified fact. Wrong architectural assumptions propagate into wrong plans.
**Prevention:** Require explicit confidence tagging. Agent must distinguish between "I read this in package.json" (HIGH) and "This looks like it might be a service layer pattern" (MEDIUM).
**Confidence: MEDIUM** — This is the hardest anti-pattern to prevent because LLMs naturally express confidence.

---

## Synthesis Approach: From Analysis to Routing

After the 4 parallel agents complete, the orchestrator needs to:

### Step 1: Generate Summary

Read the first section of each `.planning/codebase/` document. Produce a compact summary:

```
Your codebase at a glance:

Architecture: [from ARCHITECTURE.md - pattern overview]
Stack: [from STACK.md - primary language + framework]
Health: [from CONCERNS.md - count of issues by severity]
Testing: [from TESTING.md - coverage estimate and framework]
Size: [N] source files, [M] test files
```

### Step 2: Route to Workflow

Present the user with a purpose-driven choice:

```
Based on analysis, what's your goal?

1. Fix something — Address bugs, tech debt, or broken functionality
   → Routes to: debug/fix-focused planning with CONCERNS.md context

2. Improve/extend — Add features or enhance existing ones
   → Routes to: feature-focused planning with full codebase context

3. Refactor — Restructure without changing behavior
   → Routes to: refactoring-focused planning with ARCHITECTURE.md + CONCERNS.md context
```

Each route loads different codebase documents into the planning phase, keeping context focused.

**Confidence: MEDIUM** — The routing logic is novel for GSD. The 3-option structure is a recommendation based on the PROJECT.md's stated goal of "fix vs improve" routing, expanded to include refactoring as a distinct mode.

---

## Integration With Existing Architecture

### How This Fits the 3-Layer Model

```
commands/gsd/new-project.md     ← Modified: adds brownfield analysis phase
    │
    ├─→ (Tier 1 heuristics run inline in command)
    │
    ├─→ get-shit-done/workflows/brownfield-analysis.md  ← NEW workflow
    │       │
    │       ├─→ agents/gsd-codebase-mapper.md (tech)     ← EXISTING agent
    │       ├─→ agents/gsd-codebase-mapper.md (arch)     ← EXISTING agent
    │       ├─→ agents/gsd-codebase-mapper.md (quality)  ← EXISTING agent
    │       └─→ agents/gsd-codebase-mapper.md (concerns) ← EXISTING agent
    │
    ├─→ Summary + User routing (inline in workflow)
    │
    └─→ Continue to existing phases (questioning, research, etc.)
```

### What's New vs What's Reused

| Component | Status | Notes |
|-----------|--------|-------|
| `gsd-codebase-mapper` agent | **REUSE** | Already handles all 4 focus areas with templates |
| `map-codebase` workflow | **ADAPT** | Core logic reusable; needs inline integration variant |
| Brownfield detection heuristics | **EXTEND** | Existing detection in `new-project.md` needs expansion |
| Codebase templates (7 files) | **REUSE** | Already define output structure |
| Summary synthesis | **NEW** | Compact summary generation from 7 documents |
| Purpose routing (fix/improve/refactor) | **NEW** | Decision point after analysis |
| brownfield-analysis workflow | **NEW** | Orchestrates inline analysis within new-project flow |

### Key Architectural Decision

**Inline analysis vs separate command:**

The existing `map-codebase` is a standalone command. For the brownfield flow, the analysis should be **inlined into new-project** rather than calling `map-codebase` as a separate step. Reason: the new-project flow needs the analysis results immediately for routing. Exiting to `map-codebase` and re-entering `new-project` loses orchestration context.

However, the underlying agent spawning logic can be extracted from the `map-codebase` workflow into a shared workflow that both `new-project` (inline) and `map-codebase` (standalone) can reference.

**Confidence: HIGH** — This follows the existing pattern where `execute-phase` workflow is referenced by the `execute-phase` command but contains reusable logic.

---

## Alternatives Considered

| Recommended | Alternative | Why Not Alternative |
|-------------|-------------|---------------------|
| Signal-based analysis (read key files) | Exhaustive file reading | Context window limits make exhaustive reading impractical for codebases >50 files |
| 4 parallel agents | Single serial agent | Serial analysis takes 4x longer and risks context contamination between dimensions |
| Template-guided output | Free-form analysis | Templates ensure consistency and downstream parsability |
| Inline brownfield analysis in new-project | Separate brownfield command | Breaks flow; user has to re-enter new-project after analysis |
| 3-option routing (fix/improve/refactor) | 2-option routing (fix/improve) | Refactoring is distinct from feature improvement and needs different planning context |
| Tier 1 heuristics before agent spawn | Let agents self-discover everything | Wastes tokens on basic detection that Bash can do deterministically |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| AST parsing tools (tree-sitter, babel) | Requires installation, build setup, adds complexity to a markdown-based framework | Grep-based pattern matching for import analysis; sufficient for architecture inference |
| Code complexity calculators (cyclomatic complexity tools) | Require language-specific tooling, hard to generalize | File size + nesting depth as proxy; "large file = likely complex" heuristic |
| Running the test suite during analysis | May fail due to missing deps/env; slow; not informative for understanding | Read test files and config; count test files; check for coverage config |
| Dependency graph visualization tools | External tool dependency; output format incompatible with markdown agents | Grep import patterns; manually trace top-level dependencies |
| Traditional linters (ESLint, Pylint) as analysis tools | Noisy output; language-specific; findings are too granular for architecture-level analysis | Agent-level pattern recognition from reading sample files |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Agent hallucinates architecture patterns | Medium | High (wrong plans downstream) | Template structure constrains output; confidence tagging flags uncertain findings |
| Analysis takes too long (token budget) | Low | Medium (user waits) | Tier 1 heuristics pre-filter; agents read signal files, not everything |
| Agents produce inconsistent output | Low | Medium (confusing summary) | Templates enforce consistency; same agent definition for all 4 dimensions |
| Large monorepo overwhelms agents | Medium | High (incomplete analysis) | Codebase size estimation in Tier 1; for >200 files, add focus-area parameter |
| Analysis findings not used by downstream phases | Low | High (wasted effort) | Documents are already consumed by existing plan-phase and execute-phase workflows |

---

## Sources

- **GSD-Opus46 existing implementation** — `commands/gsd/map-codebase.md`, `get-shit-done/workflows/map-codebase.md`, `agents/gsd-codebase-mapper.md` demonstrate the proven parallel agent analysis pattern
- **GSD codebase templates** — 7 templates in `get-shit-done/templates/codebase/` define output structure
- **Existing brownfield detection** — `commands/gsd/new-project.md` Phase 1 shows current detection heuristics
- **Domain expertise** — AI-assisted code analysis patterns from static analysis research, code intelligence systems (GitHub Copilot, Sourcegraph, CodeScene), and LLM-based code understanding literature
- **Note:** WebSearch was unavailable during this research session. Recommendations are based on established patterns in the existing codebase and domain knowledge. Confidence levels are tagged accordingly.

---
*Stack research for: Brownfield codebase analysis mode*
*Researched: 2026-02-08*
*External verification: LIMITED — WebSearch unavailable; recommendations grounded in existing GSD patterns and domain expertise*
