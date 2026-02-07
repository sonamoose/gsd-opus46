# Phase 1: Foundation - Research

**Researched:** 2026-02-08
**Domain:** Brownfield detection logic, analysis template design, agent definition authoring (prompt-engineering framework, not traditional software)
**Confidence:** HIGH

## Summary

This research investigates how to implement Phase 1: Foundation (template + agent + detection logic) for the GSD-Opus46 brownfield analysis feature. The phase creates three artifacts: a `brownfield-summary.md` template that structures the synthesis of 7 codebase documents into a user-facing summary, a `gsd-brownfield-analyzer.md` agent that reads those 7 documents and writes the synthesis, and a mode detection logic module that uses multi-signal heuristics to distinguish brownfield from greenfield projects.

The existing codebase provides strong precedent for all three artifacts. The `gsd-codebase-mapper.md` agent is the proven model for agent definition structure. The 7 templates in `get-shit-done/templates/codebase/` define the input format the analyzer will consume. The current `new-project.md` Phase 1 already has basic brownfield detection that needs expansion with multi-signal scoring and scaffolding graceful downgrade.

**Primary recommendation:** Follow the existing agent/template patterns exactly. The brownfield-summary template should have 7 sections mapping 1:1 to the 7 codebase documents. The analyzer agent should follow gsd-codebase-mapper's structure (role, process steps, templates, critical rules, success criteria). Detection logic should use a scoring system with 4 signal categories (code files, package manifests, git history, directory structure) rather than binary file-existence checks.

## Standard Stack

This phase operates entirely within the GSD prompt-engineering framework. There are no external libraries or packages to install. The "stack" is the set of patterns and conventions used for authoring markdown-based agents, templates, and command logic.

### Core

| Component | Location | Purpose | Why Standard |
|-----------|----------|---------|--------------|
| Agent definition format | `agents/gsd-codebase-mapper.md` | YAML frontmatter + role + process + templates + rules | Proven pattern used by all GSD agents. brownfield-analyzer must follow this exactly. |
| Template format | `get-shit-done/templates/codebase/*.md` | Template markdown with guidelines + good examples | Every codebase template uses this structure. brownfield-summary must follow it. |
| Command-level detection | `commands/gsd/new-project.md` Phase 1-2 | Bash heuristics for brownfield/greenfield detection | Current detection logic is the foundation to extend, not replace. |
| Workflow orchestration | `get-shit-done/workflows/map-codebase.md` | Task() spawning, confirmation collection | The pattern for how workflows delegate to agents. |

### Supporting

| Pattern | Where Used | Purpose | When to Apply |
|---------|-----------|---------|---------------|
| Signal-based analysis | STACK.md research | Read key files, not everything | When designing what the analyzer agent reads |
| Template-guided output | All codebase templates | Templates act as implicit prompts | When designing brownfield-summary.md template |
| Agent writes directly | map-codebase workflow | Agent writes to filesystem, returns confirmation only | When designing analyzer agent's output pattern |
| Confidence tagging | PITFALLS.md Pitfall 1 | Tag findings as OBSERVED vs INFERRED | When designing template sections |

### Alternatives Considered

| Recommended | Alternative | Why Not Alternative |
|-------------|-------------|---------------------|
| 7-section summary template (1:1 with codebase docs) | Freeform synthesis template | 1:1 mapping ensures completeness; agent can't accidentally skip a dimension |
| Multi-signal scoring (4 categories) | Binary file-existence check | Binary check produces false positives on scaffolded projects (Pitfall 2, 10) |
| Separate analyzer agent (not inline in command) | Inline synthesis in new-project.md | 7 documents total 200-1000+ lines; reading all in command context wastes tokens (Architecture research) |
| Bash-based detection (no LLM for detection phase) | LLM-powered mode detection | Detection must be deterministic and fast; LLM adds latency and non-determinism for a binary decision |

## Architecture Patterns

### Recommended Artifact Structure

```
get-shit-done/templates/
    brownfield-summary.md          # NEW: template for .planning/brownfield-analysis.md

agents/
    gsd-brownfield-analyzer.md     # NEW: agent definition

commands/gsd/
    new-project.md                 # MODIFIED (Phase 2+): detection logic module (for later integration)
```

### Pattern 1: Template-as-Implicit-Prompt

**What:** The brownfield-summary.md template structure tells the analyzer agent what to look for and how to organize findings. Each section heading is an implicit prompt.

**When to use:** When designing the template sections.

**How it works in existing templates:**

Each codebase template (e.g., `concerns.md`) has:
1. A top-level purpose statement
2. A `## File Template` section with the markdown structure agents fill in
3. `<good_examples>` showing what filled output looks like
4. `<guidelines>` explaining what belongs and what does not

The brownfield-summary template should follow this same structure, but its "File Template" section defines the synthesis output format (`.planning/brownfield-analysis.md`), not raw analysis.

**Source:** All 7 templates in `get-shit-done/templates/codebase/` follow this pattern.

### Pattern 2: Agent Definition Structure (from gsd-codebase-mapper.md)

**What:** Agent definitions use a consistent structure: YAML frontmatter, `<role>`, `<why_this_matters>`, `<philosophy>`, `<process>` (with steps), `<templates>`, `<critical_rules>`, `<success_criteria>`.

**When to use:** When authoring the gsd-brownfield-analyzer agent.

**Key differences from codebase-mapper:**
- Mapper reads raw codebase files (source code, configs, package.json)
- Analyzer reads processed documents (.planning/codebase/*.md)
- Mapper writes per-dimension documents (STACK.md, ARCHITECTURE.md, etc.)
- Analyzer writes one synthesis document (brownfield-analysis.md)
- Mapper uses Glob/Grep/Bash for exploration
- Analyzer primarily uses Read (documents are already structured)

**Agent tools needed:** Read, Write (possibly Glob to discover which codebase docs exist)

**Source:** `agents/gsd-codebase-mapper.md` (lines 1-763)

### Pattern 3: Multi-Signal Detection Scoring

**What:** Instead of binary file-existence checks, use a weighted scoring system with multiple signal categories to determine brownfield/greenfield/scaffolded status.

**When to use:** When designing the mode detection logic.

**Signal categories and weights:**

```bash
# Category 1: Code Files (weight: 30%)
# Count non-config, non-generated source files
CODE_FILE_COUNT=$(find . -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" \
  -o -name "*.rs" -o -name "*.swift" -o -name "*.java" -o -name "*.rb" \
  -o -name "*.php" -o -name "*.c" -o -name "*.cpp" -o -name "*.cs" \
  -o -name "*.ex" -o -name "*.exs" -o -name "*.kt" -o -name "*.dart" \
  -o -name "*.lua" -o -name "*.zig" -o -name "*.scala" -o -name "*.clj" \
  2>/dev/null | grep -v node_modules | grep -v .git | grep -v vendor \
  | grep -v dist | grep -v build | grep -v .next | grep -v __pycache__ \
  | grep -v target | grep -v _generated | wc -l | tr -d ' ')

# Category 2: Package Manager (weight: 20%)
HAS_PACKAGE=$(ls package.json requirements.txt Cargo.toml go.mod \
  pyproject.toml Gemfile composer.json *.csproj pom.xml build.gradle \
  mix.exs pubspec.yaml Package.swift 2>/dev/null | head -1)

# Category 3: Git History (weight: 25%)
GIT_COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
# >10 commits by different authors = strong brownfield signal

# Category 4: Directory Structure (weight: 25%)
DIR_COUNT=$(find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/.next/*' \
  2>/dev/null | wc -l | tr -d ' ')
# >5 meaningful directories = structured project
```

**Scoring thresholds:**
- **Brownfield:** CODE_FILE_COUNT > 10 AND (HAS_PACKAGE OR GIT_COMMIT_COUNT > 10)
- **Scaffolded (downgrade to greenfield):** CODE_FILE_COUNT > 0 AND CODE_FILE_COUNT <= 10 AND GIT_COMMIT_COUNT <= 3
- **Greenfield:** CODE_FILE_COUNT == 0

**Source:** Current `new-project.md` Phase 1 (basic detection), STACK.md research (expanded heuristics), PITFALLS.md Pitfalls 2 and 10 (false positive prevention).

### Anti-Patterns to Avoid

- **Exhaustive file reading in analyzer agent:** The analyzer reads 7 structured documents, not raw source code. It should NOT re-explore the codebase. (STACK.md Anti-Pattern 1)
- **Unstructured synthesis output:** The brownfield-summary template must enforce structure. No freeform prose. (STACK.md Anti-Pattern 2)
- **Generic agent prompts:** When spawning the analyzer, pass context about what was detected (language, framework, size). (STACK.md Anti-Pattern 4)
- **Binary brownfield detection:** File existence alone is insufficient. Use multi-signal scoring. (PITFALLS.md Pitfall 2, 10)
- **Confidence theater:** Template should require the analyzer to distinguish OBSERVED facts from INFERRED assessments. (PITFALLS.md Pitfall 1)

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Agent definition format | Invent new agent markdown structure | Copy gsd-codebase-mapper.md structure exactly | Existing agents are loaded by Claude Code's agent system. Format must be compatible. |
| Template format | Create ad-hoc template layout | Follow existing codebase template structure (purpose, file template, good examples, guidelines) | Consistency ensures the template works as an implicit prompt. |
| Detection heuristics | Complex AST-based analysis | Bash `find`, `ls`, `wc -l`, `git rev-list` | Deterministic, zero LLM tokens, works on any codebase. |
| Language detection | Language detection library | File extension counting via `find` | Sufficient for the detection phase. Agent-level analysis handles nuance. |
| Codebase doc discovery | Hardcoded list of 7 files | `ls .planning/codebase/*.md` | Flexible if documents are added/removed later. |

**Key insight:** This phase creates prompt-engineering artifacts (markdown templates and agent definitions), not traditional software. The "solution" is structured text that follows established GSD patterns, not code that runs.

## Common Pitfalls

### Pitfall 1: Template Sections That Are Too Vague

**What goes wrong:** The brownfield-summary template has sections like "Architecture" or "Concerns" without specifying what extraction the agent should perform from each source document. The agent produces generic prose instead of structured findings.

**Why it happens:** Template design focuses on output appearance rather than agent instruction. A section heading like "## Architecture Overview" doesn't tell the agent what to extract from ARCHITECTURE.md.

**How to avoid:** Each template section should specify:
1. Which source document(s) to read
2. What specific information to extract
3. How to format the extraction (table, bullet list, one-liner)

**Warning signs:** Agent output varies wildly between runs. Some sections are detailed, others are one-liners.

### Pitfall 2: False Positive Brownfield Detection on Scaffolded Projects

**What goes wrong:** User runs `npx create-next-app`, gets 30+ TypeScript files. Detection triggers brownfield mode. Analysis runs but finds nothing meaningful beyond default scaffold patterns. User confused.

**Why it happens:** File count alone triggers brownfield. Scaffolded projects have many files but no custom logic.

**How to avoid:** Multi-signal scoring with scaffolding detection:
- Check git history depth (scaffolded = 1-2 commits)
- Check if files are unmodified from scaffold defaults
- Count custom imports/exports vs framework boilerplate
- Graceful downgrade: "This looks like a scaffolded project. Treat as greenfield?"

**Warning signs:** Analysis documents mostly say "Not detected" or describe only framework defaults.

**Source:** PITFALLS.md Pitfalls 2 and 10.

### Pitfall 3: Analyzer Agent Reads Raw Source Code Instead of Codebase Documents

**What goes wrong:** The analyzer agent, given access to Read/Grep/Glob, starts exploring the actual codebase instead of reading the pre-analyzed `.planning/codebase/*.md` documents. This duplicates the mapper agents' work and produces inconsistent findings.

**Why it happens:** The agent definition doesn't clearly constrain its scope. Without explicit boundaries, LLM agents explore broadly.

**How to avoid:** The agent definition must:
1. Explicitly state: "Read ONLY from `.planning/codebase/` documents"
2. List the 7 input documents by name
3. Provide Read as the primary tool (not Grep/Glob/Bash for exploration)
4. In `<critical_rules>`: "DO NOT explore the codebase directly. Your inputs are the 7 codebase documents."

**Warning signs:** Agent makes Grep/Glob calls against `src/` or project root.

### Pitfall 4: Detection Logic That Misses Non-JS/TS Languages

**What goes wrong:** Current detection in new-project.md only checks: `.ts`, `.js`, `.py`, `.go`, `.rs`, `.swift`, `.java`. Projects in Kotlin, Elixir, Dart, Ruby, PHP, C/C++, Scala, Clojure, Zig are treated as greenfield.

**Why it happens:** Language list was not comprehensive when originally written.

**How to avoid:** Expand file extension list to include all major languages. Group by ecosystem:
- **Web/Backend:** `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.rb`, `.php`, `.go`, `.rs`, `.java`, `.kt`, `.kts`, `.scala`, `.clj`, `.cljs`, `.ex`, `.exs`
- **Mobile:** `.swift`, `.m`, `.dart`, `.kt`
- **Systems:** `.c`, `.cpp`, `.h`, `.hpp`, `.rs`, `.zig`
- **Others:** `.lua`, `.cs`, `.fs`, `.ml`, `.hs`

**Warning signs:** Users with non-JS projects report brownfield mode never triggers.

**Source:** PITFALLS.md Pitfall 12.

### Pitfall 5: brownfield-summary Template That Is Too Long for User Review

**What goes wrong:** The template produces a 200+ line analysis document. When presented to the user via AskUserQuestion, they don't read it and blindly select an option.

**Why it happens:** Template tries to capture everything from 7 documents. No prioritization or compression.

**How to avoid:** Template should have two tiers:
1. **Executive summary** (10-15 lines): One-liner per dimension + overall health rating + top 3 concerns
2. **Detailed sections** (expandable): Full findings per dimension, referenced but not shown inline

The agent's return confirmation to the orchestrator should include ONLY the executive summary. The full document lives in `.planning/brownfield-analysis.md` for reference.

**Source:** PITFALLS.md Pitfall 8.

## Code Examples

### Example 1: brownfield-summary.md Template Structure

Based on analysis of all 7 existing codebase templates, the brownfield-summary template should follow this structure:

```markdown
# Brownfield Summary Template

Template for `.planning/brownfield-analysis.md` — synthesized codebase analysis for user presentation.

**Purpose:** Compress 7 codebase documents into actionable summary. Read by brownfield-flow
workflow and presented to user before purpose selection (fix/improve/refactor).

---

## File Template

# Codebase Analysis Summary

**Analysis Date:** [YYYY-MM-DD]
**Codebase Health:** [Good / Moderate / Concerning]

## Executive Summary

| Dimension | Finding | Confidence |
|-----------|---------|------------|
| Architecture | [one-liner from ARCHITECTURE.md] | [HIGH/MEDIUM] |
| Tech Stack | [language + framework from STACK.md] | [HIGH/MEDIUM] |
| Code Quality | [key pattern from CONVENTIONS.md] | [HIGH/MEDIUM] |
| Testing | [coverage summary from TESTING.md] | [HIGH/MEDIUM] |
| Integrations | [count + key services from INTEGRATIONS.md] | [HIGH/MEDIUM] |
| Structure | [organization pattern from STRUCTURE.md] | [HIGH/MEDIUM] |
| Concerns | [count by severity from CONCERNS.md] | [HIGH/MEDIUM] |

## Top Concerns

[Top 3-5 from CONCERNS.md, ranked by impact]

1. **[Concern]** — [one-liner] (severity: [critical/moderate/minor])
2. **[Concern]** — [one-liner] (severity: [critical/moderate/minor])
3. **[Concern]** — [one-liner] (severity: [critical/moderate/minor])

## Architecture Overview
[Source: .planning/codebase/ARCHITECTURE.md]
[Pattern, layers, key abstractions — 5-10 lines max]

## Technology Stack
[Source: .planning/codebase/STACK.md]
[Language, framework, key deps, versions — 5-10 lines max]

## Code Quality & Conventions
[Source: .planning/codebase/CONVENTIONS.md]
[Style, patterns, maturity assessment — 5-10 lines max]

## Testing State
[Source: .planning/codebase/TESTING.md]
[Framework, coverage level, test types present — 5-10 lines max]

## External Integrations
[Source: .planning/codebase/INTEGRATIONS.md]
[Services, APIs, key external dependencies — 5-10 lines max]

## Codebase Structure
[Source: .planning/codebase/STRUCTURE.md]
[Organization, key directories, naming conventions — 5-10 lines max]

## Detailed Concerns
[Source: .planning/codebase/CONCERNS.md]
[Full concern list with file paths, grouped by category]

---
*Brownfield analysis: [date]*
```

**Source:** Derived from studying all 7 templates in `get-shit-done/templates/codebase/`.

### Example 2: gsd-brownfield-analyzer.md Agent Structure

Based on the gsd-codebase-mapper.md model:

```markdown
---
name: gsd-brownfield-analyzer
description: Synthesizes 7 codebase documents into brownfield-analysis.md. Spawned by
  brownfield-flow workflow. Reads .planning/codebase/, writes .planning/brownfield-analysis.md.
tools: Read, Write, Glob
color: cyan
---

<role>
You are a GSD brownfield analyzer. You read 7 structured codebase analysis documents
and synthesize them into a single brownfield analysis summary.

You are spawned by the brownfield-flow workflow after codebase mapping is complete.

Your job: Read all documents in .planning/codebase/, synthesize findings using the
brownfield-summary template, write .planning/brownfield-analysis.md, return confirmation.
</role>

<why_this_matters>
[Explain downstream consumption: workflow presents to user, user selects purpose,
purpose-aware questioning uses this, PROJECT.md references it]
</why_this_matters>

<process>
<step name="discover_documents">
ls .planning/codebase/*.md to find available documents.
Expected: ARCHITECTURE.md, STACK.md, STRUCTURE.md, CONVENTIONS.md,
TESTING.md, INTEGRATIONS.md, CONCERNS.md
</step>

<step name="read_all_documents">
Read each document. Extract key findings per dimension.
</step>

<step name="synthesize">
Fill brownfield-summary template. Prioritize concerns by severity.
Assign confidence levels to each finding.
</step>

<step name="write_output">
Write .planning/brownfield-analysis.md using the template.
</step>

<step name="return_confirmation">
Return structured confirmation with executive summary ONLY (not full document).
</step>
</process>

<critical_rules>
- DO NOT explore the codebase directly. Read ONLY .planning/codebase/*.md documents.
- Use the brownfield-summary template structure exactly.
- Distinguish OBSERVED facts from INFERRED assessments.
- Include file paths from source documents.
- Return confirmation with executive summary, NOT full document contents.
</critical_rules>
```

**Source:** Modeled on `agents/gsd-codebase-mapper.md`.

### Example 3: Multi-Signal Detection Logic

Based on current `new-project.md` Phase 1 expanded with STACK.md and PITFALLS.md recommendations:

```bash
# === BROWNFIELD DETECTION MODULE ===
# Multi-signal scoring: code_files + package_manager + git_history + directory_structure

# Signal 1: Code files (expanded language coverage)
CODE_FILES=$(find . \
  -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
  -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.java" \
  -o -name "*.kt" -o -name "*.swift" -o -name "*.rb" -o -name "*.php" \
  -o -name "*.c" -o -name "*.cpp" -o -name "*.cs" -o -name "*.scala" \
  -o -name "*.ex" -o -name "*.exs" -o -name "*.dart" -o -name "*.lua" \
  -o -name "*.zig" -o -name "*.clj" -o -name "*.cljs" \
  2>/dev/null | grep -v node_modules | grep -v .git | grep -v vendor \
  | grep -v dist | grep -v build | grep -v .next | grep -v __pycache__ \
  | grep -v target | grep -v _generated | grep -v .turbo)
CODE_FILE_COUNT=$(echo "$CODE_FILES" | grep -c . 2>/dev/null || echo "0")

# Signal 2: Package manager
HAS_PACKAGE=$(ls package.json requirements.txt Cargo.toml go.mod \
  pyproject.toml Gemfile composer.json *.csproj pom.xml build.gradle \
  mix.exs pubspec.yaml Package.swift setup.py setup.cfg 2>/dev/null | head -1)

# Signal 3: Git history depth
GIT_COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")

# Signal 4: Directory structure complexity
SRC_DIR_COUNT=$(find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/.next/*' \
  -not -path '*/__pycache__/*' -not -path '*/target/*' \
  2>/dev/null | wc -l | tr -d ' ')

# Signal 5: Codebase map already exists
HAS_CODEBASE_MAP=$([ -d .planning/codebase ] && echo "yes" || echo "no")

# === LANGUAGE DETECTION ===
# Determine primary language by file count
detect_primary_language() {
  local lang_counts=""
  for ext in ts tsx js jsx py go rs java kt swift rb php c cpp cs; do
    count=$(echo "$CODE_FILES" | grep -c "\\.$ext$" 2>/dev/null || echo "0")
    if [ "$count" -gt 0 ]; then
      lang_counts="$lang_counts$count $ext\n"
    fi
  done
  echo -e "$lang_counts" | sort -rn | head -1 | awk '{print $2}'
}
PRIMARY_LANG=$(detect_primary_language)

# === MODE DETERMINATION ===
if [ "$CODE_FILE_COUNT" -eq 0 ] && [ -z "$HAS_PACKAGE" ]; then
  MODE="greenfield"
elif [ "$CODE_FILE_COUNT" -le 10 ] && [ "$GIT_COMMIT_COUNT" -le 3 ]; then
  MODE="scaffolded"  # Graceful downgrade to greenfield
elif [ "$CODE_FILE_COUNT" -gt 10 ] || [ "$GIT_COMMIT_COUNT" -gt 10 ]; then
  MODE="brownfield"
else
  MODE="greenfield"  # Default safe
fi
```

**Source:** Extended from `commands/gsd/new-project.md` Phase 1, informed by STACK.md Tier 1 heuristics and PITFALLS.md Pitfalls 2/10.

## State of the Art

| Current (new-project.md) | Proposed (Phase 1) | What Changes | Impact |
|---------------------------|---------------------|--------------|--------|
| 7 file extensions checked | 20+ extensions across 6 language families | Broader language coverage, fewer false negatives | DETECT-01, DETECT-03 |
| Binary exists/not-exists | Multi-signal scoring (4 categories) | Reduces false positives, enables scaffolding detection | DETECT-02 |
| No language detection | Primary language auto-detect via file counting | Informs agent prompts for targeted analysis | DETECT-03 |
| No scaffolding handling | Graceful downgrade when scaffolding detected | Prevents wasted analysis on empty projects | DETECT-04 |
| Manual "Map codebase first?" prompt | Auto-detect + auto-map | Removes unnecessary user decision | UX improvement |
| No analysis synthesis | brownfield-analyzer agent + brownfield-summary template | 7 documents compressed to user-facing summary | INFRA-01, INFRA-03 |

## Open Questions

### 1. Scaffolding Detection Threshold

**What we know:** Git commit count <= 3 combined with low code file count (<= 10) is a reasonable heuristic for scaffolding detection. Most scaffolding tools create 1 initial commit.

**What's unclear:** What about projects where the user has made 2-3 commits modifying scaffold files? These are still effectively greenfield but would pass the commit threshold.

**Recommendation:** Use git commit count as one signal but also check for custom code indicators (functions, classes, custom imports beyond framework boilerplate). This can be deferred to Phase 2 integration if the basic threshold works well enough for Phase 1.

### 2. Framework-Specific Scaffold Detection

**What we know:** Different frameworks scaffold differently. `create-next-app` generates 15+ files. `cargo new` generates 2 files. A fixed threshold won't work for all.

**What's unclear:** Whether framework-specific thresholds are needed or if the multi-signal approach handles this naturally.

**Recommendation:** Start with the generic multi-signal approach. If false positives persist in testing, add framework-specific scaffold file lists as a refinement.

### 3. Analyzer Agent's Return Format

**What we know:** The codebase-mapper returns a 10-line confirmation. The brownfield-analyzer needs to return enough for the workflow to present to the user without reading the full file.

**What's unclear:** How much of the executive summary should be in the return vs. in the file. If the return is too minimal, the workflow must read the file (adding context load). If too rich, the agent-to-orchestrator context transfer is bloated.

**Recommendation:** Return the executive summary table (7 rows, ~15 lines) plus top 3 concerns. The workflow reads this return and presents it inline. The full document exists for reference but is not read by the workflow unless the user asks for details.

### 4. Template Design: Whether to Include Good Examples

**What we know:** All 7 existing codebase templates include `<good_examples>` sections with realistic filled-in examples. These significantly help agents understand the expected output quality.

**What's unclear:** Since the brownfield-summary template synthesizes from other documents (not raw code), it's unclear whether a good example would be realistic without actual codebase document content.

**Recommendation:** Include a good example. Fabricate a plausible one based on the examples already shown in the codebase template good_examples. This helps the analyzer agent understand the expected compression level and format.

## Sources

### Primary (HIGH confidence)

- `agents/gsd-codebase-mapper.md` — Agent definition pattern (read directly, 763 lines). This is the definitive model for all agent definitions in GSD.
- `get-shit-done/templates/codebase/architecture.md` — Template structure pattern (read directly, 256 lines). Representative of all 7 codebase templates.
- `get-shit-done/templates/codebase/concerns.md` — Template with good examples (read directly, 311 lines). Shows how to structure actionable findings.
- `get-shit-done/templates/codebase/conventions.md` — Template for conventions (read directly, 308 lines).
- `get-shit-done/templates/codebase/integrations.md` — Template for integrations (read directly, 281 lines).
- `get-shit-done/templates/codebase/stack.md` — Template for tech stack (read directly, 187 lines).
- `get-shit-done/templates/codebase/structure.md` — Template for structure (read directly, 286 lines).
- `get-shit-done/templates/codebase/testing.md` — Template for testing (read directly, 481 lines).
- `commands/gsd/new-project.md` — Current brownfield detection logic (read directly, Phase 1-2, lines 40-93). The baseline to extend.
- `commands/gsd/map-codebase.md` — Codebase mapping command (read directly, 93 lines). Shows how commands delegate to workflows.
- `get-shit-done/workflows/map-codebase.md` — Workflow orchestration pattern (read directly, 343 lines). Shows Task() spawning and confirmation collection.
- `get-shit-done/templates/project.md` — PROJECT.md template with brownfield section (read directly, lines 146-167).

### Secondary (MEDIUM confidence)

- `.planning/research/STACK.md` — Analysis approaches, signal-based analysis tiers, agent coordination strategies. Written by project researcher based on domain analysis.
- `.planning/research/ARCHITECTURE.md` — System design for mode branching, component responsibilities, data flow. Written by project researcher.
- `.planning/research/FEATURES.md` — Feature landscape, MVP definition, dependency graph. Written by project researcher.
- `.planning/research/PITFALLS.md` — Domain pitfalls, especially Pitfalls 1 (hallucination), 2 (threshold), 10 (partially brownfield), 12 (language gaps). Written by project researcher.

### Tertiary (LOW confidence)

- None. All findings are grounded in direct codebase analysis or prior project research.

## Metadata

**Confidence breakdown:**
- Template design: HIGH — 7 existing templates provide clear precedent; pattern is well-established
- Agent definition: HIGH — gsd-codebase-mapper.md is a complete, proven model to follow
- Detection logic: HIGH — current new-project.md provides working baseline; expansion is straightforward Bash
- Scaffolding detection: MEDIUM — heuristics are reasonable but untested; threshold tuning may be needed
- Language detection: HIGH — file extension counting is deterministic and reliable

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (stable domain — prompt engineering patterns don't change rapidly)
