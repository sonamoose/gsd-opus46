# GSD Opus 4.6 리팩토링 분석 (Revised)

> 소크라틱 방식으로 축별 스캔 → 사용자 검증을 거쳐 작성됨.
> 각 축의 분류와 근거는 사용자의 명시적 동의를 받은 것임.
> 과제 2~4의 실제 수행 결과와 대조 검증 완료.


## 분석 방법론

1. original/ 전체 82개 파일을 패턴별로 grep 스캔
2. 발견된 패턴을 7개 축으로 분류
3. 각 축을 사용자에게 제시하고 검증 (동의/수정/추가질문)
4. 검증된 결과만 이 문서에 기록
5. 과제 2~4 실제 커밋 이력과 대조하여 정합성 확인


---


## 축 1: Context Management — 제거

**패턴:** `/clear` 강제, 컨텍스트 비율 관리, "30-40% 이하 유지" 규칙
**스캔 규모:** 79건 (context 관련) + 40건 (fresh context 관련), 31+12개 파일
**Opus 4.6 대체 기능:** Compaction API

- auto-compact가 자동으로 컨텍스트 관리
- `/clear` 강제 대신 필요 시 `/compact` 사용
- 퍼센트 기반 수동 비율 관리 불필요

**조치:** 강제 `/clear` 호출, 컨텍스트 비율 임계값 규칙, 수동 컨텍스트 관리 코드 제거.

### 실제 수행 결과 (과제 2)

| 커밋 | 내용 | 파일 수 |
|------|------|---------|
| `c57c476` | /clear 강제 패턴과 fresh context 참조 제거 | 28 |
| `9079534` | 컨텍스트 비율 규칙 제거, statusline 3단계로 단순화 | 8 |

**주요 변경:**
- "Next Up" 블록의 `/clear first → fresh context window` 패턴 전체 제거
- Quality Degradation Curve, Context Budget Rules 등 퍼센트 기반 규칙 제거
- `fresh context` → `isolated context` 용어 변경
- statusline 임계값: 4단계(63/81/95%) → 3단계(80/95%, Compaction 안내)
- 구조적 제한(2-3 tasks/plan, split signals)은 유지


## 축 2: Model Profile System — 제거

**패턴:** `resolve_model_profile`, `model=` 파라미터, quality/balanced/budget 3단계 프로필
**스캔 규모:** 54건, 21개 파일
**Opus 4.6 대체 기능:** Effort Level

- `/model` 슬라이더 (화살표 키)로 세션 전체 effort 조절
- `CLAUDE_CODE_EFFORT_LEVEL` 환경변수
- `effortLevel` in settings.json
- 서브에이전트는 세션의 effort level을 자동 상속

**조치:** resolve_model_profile 보일러플레이트 제거, Task() 호출의 model= 파라미터 제거, 에이전트 파일에 권장 effort 수준만 주석으로 기록.

### 실제 수행 결과 (과제 4)

| 커밋 | 내용 | 파일 수 |
|------|------|---------|
| `774212d` | 11개 에이전트에 Recommended Effort Level 주석 추가 | 11 |
| `5fb9e34` | model-profiles.md → Effort Level Profiles, set-profile.md 삭제, set-effort.md 생성 | 3 |
| `78c3d68` | 대표 3개 파일의 resolve_model_profile 보일러플레이트 교체 | 3 |
| `ba3448a` | 나머지 13개 파일의 resolve_model_profile + 참조 파일 갱신 | 13 |
| `8e0e476` | 12개 파일에서 Task() 호출의 model= 파라미터 일괄 제거 | 12 |

**주요 변경:**
- MODEL_PROFILE bash 스크립트와 quality/balanced/budget 모델 룩업 테이블 전량 삭제
- 교체 텍스트: `Agents use the session's effort level set via /model or CLAUDE_CODE_EFFORT_LEVEL`
- 에이전트별 권장 effort: high(planner, plan-checker, debugger, research-synthesizer), medium(codebase-mapper, roadmapper, verifier, executor), low(project-researcher, phase-researcher, integration-checker)
- set-profile.md 삭제 → set-effort.md 신규 생성


## 축 3: Sub-agent Orchestration — 유지 (분류 명확화)

**패턴:** Task() 호출, 오케스트레이션 로직, 병렬 실행 관리
**스캔 규모:** 245건, 35개 파일

**핵심 분류:**

| 구성 요소 | 분류 | 이유 |
|-----------|------|------|
| Task() 자체 | Claude Code 네이티브 도구 | GSD가 만든 것이 아님, 분석 범위 밖 |
| 오케스트레이션 로직 | GSD 고유 가치 | 무엇을, 언제, 어떤 데이터로 스폰할지 결정하는 로직 |
| 병렬 실행 | Agent Teams 선택적 활용 | 환경변수 분기로 추가 |

**조치:** Task() 패턴 유지. 병렬 작업(wave 실행, map-codebase)에 한해 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 분기 추가. 순차 작업(discuss → plan → execute → verify)은 기존 방식 유지.

### 실제 수행 결과 (과제 3)

| 커밋 | 내용 | 파일 |
|------|------|------|
| `ac53c24` | commands/gsd/execute-phase.md에 Agent Teams 분기 추가 | 1 |
| `4b38489` | commands/gsd/map-codebase.md에 Agent Teams 분기 추가 | 1 |
| `c05ff5c` | workflows/execute-phase.md에 3단계 실행 분기 추가 | 1 |
| `7ef3efb` | templates/config.json에 agent_teams 설정 필드 추가 | 1 |

**주요 변경:**
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 환경변수 확인 로직
- execute-phase: Agent Teams 설정 시 독립 플랜을 팀원에게 위임
- map-codebase: Agent Teams 설정 시 4개 focus area를 공유 태스크로 등록
- workflows/execute-phase: 3단계 분기 (Agent Teams+병렬 / Task()병렬 / Task()순차)


## 축 4: Hooks 활용 — 강화

**현황:** 14개 Hook 이벤트 중 2개만 사용
**규모:** 2개 파일 (gsd-statusline.js, gsd-check-update.js)

현재 GSD의 Hook 사용:

| 파일 | 이벤트 | 용도 |
|------|--------|------|
| gsd-statusline.js | (statusline) | 모델, 태스크, 디렉토리, 컨텍스트 사용량 표시 |
| gsd-check-update.js | SessionStart | npm 업데이트 확인 (백그라운드) |

**강화 제안 (5개 Hook):**

| Hook 이벤트 | 용도 | 메커니즘 |
|-------------|------|----------|
| A. SessionStart | .planning/ 상태 자동 로딩 | additionalContext로 STATE.md 주입 |
| B. PreCompact | 컴팩션 전 상태 자동 저장 | auto 컴팩션 직전 STATE.md 업데이트 |
| C. SubagentStart | 서브에이전트에 프로젝트 컨텍스트 주입 | additionalContext로 핵심 정보 전달 |
| D. TaskCompleted | GSD 검증 규율 강제 | exit 2로 미검증 완료 차단 |
| E. Stop | 미커밋 변경 경고 | git status 감지, decision: "block" |

**조치:** 5개 Hook을 GSD 워크플로우 자동화에 추가. 나머지 이벤트(UserPromptSubmit, PostToolUse, PermissionRequest, Notification, SessionEnd 등)는 GSD 핵심 가치와 직접 연결되지 않아 우선순위 낮음.


## 축 5: Settings System — 정리

**패턴:** GSD 자체 config와 Claude Code settings가 혼재
**스캔 규모:** 170건, 46개 파일

**분류:**

| 설정 유형 | 위치 | 예시 |
|-----------|------|------|
| GSD 프로젝트 설정 | .planning/config.json | 페이즈 구조, 마일스톤, 워크플로우 토글 |
| Claude Code 설정 | .claude/settings.json | hooks, permissions, effortLevel |
| 중복 설정 | 양쪽에 존재 | model_profile (→ effort level로 통합됨) |

**조치:** GSD config와 Claude Code settings의 역할을 명확히 분리. 중복 설정(model profile)은 과제 4에서 Claude Code 네이티브(Effort Level)로 통합 완료.


## 축 6: File-based State (.planning/) — 유지

**패턴:** .planning/ 디렉토리 구조, PROJECT.md, ROADMAP.md, STATE.md
**스캔 규모:** 1,401건, 92개 파일

**GSD 고유 가치:**
- 세션 간 상태 영속성 (Agent Teams에 없는 기능)
- 사람이 읽을 수 있는 마크다운 형식
- Git으로 버전 관리 가능
- 프로젝트 전체 히스토리 추적

**조치:** 전면 유지. 이 구조는 GSD의 핵심 차별점.


## 축 7: Git/Atomic Commit — 유지

**패턴:** atomic commit 규칙, git 워크플로우, 커밋 전 검증
**스캔 규모:** 194건, 37개 파일

**GSD 고유 가치:**
- 작업 단위별 원자적 커밋 강제
- 커밋 메시지 규칙: `{type}({phase}-{plan}): {description}`
- 커밋 전 검증 체계
- 롤백 가능한 작업 히스토리

**조치:** 전면 유지. Claude Code에는 커밋 규율을 강제하는 기능이 없음.


---


## 요약 매트릭스

| 축 | 분류 | Opus 4.6 관련 기능 | 조치 |
|----|------|-------------------|------|
| 1. Context Management | 제거 | Compaction API | 강제 /clear, 비율 관리 코드 삭제 |
| 2. Model Profile | 제거 | Effort Level | resolve_model_profile, model= 삭제 |
| 3. Sub-agent Orchestration | 유지+수정 | Agent Teams | 병렬 작업에 선택적 분기 추가 |
| 4. Hooks | 강화 | Hooks (14 이벤트) | 5개 Hook 추가 |
| 5. Settings | 정리 | settings.json | GSD/Claude Code 설정 분리 |
| 6. File-based State | 유지 | — | GSD 고유 가치 |
| 7. Git/Atomic Commit | 유지 | — | GSD 고유 가치 |


## 커밋 이력 (과제 2~4 수행 완료)

| 커밋 | 과제 | 관련 축 | 내용 | 파일 수 |
|------|------|---------|------|---------|
| `39b6756` | 1 | 전체 | ANALYSIS.md 작성 | 1 |
| `c57c476` | 2 | 축1 | /clear 강제 패턴, fresh context 참조 제거 | 28 |
| `9079534` | 2 | 축1 | 컨텍스트 비율 규칙 제거, statusline 단순화 | 8 |
| `ac53c24` | 3 | 축3 | execute-phase에 Agent Teams 분기 | 1 |
| `4b38489` | 3 | 축3 | map-codebase에 Agent Teams 분기 | 1 |
| `c05ff5c` | 3 | 축3 | workflows/execute-phase에 Agent Teams 분기 | 1 |
| `7ef3efb` | 3 | 축3 | config.json에 agent_teams 설정 | 1 |
| `774212d` | 4 | 축2 | 11개 에이전트에 Recommended Effort Level 추가 | 11 |
| `5fb9e34` | 4 | 축2 | model-profiles → Effort Level, set-effort.md 생성 | 3 |
| `78c3d68` | 4 | 축2 | 대표 3개 파일 resolve_model_profile 교체 | 3 |
| `ba3448a` | 4 | 축2 | 나머지 13개 파일 resolve_model_profile 교체 | 13 |
| `8e0e476` | 4 | 축2 | Task() 호출의 model= 파라미터 제거 | 12 |


## 과제 매핑

| 과제 | 관련 축 | 상태 |
|------|---------|------|
| 과제 1: 분석 | 전체 | 완료 (ANALYSIS.md + 이 문서) |
| 과제 2: Context Rot 경량화 | 축 1 | 완료 (2 커밋, 36 파일) |
| 과제 3: Agent Teams 호환 | 축 3 | 완료 (4 커밋, 4 파일) |
| 과제 4: Effort Level 자동 조절 | 축 2 | 완료 (5 커밋, 42 파일 변경) |
| 과제 5: 슬래시 커맨드 | 축 1, 2, 3 | 미진행 |
| 과제 6: Hooks 추가 | 축 4 | 미진행 |
| 과제 7: Skills | — | 미진행 |
| 과제 8: 전체 검증 | 전체 | 미진행 |
