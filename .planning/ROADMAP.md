# Roadmap: GSD-Opus46 모드 분기 개선

**Version:** v1.0
**Phases:** 5
**Requirements:** 19 mapped

## Milestone 1: v1.0 — Brownfield Mode

### Phase 1: Foundation (템플릿 + 에이전트 + 감지 로직)
**Goal:** 브라운필드 분석의 기반 컴포넌트(템플릿, 에이전트 정의, 모드 감지 로직)를 생성하여 이후 파이프라인의 토대를 마련한다.
**Requirements:** DETECT-01, DETECT-02, DETECT-03, DETECT-04, INFRA-01, INFRA-03
**Plans:** 3 plans

Plans:
- [x] 01-01-PLAN.md — brownfield-summary.md 분석 요약 출력 템플릿 생성
- [x] 01-02-PLAN.md — gsd-brownfield-analyzer.md 코드베이스 분석 에이전트 정의
- [x] 01-03-PLAN.md — 모드 감지 로직 사양 (다중 시그널 + 언어 감지 + 스캐폴딩 다운그레이드)

**Artifacts:**
- `get-shit-done/templates/brownfield-summary.md` (NEW)
- `agents/gsd-brownfield-analyzer.md` (NEW)
- `get-shit-done/references/brownfield-detection.md` (NEW)

**Success Criteria:**
1. `brownfield-summary.md` 템플릿이 7개 코드베이스 문서 영역(Architecture, Stack, Concerns, Testing, Structure, Integrations, Conventions)을 구조화된 섹션으로 정의한다.
2. `gsd-brownfield-analyzer` 에이전트가 `.planning/codebase/*.md` 7개 문서를 읽고 `brownfield-summary.md` 템플릿에 따라 `.planning/brownfield-analysis.md`를 작성한다.
3. 모드 감지 로직이 코드 파일, 패키지 매니저, git 히스토리, 디렉토리 구조 등 다중 시그널을 복합적으로 판단하여 브라운필드/그린필드를 자동 구분한다.
4. JS/TS, Python, Go, Rust, Java, Swift 등 주요 언어가 자동 판별되고, 스캐폴딩 프로젝트(CRA, Next.js init 등)는 그린필드로 그레이스풀 다운그레이드된다.

---

### Phase 2: Analysis Pipeline (워크플로우 + 분석 기능)
**Goal:** 브라운필드 분석 워크플로우를 생성하여 4방면 병렬 분석, 요약 대시보드, 문제점 우선순위 랭킹, 영역 스코프 분석을 구현한다.
**Requirements:** ANALYSIS-01, ANALYSIS-02, ANALYSIS-03, ANALYSIS-04, INFRA-02
**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md — brownfield-analyzer 에이전트 강화 (심각도 분류 기준 + 영역 스코프 분석 로직)
- [x] 02-02-PLAN.md — brownfield-flow.md 분석 파이프라인 워크플로우 생성

**Artifacts:**
- `get-shit-done/workflows/brownfield-flow.md` (NEW)
- `agents/gsd-brownfield-analyzer.md` (MODIFIED — severity classification + scoped analysis)

**Success Criteria:**
1. `brownfield-flow.md` 워크플로우가 분석→요약→결정→실행 파이프라인을 오케스트레이션하며, `brownfield-analyzer` 에이전트를 Task()로 스폰한다.
2. 4방면 병렬 분석(구조/아키텍처, 기술 스택, 문제점/기술부채, 테스트 상태)이 7개 코드베이스 문서로부터 종합적으로 수행된다.
3. 분석 결과가 사용자 친화적 요약 대시보드로 10줄 이내에 제시되며, 문제점이 critical/moderate/minor로 분류되어 중요도순 정렬된다.
4. 특정 서브디렉토리만 집중 분석하는 영역 스코프 옵션이 제공된다.

---

### Phase 3: Purpose Routing (목적 라우팅 + 질문 흐름)
**Goal:** 분석 결과를 기반으로 사용자 목적(버그 수정/기능 개선/리팩토링)을 확인하고, 목적별 맞춤 질문 흐름과 로드맵 자동 생성을 구현한다.
**Requirements:** ROUTE-01, ROUTE-02, ROUTE-03, ROUTE-04
**Plans:** 3 plans

Plans:
- [x] 03-01-PLAN.md — brownfield-questioning.md 목적별 질문 흐름 레퍼런스 생성
- [x] 03-02-PLAN.md — brownfield-roadmap.md 목적 인식 로드맵 템플릿 생성
- [x] 03-03-PLAN.md — brownfield-flow.md 확장 (Steps 6-9: 목적 선택, 질문, 디버그 브릿징, 로드맵 생성)

**Artifacts:**
- `get-shit-done/references/brownfield-questioning.md` (NEW)
- `get-shit-done/templates/brownfield-roadmap.md` (NEW)
- `get-shit-done/workflows/brownfield-flow.md` (MODIFIED — Steps 6-9 추가)

**Success Criteria:**
1. 분석 요약 제시 후 사용자가 '버그 수정', '기능 개선', '리팩토링', '기타' 중 목적을 선택할 수 있다.
2. 수정 모드에서는 CONCERNS.md 기반 증상/기대 동작 질문이, 개선 모드에서는 아키텍처 적합성/제약 조건 질문이 각각 다른 스레드로 진행된다.
3. CONCERNS.md 발견사항이 디버그 세션에 자동 프리필되어 문제점-디버그 브릿징이 동작한다.
4. 수정 목적은 심각도순, 개선 목적은 의존성순으로 로드맵이 자동 생성된다.

---

### Phase 4: Command Integration (new-project.md 수정)
**Goal:** `new-project.md` 커맨드에 브라운필드 분기 로직을 통합하여, 사용자가 `/gsd:new-project`만 실행하면 자동으로 최적 흐름이 적용되게 한다.
**Requirements:** INFRA-04, STATE-03
**Plans:** 2 plans

Plans:
- [x] 04-01-PLAN.md — 감지 로직 업그레이드 (Phase 1 Step 3) + MODE 기반 3분기 라우팅 (Phase 2)
- [x] 04-02-PLAN.md — 브라운필드 파이프라인 (Phase 2B) + 수렴 가드 (Phases 6-8) + 동적 완료 배너 (Phase 10)

**Artifacts:**
- `commands/gsd/new-project.md` (MODIFIED)

**Success Criteria:**
1. `/gsd:new-project` 실행 시 코드가 존재하면 자동으로 map-codebase 실행 후 brownfield-flow 워크플로우로 위임된다.
2. 코드가 없는 프로젝트에서 `/gsd:new-project` 실행 시 기존 그린필드 워크플로우가 변경 없이 동작한다(회귀 없음).
3. 브라운필드 경로의 Phase 2-4가 완료된 후 Phase 5+(config, research, requirements, roadmap)에서 그린필드 경로와 합류한다.

---

### Phase 5: State Integration + Polish (상태 관리 + 컨텍스트 전파)
**Goal:** 브라운필드 분석 컨텍스트가 PROJECT.md와 STATE.md를 통해 다운스트림 에이전트(planner, executor)에 전달되도록 상태 관리를 완성한다.
**Requirements:** STATE-01, STATE-02
**Plans:** 2 plans

Plans:
- [ ] 05-01-PLAN.md — project.md/state.md 템플릿에 Codebase Context 섹션 추가 + 브라운필드 가이던스 확장
- [ ] 05-02-PLAN.md — 브라운필드 컨텍스트 전파 체인 종단간 검증

**Artifacts:**
- `get-shit-done/templates/project.md` (MINOR UPDATE)
- `get-shit-done/templates/state.md` (MINOR UPDATE)
- Context propagation validation

**Success Criteria:**
1. 브라운필드 PROJECT.md에 기존 기능이 Validated 요구사항으로 자동 추론되어 기록된다(ARCHITECTURE.md, STACK.md 기반).
2. PROJECT.md의 Codebase Mode 섹션과 분석 참조가 gsd-planner와 gsd-executor에 의해 읽히고 계획/실행에 반영된다.
3. STATE.md에 코드베이스 컨텍스트 참조와 목적(purpose)이 기록되어 세션 간 상태가 유지된다.

---

## Phase-Requirement Coverage Matrix

| Requirement | Phase | Category |
|-------------|-------|----------|
| DETECT-01 | 1 | Mode Detection |
| DETECT-02 | 1 | Mode Detection |
| DETECT-03 | 1 | Mode Detection |
| DETECT-04 | 1 | Mode Detection |
| INFRA-01 | 1 | Infrastructure |
| INFRA-03 | 1 | Infrastructure |
| ANALYSIS-01 | 2 | Codebase Analysis |
| ANALYSIS-02 | 2 | Codebase Analysis |
| ANALYSIS-03 | 2 | Codebase Analysis |
| ANALYSIS-04 | 2 | Codebase Analysis |
| INFRA-02 | 2 | Infrastructure |
| ROUTE-01 | 3 | Purpose Routing |
| ROUTE-02 | 3 | Purpose Routing |
| ROUTE-03 | 3 | Purpose Routing |
| ROUTE-04 | 3 | Purpose Routing |
| INFRA-04 | 4 | Infrastructure |
| STATE-03 | 4 | State Management |
| STATE-01 | 5 | State Management |
| STATE-02 | 5 | State Management |

**Coverage:** 19/19 v1 requirements mapped. 0 unmapped.

## Build Dependencies

```
Phase 1: Foundation          (no dependencies — leaf nodes)
    │
    ▼
Phase 2: Analysis Pipeline   (depends on Phase 1 agent + template)
    │
    ▼
Phase 3: Purpose Routing     (depends on Phase 2 workflow)
    │
    ▼
Phase 4: Command Integration (depends on Phase 2-3 workflow completion)
    │
    ▼
Phase 5: State Integration   (depends on Phase 4 command producing brownfield PROJECT.md)
```

**Rationale:** ARCHITECTURE.md 연구의 빌드 의존성 그래프에 따라, 감지 정확도(신뢰 기반) → 분석 품질(가치 계층) → 워크플로우 라우팅(사용자 경험) → 통합(진입점) → 상태 전파(완성도) 순으로 구성.

---
*Roadmap created: 2026-02-08*
*Based on: REQUIREMENTS.md (19 v1 requirements), ARCHITECTURE.md (build order), SUMMARY.md (research findings)*
