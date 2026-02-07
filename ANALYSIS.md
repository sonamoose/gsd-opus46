# GSD-Opus 4.6 리팩토링 분석 보고서

## 분석 개요

- **분석 일자:** 2026-02-07
- **분석 도구:** Claude Code Plan Mode (effort: high)
- **분석 범위:**

| 디렉토리 | 파일 수 | 역할 |
|----------|---------|------|
| agents/ | 11 | 전문 에이전트 정의 |
| commands/gsd/ | 27 | 슬래시 커맨드 |
| get-shit-done/workflows/ | 12 | 워크플로우 오케스트레이션 |
| get-shit-done/references/ | 9 | 공통 참조 문서 |
| get-shit-done/templates/ | ~21 | 문서/설정 템플릿 |
| hooks/ | 2 | Claude Code 훅 |
| **합계** | **~82** | |

- **판단 기준:** Opus 4.6 네이티브 기능 (Compaction API, Agent Teams, Adaptive Thinking/effort level)


## 결론 요약

| 분류 | 설명 | 영향 파일 수 |
|------|------|-------------|
| **제거** | Opus 4.6이 완전 대체 — 코드 삭제 | ~30개 파일의 특정 부분 |
| **수정** | Opus 4.6으로 보강 — 코드 변경 | ~10개 파일 |
| **유지** | GSD 고유 가치 — 변경 없음 | ~50개 파일 |


---


## 1. GSD 코드베이스 아키텍처

### 1.1 디렉토리 구조

```
agents/                          # 에이전트 정의 (11개)
  gsd-planner.md                 #   계획 수립
  gsd-executor.md                #   코드 실행
  gsd-verifier.md                #   검증
  gsd-debugger.md                #   디버깅
  gsd-project-researcher.md      #   프로젝트 리서치
  gsd-phase-researcher.md        #   단계 리서치
  gsd-research-synthesizer.md    #   리서치 종합
  gsd-roadmapper.md              #   로드맵 생성
  gsd-codebase-mapper.md         #   코드베이스 분석
  gsd-plan-checker.md            #   계획 검증
  gsd-integration-checker.md     #   통합 검증

commands/gsd/                    # 슬래시 커맨드 (27개)
  new-project.md                 #   프로젝트 초기화
  discuss-phase.md               #   단계 논의
  plan-phase.md                  #   계획 수립
  execute-phase.md               #   실행
  verify-work.md                 #   검증
  progress.md                    #   진행 상황
  settings.md                    #   설정
  set-profile.md                 #   모델 프로필 전환
  quick.md                       #   빠른 작업
  debug.md                       #   디버깅
  help.md, pause-work.md, resume-work.md,
  map-codebase.md, add-phase.md, insert-phase.md,
  remove-phase.md, add-todo.md, check-todos.md,
  audit-milestone.md, complete-milestone.md,
  new-milestone.md, plan-milestone-gaps.md,
  research-phase.md, list-phase-assumptions.md,
  join-discord.md, update.md

get-shit-done/
  workflows/                     # 워크플로우 상세 로직 (12개)
    execute-phase.md, execute-plan.md, verify-work.md,
    map-codebase.md, discuss-phase.md, transition.md,
    resume-project.md, complete-milestone.md,
    verify-phase.md, discovery-phase.md,
    list-phase-assumptions.md, diagnose-issues.md

  references/                    # 공통 참조 문서 (9개)
    model-profiles.md            #   모델 프로필 정의
    continuation-format.md       #   "Next Up" 포맷
    git-integration.md           #   Git 규칙
    checkpoints.md               #   체크포인트 프로토콜
    tdd.md                       #   TDD 가이드
    ui-brand.md, questioning.md,
    planning-config.md, verification-patterns.md

  templates/                     # 문서 템플릿 (~21개)
    project.md, state.md, roadmap.md, config.json,
    context.md, phase-prompt.md, summary.md,
    requirements.md, DEBUG.md, UAT.md, ...

hooks/                           # Claude Code 훅 (2개)
  gsd-statusline.js              #   상태줄 표시
  gsd-check-update.js            #   업데이트 확인
```

### 1.2 실행 흐름

```
사용자 → /gsd:커맨드 (commands/)
           → 워크플로우 위임 (workflows/)
              → Task() 호출로 에이전트 스폰 (agents/)
                 → 참조 문서 참고 (references/)
                 → 템플릿으로 문서 생성 (templates/)
                 → .planning/ 디렉토리에 상태 기록
```

### 1.3 핵심 의존관계

- **continuation-format.md**: 20+ 파일이 이 포맷을 참조 ("Next Up" 블록의 `/clear` 패턴)
- **model-profiles.md**: 12개 커맨드/워크플로우가 resolve_model_profile 보일러플레이트 사용
- **config.json 템플릿**: model_profile, workflow 토글, 병렬화 설정 보유


---


## 2. 제거 대상: Opus 4.6이 완전 대체하는 기능

### 2.1 Context Rot 강제 대응 → Compaction API

Opus 4.6은 Compaction API로 컨텍스트를 자동 관리한다.
`/clear` 강제 + 수동 비율 관리는 불필요하다.

#### 2.1.1 "/clear → fresh context" 강제 패턴

모든 "Next Up" 블록에 포함된 `<sub>/clear first → fresh context window</sub>` 패턴.

| 파일 | 행 | 조치 |
|------|-----|------|
| **references/continuation-format.md** | 16, 32, 49, 74, 96, 125, 154, 174, 216, 222, 227 | 전체 수정: /clear 패턴을 제거하고 포맷 갱신 |
| **workflows/transition.md** | 453, 500 | 해당 행 제거 |
| **workflows/discuss-phase.md** | 381 | 해당 행 제거 |
| **workflows/execute-phase.md** | 583, 641 | 해당 행 제거 |
| **workflows/execute-plan.md** | 219, 1726, 1787, 1825 | 해당 행 제거 |
| **workflows/map-codebase.md** | 4, 11, 332 | 해당 행 제거 |
| **workflows/verify-work.md** | 2, 541 | 해당 행 수정 |
| **workflows/resume-project.md** | 221, 235 | 해당 행 제거 |
| **workflows/complete-milestone.md** | 841 | 해당 행 제거 |
| **commands/gsd/execute-phase.md** | 171, 202, 237 | 해당 행 제거 |
| **commands/gsd/verify-work.md** | 53, 95, 126, 161 | 해당 행 제거 |
| **commands/gsd/progress.md** | 167, 190, 206, 232, 279, 307, 338 | 해당 행 제거 (7곳) |
| **commands/gsd/plan-phase.md** | 28, 543 | 해당 행 제거 |
| **commands/gsd/help.md** | 239, 430, 432, 454, 472 | 해당 행 제거 |
| **commands/gsd/new-project.md** | 958 | 해당 행 제거 |
| **commands/gsd/audit-milestone.md** | 186, 223, 265 | 해당 행 제거 |
| **commands/gsd/add-phase.md** | 175 | 해당 행 제거 |
| **commands/gsd/insert-phase.md** | 194 | 해당 행 제거 |
| **commands/gsd/plan-milestone-gaps.md** | 193 | 해당 행 제거 |
| **commands/gsd/new-milestone.md** | 693 | 해당 행 제거 |
| **commands/gsd/check-todos.md** | 158 | 해당 행 수정 |
| **agents/gsd-planner.md** | 1308 | 해당 행 제거 |
| **agents/gsd-debugger.md** | 812, 897, 1199 | 수정: /clear → /compact 또는 제거 |
| **templates/DEBUG.md** | 35, 71, 84, 138 | 수정: /clear → /compact |
| **templates/UAT.md** | 159 | 수정: /clear → /compact |
| **GSD-STYLE.md** | 12, 240, 342 | "Fresh Context Pattern" 섹션 제거 |
| **references/ui-brand.md** | 113 | 해당 행 제거 |
| **README.md** | 7, 240, 255, 389 | "Solves context rot" 설명 수정 |

**총 영향: 28개 파일, 약 80곳**

#### 2.1.2 컨텍스트 비율 관리 규칙

"~50% context", "30-40% 유지" 같은 수동 비율 관리.

| 파일 | 행 | 내용 | 조치 |
|------|-----|------|------|
| **agents/gsd-planner.md** | 82-94 | Quality Degradation Curve 테이블 | 제거 |
| **agents/gsd-planner.md** | 346-362 | Context Budget Rules (~50%) | 제거 (태스크 수 제한 2-3개는 유지) |
| **agents/gsd-planner.md** | 823 | TDD ~40% context | 제거 |
| **agents/gsd-planner.md** | 1194, 1210, 1399 | ~50% context 언급 | 제거 |
| **agents/gsd-plan-checker.md** | 204, 627 | ~50%/~70%/80%+ 검사, ~80% 경고 | 제거 |
| **templates/phase-prompt.md** | 240, 466 | ~50% context usage maximum | 제거 |
| **references/tdd.md** | 253 | ~40% context usage | 제거 |
| **commands/gsd/quick.md** | 160 | ~30% context usage | 제거 |
| **commands/gsd/execute-phase.md** | 22 | Context budget: ~15% | 제거 |
| **workflows/execute-plan.md** | 172, 219 | ~5%, ~15% usage | 제거 |
| **README.md** | 389 | 30-40% 유지 설명 | 수정 |

**총 영향: 11개 파일, 약 20곳**

#### 2.1.3 Statusline 컨텍스트 임계값 로직

| 파일 | 행 | 내용 | 조치 |
|------|-----|------|------|
| **hooks/gsd-statusline.js** | 21-43 | 80% 스케일링, 63/81/95% 색상 임계값 | 경량화 |

### 2.2 Model Profile 시스템 → effort level (low/medium/high)

Opus 4.6은 `/model` 슬라이더 또는 `CLAUDE_CODE_EFFORT_LEVEL` 환경변수로 사고 깊이를 조절한다.
GSD의 quality/balanced/budget 모델 프로필 시스템은 대체 가능하다.

#### 2.2.1 프로필 정의 및 전환 커맨드

| 파일 | 내용 | 조치 |
|------|------|------|
| **references/model-profiles.md** | 전체 (74행) — 프로필 정의, 철학, 해소 로직 | 제거 또는 effort-profiles.md로 대체 |
| **commands/gsd/set-profile.md** | 전체 — quality/balanced/budget 전환 | 제거 또는 effort 기반으로 대체 |

#### 2.2.2 resolve_model_profile 보일러플레이트

12개 커맨드/워크플로우에 동일한 패턴이 반복된다:

```bash
MODEL_PROFILE=$(cat .planning/config.json 2>/dev/null | grep -o '"model_profile"...' || echo "balanced")
```

| 파일 | 행 | 조치 |
|------|-----|------|
| **commands/gsd/execute-phase.md** | 41-57 | 수정: effort 기반으로 변경 |
| **commands/gsd/plan-phase.md** | 45-69 | 수정 |
| **commands/gsd/quick.md** | 37-54 | 수정 |
| **commands/gsd/debug.md** | 31-47 | 수정 |
| **commands/gsd/research-phase.md** | 34-50 | 수정 |
| **commands/gsd/new-project.md** | 346, 379-397 | 수정 |
| **commands/gsd/new-milestone.md** | 125-143 | 수정 |
| **commands/gsd/audit-milestone.md** | 42-58 | 수정 |
| **workflows/execute-phase.md** | 16-33 | 수정 |
| **workflows/execute-plan.md** | 14-29 | 수정 |
| **workflows/map-codebase.md** | 25-40 | 수정 |
| **workflows/verify-work.md** | 23-39 | 수정 |

#### 2.2.3 기타 model_profile 참조

| 파일 | 행 | 조치 |
|------|-----|------|
| **commands/gsd/settings.md** | 30, 50, 118, 143, 152, 163 | 수정: effort 설정으로 변경 |
| **commands/gsd/progress.md** | 55, 84 | 수정 |
| **commands/gsd/help.md** | 311, 316, 323 | 수정 |
| **README.md** | 470, 503 | 수정 |
| **templates/config.json** | model_profile 필드 | 수정 |

**총 영향: ~18개 파일**


---


## 3. 수정 대상: Opus 4.6으로 보강 가능한 기능

### 3.1 Orchestrator 병렬 실행 → Agent Teams 선택적 활용

GSD는 Task() 패턴으로 서브에이전트를 스폰한다. Opus 4.6 Agent Teams는 독립 세션 간
병렬 실행 + 공유 태스크 리스트를 네이티브 지원한다.

**수정 방향:** Task() 패턴을 기본으로 유지하되, Agent Teams를 선택적으로 활용하는 분기 추가.

| 구분 | Agent Teams 활용 가능 (병렬) | 기존 Task() 유지 (순차) |
|------|---------------------------|----------------------|
| 대상 | map-codebase 4개 영역 동시 분석 | discuss → plan → execute → verify 순서 |
| | execute-phase 같은 wave 내 독립 플랜 | plan-checker 검증 후 수정 루프 |
| | 병렬 디버그 스폰 | 의존성 있는 태스크 체인 |

| 파일 | 수정 내용 |
|------|-----------|
| **commands/gsd/execute-phase.md** | CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 분기 추가 |
| **commands/gsd/map-codebase.md** | Agent Teams 병렬 옵션 추가 |
| **workflows/execute-phase.md** | 같은 wave 내 Agent Teams 옵션 |
| **templates/config.json** | agent_teams 설정 필드 추가 |

### 3.2 Debug File Protocol → Compaction 활용

GSD 디버거는 /clear 후 재개를 위해 디버그 파일에 상태를 기록한다.
Compaction으로 /clear 빈도가 줄지만, 디버그 파일 자체는 장시간 세션에서 여전히 유용하다.

| 파일 | 행 | 수정 내용 |
|------|-----|-----------|
| **agents/gsd-debugger.md** | 812, 897 | "/clear" → "/compact" |
| **templates/DEBUG.md** | 35, 71, 84, 138 | "/clear" → "/compact" |


---


## 4. 유지 대상: GSD 고유 가치

Opus 4.6에 동등한 기능이 없으며, GSD만의 핵심 차별점.

### 4.1 파일 기반 상태 관리 (.planning/ 디렉토리)

세션 간 프로젝트 상태가 파일로 영속된다. Agent Teams에는 이런 구조가 없다.

- `.planning/PROJECT.md` — 프로젝트 비전, 핵심 가치, 제약 조건
- `.planning/ROADMAP.md` — 마일스톤/단계 계획, 요구사항 매핑
- `.planning/STATE.md` — 현재 진행 상태, 누적 결정, 블로커
- `.planning/CONTEXT.md` — 사용자 구현 의도 (locked/deferred/discretionary)
- `.planning/config.json` — 설정 (워크플로우 토글, 병렬화)
- `.planning/phases/` — 단계별 PLAN.md, SUMMARY.md, VERIFICATION.md
- `.planning/codebase/` — 코드베이스 분석 문서
- `.planning/debug/` — 디버그 세션 기록

**관련 템플릿:** templates/ 전체 (~21개 파일)

### 4.2 개발 방법론 규율

#### 워크플로우 강제 순서

discuss → plan → execute → verify. 순서를 건너뛸 수 없다.

- `commands/gsd/discuss-phase.md` — 사용자 의도 수집, CONTEXT.md 생성
- `commands/gsd/plan-phase.md` — 리서치 → 계획 수립 → 계획 검증
- `commands/gsd/execute-phase.md` — wave별 병렬/순차 실행
- `commands/gsd/verify-work.md` — UAT + Goal-backward 검증

#### Goal-Backward Verification (3-level 아티팩트 검증)

1. **Exists** — 파일 존재 여부
2. **Substantive** — 실제 구현인지 stub인지 (최소 행 수, stub 패턴 탐지)
3. **Wired** — 시스템에 연결되었는지 (import, 사용 여부)

핵심 파일: `agents/gsd-verifier.md`, `agents/gsd-plan-checker.md`

#### Atomic Commit 규칙

태스크 1개 = 커밋 1개. 형식: `{type}({phase}-{plan}): {description}`

핵심 파일: `agents/gsd-executor.md`, `references/git-integration.md`

#### Checkpoint Protocol

- human-verify (90%) — 자동화 후 사용자 확인
- decision (9%) — 아키텍처 선택 필요
- human-action (1%) — 불가피한 수동 작업

핵심 파일: `agents/gsd-executor.md`, `references/checkpoints.md`

#### Deviation Rules (실행자 자율성 규칙 1-4)

- Rule 1: 버그 자동 수정
- Rule 2: 누락된 필수 기능 자동 추가
- Rule 3: 블로킹 이슈 자동 해결
- Rule 4: 아키텍처 변경은 중단 후 사용자 결정

핵심 파일: `agents/gsd-executor.md`

#### Discovery Protocol (리서치 레벨 0-3)

- Level 0: 건너뛰기 (기존 패턴 활용)
- Level 1: 빠른 검증 (2-5분)
- Level 2: 표준 리서치 (15-30분)
- Level 3: 심층 분석 (1시간+)

핵심 파일: `agents/gsd-planner.md` 114-149행

### 4.3 프로젝트 관리

- **Brownfield/Greenfield 접근법:** `commands/gsd/new-project.md`, `commands/gsd/map-codebase.md`
- **마일스톤 관리:** `commands/gsd/new-milestone.md`, `complete-milestone.md`, `audit-milestone.md`
- **DECISIONS.md:** 의사결정 영속 기록
- **TDD 통합:** `agents/gsd-planner.md` 750-832행, `references/tdd.md`


---


## 5. 과제별 수정 매핑

### 과제 2: Context Rot 대응 코드 경량화

| 분류 | 대상 | 파일 수 | 수정 위치 |
|------|------|---------|-----------|
| 제거 | "/clear → fresh context" 패턴 | 28 | ~80곳 |
| 제거 | 컨텍스트 비율 규칙 (~50%, ~30%) | 11 | ~20곳 |
| 경량화 | statusline 임계값 | 1 | hooks/gsd-statusline.js |
| **예상 난이도** | **medium** | | |

### 과제 3: Orchestrator를 Agent Teams 호환으로 수정

| 대상 | 파일 |
|------|------|
| Agent Teams 분기 추가 | commands/gsd/execute-phase.md |
| Agent Teams 병렬 옵션 | commands/gsd/map-codebase.md |
| 워크플로우 수정 | workflows/execute-phase.md |
| 설정 추가 | templates/config.json |
| **예상 난이도** | **high** |

### 과제 4: Adaptive Thinking 기반 effort 자동 조절

| 대상 | 파일 수 |
|------|---------|
| model-profiles.md → effort 기반 대체 | 1 |
| set-profile.md → effort 전환 대체 | 1 |
| resolve_model_profile 보일러플레이트 수정 | 12 |
| 에이전트별 권장 effort 추가 | 11 |
| config.json effort 설정 추가 | 1 |
| settings/help/progress 참조 수정 | 4 |
| **예상 난이도** | **medium** |

### 과제 5: Opus 4.6 전용 슬래시 커맨드 생성

| 신규 파일 | 용도 |
|-----------|------|
| .claude/commands/gsd:team-review.md | Agent Teams 병렬 코드 리뷰 |
| .claude/commands/gsd:effort-report.md | effort 사용 패턴 분석 |
| .claude/commands/gsd:compact-state.md | Compaction 기반 상태 요약 |
| **예상 난이도** | **medium** |

### 과제 6: 자동화 Hooks 추가

| 신규/수정 | 파일 | 용도 |
|-----------|------|------|
| 신규 | SessionStart hook | STATE.md 자동 로딩 |
| 신규 | PostToolUse hook | 자동 검증 |
| 통합 | hooks/gsd-statusline.js | 기존 훅과 충돌 방지 |
| **예상 난이도** | **medium** |

### 과제 7: GSD 분석 Skills 만들기

| 신규 파일 | 용도 |
|-----------|------|
| .claude/skills/gsd-analyzer/SKILL.md | .planning/ 상태 분석 |
| .claude/skills/opus46-advisor/SKILL.md | Opus 4.6 기능 추천 |
| **예상 난이도** | **medium** |

### 과제 8: 전체 리팩토링 결과 검증

| 대상 | 내용 |
|------|------|
| Agent Teams 병렬 검증 | 3개 에이전트 스폰 |
| 커밋 히스토리 리뷰 | atomic commit 확인 |
| CHANGELOG.md 작성 | 전체 변경 사항 정리 |
| **예상 난이도** | **high** |


---


## 6. 과제 의존성 그래프

```
과제 1 (분석) ── 완료
  │
  └── 과제 2 (Context Rot 경량화)
        │
        ├── 과제 3 (Agent Teams 호환)
        ├── 과제 4 (effort 자동 조절)
        └── 과제 6 (Hooks 추가)
              │
              ├── 과제 5 (커맨드 생성) ← 과제 3, 4에도 의존
              │
              └── 과제 7 (Skills 생성) ← 과제 4, 5에도 의존
                    │
                    └── 과제 8 (최종 검증) ← 과제 2~7 전부 완료 후
```

**권장 실행 순서:** 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8


---


## 7. 참고 문서

| 주제 | Claude Code 문서 경로 |
|------|----------------------|
| Compaction/Extended Thinking | tutor/claude-code-tutor/docs/claude_code_docs/common-workflows.md |
| Agent Teams | tutor/claude-code-tutor/docs/claude_code_docs/agent-teams.md |
| Sub-agents | tutor/claude-code-tutor/docs/claude_code_docs/sub-agents.md |
| effort level | tutor/claude-code-tutor/docs/claude_code_docs/model-config.md |
| Skills | tutor/claude-code-tutor/docs/claude_code_docs/skills.md |
| Hooks | tutor/claude-code-tutor/docs/claude_code_docs/hooks.md |
| settings.json | tutor/claude-code-tutor/docs/claude_code_docs/settings.md |
