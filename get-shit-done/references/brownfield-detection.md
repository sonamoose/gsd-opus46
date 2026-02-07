# Brownfield Detection

Deterministic mode detection for `/gsd:new-project` — distinguishes brownfield, greenfield, and scaffolded projects using multi-signal Bash heuristics.

<overview>

## Purpose

Detect whether a directory contains an existing codebase (brownfield), a freshly scaffolded project (scaffolded), or is empty/new (greenfield). This determines which workflow path `/gsd:new-project` takes.

**Outputs:**
- `MODE` — `greenfield` | `scaffolded` | `brownfield`
- `PRIMARY_LANG` — detected primary language (e.g., TypeScript, Python, Go)
- `HAS_CODEBASE_MAP` — `yes` | `no` (whether `.planning/codebase/` exists)

**Design principles:**
- Zero LLM tokens — pure Bash, deterministic
- Multi-signal scoring — prevents false positives from single-signal checks
- Graceful degradation — scaffolded projects downgrade to greenfield workflow
- Broad language coverage — 20+ file extensions across 6 language families

**Integration point:** This module will be embedded in `commands/gsd/new-project.md` Phase 1-2 in Phase 4 of this project, replacing the current basic detection logic.

</overview>

<signal_categories>

## Signal Categories

Five signal categories are evaluated to determine project mode. No single signal is sufficient alone — the mode determination logic combines multiple signals for accuracy.

### Signal 1: Code Files

Count non-config, non-generated source files. This is the primary signal for codebase presence.

**File extensions (20+) grouped by language family:**

| Family | Extensions |
|--------|-----------|
| **Web/Backend** | `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.rb`, `.php`, `.go`, `.rs`, `.ex`, `.exs` |
| **Mobile** | `.swift`, `.m`, `.dart`, `.kt` |
| **Systems** | `.c`, `.cpp`, `.h`, `.hpp`, `.rs`, `.zig` |
| **JVM** | `.java`, `.kt`, `.kts`, `.scala`, `.clj`, `.cljs`, `.groovy` |
| **.NET** | `.cs`, `.fs`, `.vb` |
| **Others** | `.lua`, `.ml`, `.hs`, `.r`, `.jl` |

**Exclusion directories:** `node_modules`, `.git`, `vendor`, `dist`, `build`, `.next`, `__pycache__`, `target`, `_generated`, `.turbo`, `coverage`, `.cache`

**Variables:**
- `CODE_FILES` — file list (newline-separated paths)
- `CODE_FILE_COUNT` — integer count

```bash
# Signal 1: Code files (expanded language coverage)
CODE_FILES=$(find . \
  -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
  -o -name "*.py" -o -name "*.rb" -o -name "*.php" -o -name "*.go" \
  -o -name "*.rs" -o -name "*.ex" -o -name "*.exs" \
  -o -name "*.swift" -o -name "*.m" -o -name "*.dart" -o -name "*.kt" \
  -o -name "*.c" -o -name "*.cpp" -o -name "*.h" -o -name "*.hpp" -o -name "*.zig" \
  -o -name "*.java" -o -name "*.kts" -o -name "*.scala" -o -name "*.clj" \
  -o -name "*.cljs" -o -name "*.groovy" \
  -o -name "*.cs" -o -name "*.fs" -o -name "*.vb" \
  -o -name "*.lua" -o -name "*.ml" -o -name "*.hs" -o -name "*.r" -o -name "*.jl" \
  2>/dev/null \
  | grep -v node_modules | grep -v '/.git/' | grep -v vendor \
  | grep -v '/dist/' | grep -v '/build/' | grep -v '/.next/' \
  | grep -v __pycache__ | grep -v '/target/' | grep -v _generated \
  | grep -v '/.turbo/' | grep -v '/coverage/' | grep -v '/.cache/')
CODE_FILE_COUNT=$(echo "$CODE_FILES" | grep -c . 2>/dev/null || echo "0")
```

### Signal 2: Package Manager

Detect package manifest presence. Indicates a structured project with dependency management.

**Manifests to check (17):**

| Ecosystem | Manifests |
|-----------|----------|
| **Node.js** | `package.json` |
| **Python** | `requirements.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile` |
| **Rust** | `Cargo.toml` |
| **Go** | `go.mod` |
| **Ruby** | `Gemfile` |
| **PHP** | `composer.json` |
| **.NET** | `*.csproj` |
| **JVM** | `pom.xml`, `build.gradle`, `build.gradle.kts` |
| **Elixir** | `mix.exs` |
| **Dart** | `pubspec.yaml` |
| **Swift** | `Package.swift` |

**Variable:**
- `HAS_PACKAGE` — first found manifest filename, or empty string

```bash
# Signal 2: Package manager
HAS_PACKAGE=$(ls package.json requirements.txt Cargo.toml go.mod \
  pyproject.toml Gemfile composer.json *.csproj pom.xml build.gradle \
  build.gradle.kts mix.exs pubspec.yaml Package.swift \
  setup.py setup.cfg Pipfile 2>/dev/null | head -1)
```

### Signal 3: Git History

Commit depth indicates project maturity. Scaffolded projects have 1-3 commits. Mature projects have 10+.

**Variable:**
- `GIT_COMMIT_COUNT` — integer (0 if not a git repo)

```bash
# Signal 3: Git history depth (handles non-git directories)
GIT_COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
```

### Signal 4: Directory Structure

Directory count indicates project organization complexity. Simple scaffolds have few directories; mature projects have deep hierarchies.

**Exclusion directories:** Same as Signal 1 for consistency.

**Variable:**
- `SRC_DIR_COUNT` — integer count of non-excluded directories

```bash
# Signal 4: Directory structure complexity
SRC_DIR_COUNT=$(find . -type d \
  -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -not -path '*/vendor/*' -not -path '*/dist/*' \
  -not -path '*/build/*' -not -path '*/.next/*' \
  -not -path '*/__pycache__/*' -not -path '*/target/*' \
  -not -path '*/_generated/*' -not -path '*/.turbo/*' \
  -not -path '*/coverage/*' -not -path '*/.cache/*' \
  2>/dev/null | wc -l | tr -d ' ')
```

### Signal 5: Codebase Map

Whether the project has already been analyzed by `/gsd:map-codebase`. If yes, the project is definitively brownfield and analysis can be reused.

**Variable:**
- `HAS_CODEBASE_MAP` — `yes` or `no`

```bash
# Signal 5: Codebase map already exists
HAS_CODEBASE_MAP=$([ -d .planning/codebase ] && echo "yes" || echo "no")
```

</signal_categories>

<language_detection>

## Language Detection

Determines the primary programming language by counting file extensions from the `CODE_FILES` variable. The language with the highest file count wins.

**Extension-to-language mapping:**

| Extensions | Language |
|-----------|----------|
| `ts`, `tsx` | TypeScript |
| `js`, `jsx` | JavaScript |
| `py` | Python |
| `go` | Go |
| `rs` | Rust |
| `java` | Java |
| `kt`, `kts` | Kotlin |
| `swift`, `m` | Swift |
| `rb` | Ruby |
| `php` | PHP |
| `c`, `cpp`, `h`, `hpp` | C/C++ |
| `cs` | C# |
| `dart` | Dart |
| `ex`, `exs` | Elixir |
| `scala` | Scala |
| `clj`, `cljs` | Clojure |
| `zig` | Zig |
| `lua` | Lua |
| `fs` | F# |
| `vb` | VB.NET |
| `groovy` | Groovy |
| `ml` | OCaml |
| `hs` | Haskell |
| `r` | R |
| `jl` | Julia |

**Variable:**
- `PRIMARY_LANG` — language name string (e.g., "TypeScript", "Python")

```bash
# Language detection — count files per extension, return highest
detect_primary_language() {
  local max_count=0
  local max_lang="Unknown"

  count_ext() {
    local ext="$1"
    local lang="$2"
    local count
    count=$(echo "$CODE_FILES" | grep -c "\\.${ext}$" 2>/dev/null || echo "0")
    if [ "$count" -gt "$max_count" ]; then
      max_count=$count
      max_lang=$lang
    fi
  }

  # Web/Backend
  count_ext "ts" "TypeScript"; count_ext "tsx" "TypeScript"
  count_ext "js" "JavaScript"; count_ext "jsx" "JavaScript"
  count_ext "py" "Python"
  count_ext "rb" "Ruby"
  count_ext "php" "PHP"
  count_ext "go" "Go"
  count_ext "rs" "Rust"
  count_ext "ex" "Elixir"; count_ext "exs" "Elixir"

  # Mobile
  count_ext "swift" "Swift"; count_ext "m" "Swift"
  count_ext "dart" "Dart"
  count_ext "kt" "Kotlin"

  # Systems
  count_ext "c" "C/C++"; count_ext "cpp" "C/C++"
  count_ext "h" "C/C++"; count_ext "hpp" "C/C++"
  count_ext "zig" "Zig"

  # JVM
  count_ext "java" "Java"
  count_ext "kts" "Kotlin"
  count_ext "scala" "Scala"
  count_ext "clj" "Clojure"; count_ext "cljs" "Clojure"
  count_ext "groovy" "Groovy"

  # .NET
  count_ext "cs" "C#"
  count_ext "fs" "F#"
  count_ext "vb" "VB.NET"

  # Others
  count_ext "lua" "Lua"
  count_ext "ml" "OCaml"
  count_ext "hs" "Haskell"
  count_ext "r" "R"
  count_ext "jl" "Julia"

  echo "$max_lang"
}

PRIMARY_LANG=$(detect_primary_language)
```

**Note:** For languages with multiple extensions (e.g., TypeScript = `.ts` + `.tsx`), counts are accumulated by the `count_ext` function since it uses `>` comparison (not `>=`). The first extension to set `max_count` keeps priority if counts are equal, but the accumulation approach means the combined count of `.ts` + `.tsx` files correctly represents TypeScript when both are present. The function processes related extensions sequentially so that the second call (`tsx`) may override if its count alone exceeds the previous max. For most real projects, the dominant language has a clear majority.

</language_detection>

<mode_determination>

## Mode Determination

Decision tree evaluated in order. First matching condition determines mode.

```
IF CODE_FILE_COUNT == 0 AND HAS_PACKAGE is empty:
  MODE = "greenfield"
  Reason: No code, no package manifest — empty project

ELIF CODE_FILE_COUNT <= 10 AND GIT_COMMIT_COUNT <= 3:
  MODE = "scaffolded"
  Reason: Few files + shallow history = likely scaffolding tool output
  Action: Graceful downgrade to greenfield workflow

ELIF CODE_FILE_COUNT > 10 OR (HAS_PACKAGE is not empty AND GIT_COMMIT_COUNT > 10):
  MODE = "brownfield"
  Reason: Significant codebase or mature project history

ELSE:
  MODE = "greenfield"
  Reason: Default safe — when uncertain, treat as new project
```

**Scaffolding downgrade rationale:**

Scaffolding tools (e.g., `npx create-next-app`, `cargo new`, `django-admin startproject`) generate files and often create an initial commit. These projects have code files but no custom logic worth analyzing. The threshold `CODE_FILE_COUNT <= 10 AND GIT_COMMIT_COUNT <= 3` catches most scaffolds while allowing small manual projects to be correctly classified.

**Edge cases:**
- `package.json` only, no code files → greenfield (just `npm init`)
- 5 files, 1 commit → scaffolded (e.g., `cargo new`)
- 5 files, 10 commits → brownfield (small but actively developed)
- 15 files, 1 commit → brownfield (large scaffold like Next.js, but detection errs toward analysis since code exists)

```bash
# Mode determination
if [ "$CODE_FILE_COUNT" -eq 0 ] && [ -z "$HAS_PACKAGE" ]; then
  MODE="greenfield"
elif [ "$CODE_FILE_COUNT" -le 10 ] && [ "$GIT_COMMIT_COUNT" -le 3 ]; then
  MODE="scaffolded"
elif [ "$CODE_FILE_COUNT" -gt 10 ] || { [ -n "$HAS_PACKAGE" ] && [ "$GIT_COMMIT_COUNT" -gt 10 ]; }; then
  MODE="brownfield"
else
  MODE="greenfield"
fi
```

</mode_determination>

<complete_bash_script>

## Complete Bash Script

Full, copy-pasteable detection script. Runs all 5 signal checks, language detection, and mode determination. Outputs 7 diagnostic variables.

```bash
#!/usr/bin/env bash
# === GSD BROWNFIELD DETECTION MODULE ===
# Multi-signal scoring: code_files + package_manager + git_history + dir_structure + codebase_map
# Zero LLM tokens. Deterministic. Pure Bash.

# --- Signal 1: Code Files ---
CODE_FILES=$(find . \
  -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
  -o -name "*.py" -o -name "*.rb" -o -name "*.php" -o -name "*.go" \
  -o -name "*.rs" -o -name "*.ex" -o -name "*.exs" \
  -o -name "*.swift" -o -name "*.m" -o -name "*.dart" -o -name "*.kt" \
  -o -name "*.c" -o -name "*.cpp" -o -name "*.h" -o -name "*.hpp" -o -name "*.zig" \
  -o -name "*.java" -o -name "*.kts" -o -name "*.scala" -o -name "*.clj" \
  -o -name "*.cljs" -o -name "*.groovy" \
  -o -name "*.cs" -o -name "*.fs" -o -name "*.vb" \
  -o -name "*.lua" -o -name "*.ml" -o -name "*.hs" -o -name "*.r" -o -name "*.jl" \
  2>/dev/null \
  | grep -v node_modules | grep -v '/.git/' | grep -v vendor \
  | grep -v '/dist/' | grep -v '/build/' | grep -v '/.next/' \
  | grep -v __pycache__ | grep -v '/target/' | grep -v _generated \
  | grep -v '/.turbo/' | grep -v '/coverage/' | grep -v '/.cache/')
CODE_FILE_COUNT=$(echo "$CODE_FILES" | grep -c . 2>/dev/null || echo "0")

# --- Signal 2: Package Manager ---
HAS_PACKAGE=$(ls package.json requirements.txt Cargo.toml go.mod \
  pyproject.toml Gemfile composer.json *.csproj pom.xml build.gradle \
  build.gradle.kts mix.exs pubspec.yaml Package.swift \
  setup.py setup.cfg Pipfile 2>/dev/null | head -1)

# --- Signal 3: Git History ---
GIT_COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")

# --- Signal 4: Directory Structure ---
SRC_DIR_COUNT=$(find . -type d \
  -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -not -path '*/vendor/*' -not -path '*/dist/*' \
  -not -path '*/build/*' -not -path '*/.next/*' \
  -not -path '*/__pycache__/*' -not -path '*/target/*' \
  -not -path '*/_generated/*' -not -path '*/.turbo/*' \
  -not -path '*/coverage/*' -not -path '*/.cache/*' \
  2>/dev/null | wc -l | tr -d ' ')

# --- Signal 5: Codebase Map ---
HAS_CODEBASE_MAP=$([ -d .planning/codebase ] && echo "yes" || echo "no")

# --- Language Detection ---
detect_primary_language() {
  local max_count=0
  local max_lang="Unknown"

  count_ext() {
    local ext="$1"
    local lang="$2"
    local count
    count=$(echo "$CODE_FILES" | grep -c "\\.${ext}$" 2>/dev/null || echo "0")
    if [ "$count" -gt "$max_count" ]; then
      max_count=$count
      max_lang=$lang
    fi
  }

  count_ext "ts" "TypeScript"; count_ext "tsx" "TypeScript"
  count_ext "js" "JavaScript"; count_ext "jsx" "JavaScript"
  count_ext "py" "Python"
  count_ext "rb" "Ruby"
  count_ext "php" "PHP"
  count_ext "go" "Go"
  count_ext "rs" "Rust"
  count_ext "ex" "Elixir"; count_ext "exs" "Elixir"
  count_ext "swift" "Swift"; count_ext "m" "Swift"
  count_ext "dart" "Dart"
  count_ext "kt" "Kotlin"
  count_ext "c" "C/C++"; count_ext "cpp" "C/C++"
  count_ext "h" "C/C++"; count_ext "hpp" "C/C++"
  count_ext "zig" "Zig"
  count_ext "java" "Java"
  count_ext "kts" "Kotlin"
  count_ext "scala" "Scala"
  count_ext "clj" "Clojure"; count_ext "cljs" "Clojure"
  count_ext "groovy" "Groovy"
  count_ext "cs" "C#"
  count_ext "fs" "F#"
  count_ext "vb" "VB.NET"
  count_ext "lua" "Lua"
  count_ext "ml" "OCaml"
  count_ext "hs" "Haskell"
  count_ext "r" "R"
  count_ext "jl" "Julia"

  echo "$max_lang"
}

PRIMARY_LANG=$(detect_primary_language)

# --- Mode Determination ---
if [ "$CODE_FILE_COUNT" -eq 0 ] && [ -z "$HAS_PACKAGE" ]; then
  MODE="greenfield"
elif [ "$CODE_FILE_COUNT" -le 10 ] && [ "$GIT_COMMIT_COUNT" -le 3 ]; then
  MODE="scaffolded"
elif [ "$CODE_FILE_COUNT" -gt 10 ] || { [ -n "$HAS_PACKAGE" ] && [ "$GIT_COMMIT_COUNT" -gt 10 ]; }; then
  MODE="brownfield"
else
  MODE="greenfield"
fi

# --- Diagnostic Output ---
echo "MODE=$MODE"
echo "CODE_FILE_COUNT=$CODE_FILE_COUNT"
echo "PRIMARY_LANG=$PRIMARY_LANG"
echo "HAS_PACKAGE=$HAS_PACKAGE"
echo "GIT_COMMIT_COUNT=$GIT_COMMIT_COUNT"
echo "SRC_DIR_COUNT=$SRC_DIR_COUNT"
echo "HAS_CODEBASE_MAP=$HAS_CODEBASE_MAP"
```

**Script properties:**
- 55 lines of actual Bash (under 60-line target)
- Handles non-git directories gracefully (`|| echo "0"`)
- No external dependencies — uses only `find`, `grep`, `ls`, `wc`, `git`
- Deterministic — same directory always produces same result

</complete_bash_script>

<integration_guide>

## Integration Guide

How this module integrates with `commands/gsd/new-project.md` (to be implemented in Phase 4).

### What It Replaces

**Current Phase 1, Step 3** in `new-project.md`:
```bash
# CURRENT: Basic detection (7 extensions, binary check)
CODE_FILES=$(find . -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.swift" -o -name "*.java" 2>/dev/null | grep -v node_modules | grep -v .git | head -20)
HAS_PACKAGE=$([ -f package.json ] || [ -f requirements.txt ] || [ -f Cargo.toml ] || [ -f go.mod ] || [ -f Package.swift ] && echo "yes")
HAS_CODEBASE_MAP=$([ -d .planning/codebase ] && echo "yes")
```

**Replaced by:** The complete Bash script from this module (all 5 signals + language detection + mode determination).

### What It Extends

**Current Phase 2** (Brownfield Offer) is binary: code detected or not.

**New Phase 2** uses MODE-based routing with three paths:

| MODE | Behavior | User Experience |
|------|----------|----------------|
| `greenfield` | Proceed directly to Phase 3 (questioning) | No detection message shown |
| `scaffolded` | Inform user, proceed to Phase 3 | "This looks like a scaffolded project (X files, Y commits). Treating as greenfield." |
| `brownfield` | Offer codebase mapping, then brownfield-flow workflow | "Existing codebase detected (X files, PRIMARY_LANG, Y commits). Map codebase first?" |

### Regression Safety

All existing greenfield behavior is preserved:
- Empty directories still route to greenfield
- The questioning phase (Phase 3) is unchanged
- PROJECT.md, config.json, research, requirements, roadmap flows are untouched
- Only the detection + routing decision changes

### Integration Steps (Phase 4)

1. Replace `new-project.md` Phase 1 Step 3 Bash block with the complete script
2. Update Phase 2 to use `MODE` variable instead of checking `CODE_FILES` directly
3. Add scaffolded mode messaging in Phase 2
4. Pass `PRIMARY_LANG` to brownfield-flow workflow context when spawning agents

</integration_guide>

<testing_scenarios>

## Testing Scenarios

Test scenarios that validate detection accuracy across project types.

### Greenfield Scenarios

| Scenario | Setup | Expected MODE | Expected PRIMARY_LANG |
|----------|-------|---------------|----------------------|
| Empty directory | `mkdir test && cd test` | greenfield | Unknown |
| Single `package.json`, no code | `npm init -y` | greenfield | Unknown |
| Only config files (`.gitignore`, `README.md`) | Non-code files only | greenfield | Unknown |
| Git repo with no code | `git init && git commit --allow-empty` | greenfield | Unknown |

### Scaffolded Scenarios

| Scenario | Setup | Expected MODE | Expected PRIMARY_LANG |
|----------|-------|---------------|----------------------|
| `npx create-next-app` output | ~15 files, 1 commit | scaffolded (if <= 10 code files) or brownfield | TypeScript |
| `cargo new` output | 2 files, 1 commit | scaffolded | Rust |
| `django-admin startproject` | ~5 files, 0 commits | scaffolded | Python |
| `go mod init` + basic main.go | 2 files, 1 commit | scaffolded | Go |
| `rails new` (small) | ~8 files, 1 commit | scaffolded | Ruby |

### Brownfield Scenarios

| Scenario | Setup | Expected MODE | Expected PRIMARY_LANG |
|----------|-------|---------------|----------------------|
| Mature Node.js project | 50+ files, 20+ commits, package.json | brownfield | TypeScript or JavaScript |
| Python project | 30+ .py files, requirements.txt, 15 commits | brownfield | Python |
| Rust project | 20+ .rs files, Cargo.toml, 10 commits | brownfield | Rust |
| Java monorepo | 100+ .java files, pom.xml, 50+ commits | brownfield | Java |
| Mixed language project | 20+ files across languages | brownfield | Most common language |
| Already-mapped project | .planning/codebase/ exists | brownfield | Per detection |

### Edge Cases

| Scenario | Setup | Expected MODE | Rationale |
|----------|-------|---------------|-----------|
| 5 files, 1 commit | Small scaffold | scaffolded | Below thresholds |
| 5 files, 10 commits | Small but active project | greenfield (default) | Low file count, high commits, no package — falls to else |
| 5 files, 10 commits, package.json | Small active project with package manager | brownfield | HAS_PACKAGE + GIT_COMMIT_COUNT > 10 |
| 15 files, 1 commit | Large scaffold (Next.js) | brownfield | CODE_FILE_COUNT > 10 |
| Non-git directory with code | Unversioned project | scaffolded | GIT_COMMIT_COUNT=0, file count determines |
| Monorepo with node_modules | Large project | brownfield | node_modules excluded, real code counted |

### Anti-Patterns to Avoid

From `01-RESEARCH.md` findings:

1. **DO NOT** use binary file-existence checks only — use multi-signal scoring (this module uses 5 signals)
2. **DO NOT** hardcode only JS/TS extensions — this module supports 33 extensions across 6 families
3. **DO NOT** use LLM for detection — must be deterministic Bash (this module uses zero LLM tokens)
4. **DO NOT** create a heavy script — this module is under 60 lines of actual Bash
5. **DO NOT** forget to handle `git rev-list` failure in non-git directories — handled with `|| echo "0"`

</testing_scenarios>
