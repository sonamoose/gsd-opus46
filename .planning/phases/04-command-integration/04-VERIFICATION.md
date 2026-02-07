---
status: passed
score: 11/11
---

# Phase 4 Verification: Command Integration

## Goal

`new-project.md` 커맨드에 브라운필드 분기 로직을 통합하여, 사용자가 `/gsd:new-project`만 실행하면 자동으로 최적 흐름이 적용되게 한다.

## Must-Haves Checked

### Plan 04-01 Must-Haves

| # | Must-Have | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Empty directory produces MODE=greenfield and reaches Phase 3 unchanged | PASS | `new-project.md:158-159` — `if CODE_FILE_COUNT == 0 AND HAS_PACKAGE is empty -> MODE="greenfield"`. Line 184: `If MODE == "greenfield": Continue directly to Phase 3`. Phase 3 content (line 289+) is standard greenfield questioning with no brownfield modifications. |
| 2 | Scaffolded project (<=10 files, <=3 commits) produces MODE=scaffolded and reaches Phase 3 with info message | PASS | `new-project.md:160-161` — `elif CODE_FILE_COUNT <= 10 AND GIT_COMMIT_COUNT <= 3 -> MODE="scaffolded"`. Lines 187-192: displays info message with file count and commit count, then continues to Phase 3. |
| 3 | Mature codebase (>10 files OR package+>10 commits) produces MODE=brownfield | PASS | `new-project.md:162-163` — `elif CODE_FILE_COUNT > 10 OR (HAS_PACKAGE not empty AND GIT_COMMIT_COUNT > 10) -> MODE="brownfield"`. Two independent conditions for brownfield detection. |
| 4 | MODE variable is the single source of truth for routing (raw signals not re-checked) | PASS | Phase 2 (line 180) routes exclusively on `MODE` variable. Lines 182-199: all three routing branches check `MODE ==` only. No references to `CODE_FILES`, `HAS_PACKAGE`, or `HAS_CODEBASE_MAP` in routing decisions. Phase 2B's use of `HAS_CODEBASE_MAP` (line 208) is for map-codebase skip logic, not for mode routing. |
| 5 | Greenfield Phase 3+ is byte-identical to pre-modification state | PASS | Phase 3 (line 289-343), Phase 4 (line 345-433), Phase 5 (line 435-573), Phase 6 (line 580-825, after guard), Phase 7 (line 827-970, after guard), Phase 8 (line 972-1114, after guard) all contain original greenfield content. Guards are prepended as standalone lines; existing content is not modified. |

### Plan 04-02 Must-Haves

| # | Must-Have | Status | Evidence |
|---|-----------|--------|----------|
| 6 | Brownfield project runs map-codebase inline (no exit-and-return) | PASS | `new-project.md:205-223` — Phase 2B Step 1 references `@~/.claude/get-shit-done/workflows/map-codebase.md` inline. Grep for "exit-and-return", "exit command", "Run map-codebase first then return" returns zero matches. No AskUserQuestion exists in Phase 2 routing. |
| 7 | Brownfield project runs brownfield-flow inline with purpose routing | PASS | `new-project.md:225-248` — Phase 2B Step 2 references `@~/.claude/get-shit-done/workflows/brownfield-flow.md` inline. Line 237: "purpose_routing: true (default)". Line 241: "CRITICAL: brownfield-flow uses AskUserQuestion... It MUST execute inline within this command context. Do NOT spawn it as Task()." |
| 8 | Brownfield project writes PROJECT.md with Validated requirements from codebase | PASS | `new-project.md:249-272` — Phase 2B Step 3 instructs: "Read .planning/codebase/ARCHITECTURE.md and STACK.md. Infer Validated requirements from existing code capabilities." Lines 374-399 provide the detailed brownfield PROJECT.md writing logic with "Validated" section containing `existing` tagged items. Lines 255-257 add Codebase Mode and brownfield-analysis.md reference. |
| 9 | Brownfield project skips Phases 3, 4, 6, 7, 8 and converges at Phase 5 | PASS | Phase 2B Step 4 (lines 274-287) explicitly lists skipped phases: Phase 3 (questioning), Phase 4 (PROJECT.md), Phase 6 (research), Phase 7 (requirements), Phase 8 (roadmap). Lines 287, 291: guards before Phase 3. Line 582: Phase 6 guard. Line 829: Phase 7 guard. Line 974: Phase 8 guard. All guards direct to skip. |
| 10 | Greenfield project executes Phases 3-10 unchanged (STATE-03 regression safety) | PASS | All brownfield guards are conditional on `MODE == "brownfield"`. When MODE is greenfield or scaffolded, guards are not triggered and all phases execute normally. Phase 3 content starts at line 293 (after guard). execution_context (lines 32-39) has no brownfield references -- only greenfield templates/references. Greenfield path: Phase 1 -> Phase 2 (silent) -> Phase 3 -> Phase 4 -> Phase 5 -> Phase 6 -> Phase 7 -> Phase 8 -> Phase 10. |
| 11 | Phase 10 Done banner adapts artifacts dynamically for both paths | PASS | `new-project.md:1120-1158` — Phase 10 Done banner uses conditional rows: `{If .planning/brownfield-analysis.md exists:}` for Analysis row (line 1133), `{If .planning/research/ exists:}` for Research row (line 1136). Lines 1142-1143: conditional brownfield completion message. Both paths share Project, Config, Requirements, Roadmap rows. |

## Path Trace: Greenfield

1. **Phase 1: Setup** (line 43)
   - Step 1: Abort check (`[ -f .planning/PROJECT.md ]`) -- passes if no existing project
   - Step 2: Git init check -- initializes if needed
   - Step 3: Brownfield detection (lines 63-176) -- runs full 5-signal script
   - Result: `MODE=greenfield` (CODE_FILE_COUNT=0, no package manager)

2. **Phase 2: Mode Routing** (line 180)
   - Line 184: `If MODE == "greenfield":` -- matched
   - "No existing code detected. Continue directly to Phase 3."
   - **No message shown to user** (silent pass-through)

3. **Phase 3: Deep Questioning** (line 289)
   - Line 291: Guard `If MODE == "brownfield"` -- NOT triggered (MODE is greenfield)
   - Proceeds to questioning flow (banner, "What do you want to build?", follow-up questions, decision gate)

4. **Phase 4: Write PROJECT.md** (line 345)
   - Greenfield path: requirements as hypotheses (Active, none Validated)
   - Commit PROJECT.md

5. **Phase 5: Workflow Preferences** (line 435)
   - 4 core workflow questions + 4 agent questions
   - Write config.json, commit

6. **Phase 5.5: Effort Level** (line 575)
   - References model-profiles.md

7. **Phase 6: Research Decision** (line 580)
   - Line 582: Guard `If MODE == "brownfield"` -- NOT triggered
   - User chooses research or skip
   - If research: 4 parallel researchers + synthesizer

8. **Phase 7: Define Requirements** (line 827)
   - Line 829: Guard `If MODE == "brownfield"` -- NOT triggered
   - Feature categories, scoping, REQUIREMENTS.md

9. **Phase 8: Create Roadmap** (line 972)
   - Line 974: Guard `If MODE == "brownfield"` -- NOT triggered
   - Spawn gsd-roadmapper, present roadmap, get approval

10. **Phase 10: Done** (line 1116)
    - Dynamic banner: Project, Config, Research (if exists), Requirements, Roadmap
    - No brownfield-analysis.md exists, so Analysis row is NOT shown
    - No brownfield message shown (line 1142 condition not met)
    - Next step: `/gsd:discuss-phase 1`

**Verdict:** Greenfield path is clean end-to-end. No brownfield artifacts or messages leak into the greenfield experience.

## Path Trace: Brownfield

1. **Phase 1: Setup** (line 43)
   - Step 1: Abort check -- passes if no existing PROJECT.md
   - Step 2: Git init check
   - Step 3: Brownfield detection -- runs full 5-signal script
   - Result: `MODE=brownfield` (e.g., CODE_FILE_COUNT=50, HAS_PACKAGE=package.json, GIT_COMMIT_COUNT=20)

2. **Phase 2: Mode Routing** (line 180)
   - Line 194: `If MODE == "brownfield":` -- matched
   - Displays: "Existing codebase detected: {CODE_FILE_COUNT} files, {PRIMARY_LANG}, {GIT_COMMIT_COUNT} commits."
   - Routes to Phase 2B

3. **Phase 2B: Brownfield Pipeline** (line 201)
   - Line 203: "This phase runs ONLY when MODE == brownfield."
   - **Step 1** (line 205): Map Codebase
     - Checks HAS_CODEBASE_MAP; if no, runs map-codebase.md inline (4 parallel agents, 7 documents)
     - If existing map: "Using existing codebase map." Skip.
   - **Step 2** (line 225): Run brownfield-flow inline
     - purpose_routing: true (default)
     - Steps 1-5: Analysis pipeline
     - Steps 6-9: Purpose routing (AskUserQuestion for purpose selection and questioning)
     - Produces: brownfield-analysis.md, ROADMAP.md, STATE.md, REQUIREMENTS.md
   - **Step 3** (line 249): Write PROJECT.md (Brownfield)
     - Reads ARCHITECTURE.md and STACK.md
     - Writes Validated requirements from existing capabilities
     - Adds Codebase Mode: brownfield, Primary Language, analysis reference
     - Commits PROJECT.md
   - **Step 4** (line 274): Jump to Phase 5
     - "Brownfield pipeline complete. Continuing to workflow preferences..."
     - Explicit skip list: Phases 3, 4, 6, 7, 8

4. **Guard before Phase 3** (line 287)
   - `If MODE == "brownfield": Skip to Phase 5` -- triggered, skips Phase 3

5. **Phase 5: Workflow Preferences** (line 435)
   - Same 8 questions as greenfield
   - config.json written and committed

6. **Phase 5.5: Effort Level** (line 575)
   - Same as greenfield

7. **Phase 6: Research Decision** (line 580)
   - Line 582: Guard triggered -- "Skip this phase. Brownfield analysis serves as domain research. Continue to Phase 10 (Done)."

8. **Phase 7: Define Requirements** (line 827)
   - Line 829: Guard triggered -- "Skip this phase. brownfield-flow already produced REQUIREMENTS.md."

9. **Phase 8: Create Roadmap** (line 972)
   - Line 974: Guard triggered -- "Skip this phase. brownfield-flow already produced ROADMAP.md."

10. **Phase 10: Done** (line 1116)
    - Dynamic banner shows: Project, Config, **Analysis** (brownfield-analysis.md exists), Requirements, Roadmap
    - Research row NOT shown (no .planning/research/ in brownfield)
    - Line 1142: "Brownfield analysis and purpose routing complete."
    - Next step: `/gsd:discuss-phase 1`

**Verdict:** Brownfield path is clean end-to-end. All inline, no exit-and-return. Convergence at Phase 5, skip through 6-8 via guards, dynamic Done banner.

## Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `/gsd:new-project` 실행 시 코드가 존재하면 자동으로 map-codebase 실행 후 brownfield-flow 워크플로우로 위임된다. | PASS | Phase 1 detection sets MODE=brownfield -> Phase 2 routes to Phase 2B -> Step 1 runs map-codebase inline -> Step 2 runs brownfield-flow inline. All automatic, no user decision needed for routing. |
| 2 | 코드가 없는 프로젝트에서 `/gsd:new-project` 실행 시 기존 그린필드 워크플로우가 변경 없이 동작한다(회귀 없음). | PASS | Greenfield path trace confirms: MODE=greenfield -> silent Phase 2 -> Phase 3 unchanged -> Phase 4 unchanged -> Phase 5 unchanged -> Phase 6-8 unchanged (guards not triggered) -> Phase 10 unchanged. execution_context has no brownfield references. |
| 3 | 브라운필드 경로의 Phase 2-4가 완료된 후 Phase 5+(config, research, requirements, roadmap)에서 그린필드 경로와 합류한다. | PASS | Brownfield converges at Phase 5 (Workflow Preferences), which is shared between both paths. Phase 6-8 are skipped via guards (brownfield-flow already produced those artifacts). Phase 10 is shared with dynamic banner. |

## Issues

**Minor observation (not a blocker):** The brownfield Phase 6 guard (line 582) says "Continue to Phase 10 (Done)" while the document has Phases 7 and 8 between Phase 6 and Phase 10. Since the guard instructs to skip directly to Phase 10, and Phases 7 and 8 also have their own guards, this is redundant but safe. An LLM reading sequentially would hit all three guards and correctly arrive at Phase 10. No functional issue.

**Minor observation (not a blocker):** There are two guard statements for Phase 3 -- one at line 287 (end of Phase 2B Step 4 section) and one at line 291 (start of Phase 3). This is intentional redundancy per the plan ("guard instruction before Phase 3"). Both serve the same purpose and reinforce the skip behavior.

No functional issues found.

## Human Verification

The following items cannot be verified by static code reading alone and require human testing:

1. **End-to-end greenfield test:** Run `/gsd:new-project` in an empty directory and confirm the full questioning -> research -> requirements -> roadmap flow works without any brownfield artifacts or messages appearing.

2. **End-to-end brownfield test:** Run `/gsd:new-project` in a directory with an existing codebase (>10 files, package.json, >10 commits) and confirm: map-codebase runs automatically, brownfield-flow runs with purpose routing, PROJECT.md has Validated requirements, and Phases 3/4/6/7/8 are correctly skipped.

3. **Scaffolded test:** Run `/gsd:new-project` in a directory with a freshly scaffolded project (e.g., `npx create-next-app`) and confirm it shows the informational message and continues to greenfield Phase 3.

4. **INFRA-04 and STATE-03 traceability update:** REQUIREMENTS.md still shows INFRA-04 and STATE-03 as "Pending" (line 85-86). These should be updated to "Complete" after verification passes.
