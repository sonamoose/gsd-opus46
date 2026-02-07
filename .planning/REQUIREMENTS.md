# Requirements: GSD-Opus46 모드 분기 개선

**Defined:** 2026-02-08
**Core Value:** 코드 존재 여부에 따라 자동으로 최적의 워크플로우를 제공

## v1 Requirements

### Mode Detection (모드 감지)

- [ ] **DETECT-01**: 코드 파일과 패키지 매니저 존재 여부로 브라운필드/그린필드 자동 판단
- [ ] **DETECT-02**: 다중 시그널 감지 — 파일 수, 디렉토리 구조, git 히스토리 등 복합 판단으로 오탐 방지
- [ ] **DETECT-03**: 주요 언어 자동 판별 — JS/TS, Python, Go, Rust, Java, Swift 등 감지
- [ ] **DETECT-04**: 스캐폴딩 프로젝트 감지 시 그린필드로 그레이스풀 다운그레이드

### Codebase Analysis (코드베이스 분석)

- [ ] **ANALYSIS-01**: 4방면 병렬 분석 — 구조/아키텍처, 기술 스택, 문제점/기술부채, 테스트 상태
- [ ] **ANALYSIS-02**: 사용자 친화적 분석 요약 대시보드 — 7개 원문서를 10줄 이내로 요약 제시
- [ ] **ANALYSIS-03**: 문제점 우선순위 랭킹 — critical/moderate/minor 분류 및 중요도 순 정렬
- [ ] **ANALYSIS-04**: 영역 스코프 분석 — 특정 서브디렉토리만 집중 분석 옵션

### Purpose Routing (목적 라우팅)

- [ ] **ROUTE-01**: 분석 결과 확인 후 '버그 수정' vs '기능 개선' 목적 선택
- [ ] **ROUTE-02**: 목적별 맞춤 질문 흐름 — 수정 모드와 개선 모드에서 다른 질문 스레드
- [ ] **ROUTE-03**: 문제점-디버그 세션 브릿징 — CONCERNS.md 발견사항을 디버그 세션에 자동 프리필
- [ ] **ROUTE-04**: 분석 결과 기반 로드맵 자동 생성 — 수정은 심각도순, 개선은 의존성순 로드맵

### State Management (상태 관리)

- [ ] **STATE-01**: 브라운필드 PROJECT.md에 기존 기능을 Validated 요구사항으로 자동 추론
- [ ] **STATE-02**: 분석 컨텍스트가 다운스트림 워크플로우(planner, executor)에 전달
- [ ] **STATE-03**: 그린필드 워크플로우 무변경 보장 — 기존 동작 회귀 없음

### Infrastructure (인프라)

- [ ] **INFRA-01**: gsd-brownfield-analyzer 에이전트 생성 — 7개 코드베이스 문서를 종합 분석
- [ ] **INFRA-02**: brownfield-flow 워크플로우 생성 — 분석→결정→실행 파이프라인 오케스트레이션
- [ ] **INFRA-03**: brownfield-summary 템플릿 생성 — 분석 결과 요약 출력 구조 정의
- [ ] **INFRA-04**: new-project.md 커맨드 수정 — Phase 2-4에 브라운필드 분기 로직 통합

## v2 Requirements

### Incremental Analysis

- **INCR-01**: 수정 후 변경 영역만 재분석하여 개선 상태 비교
- **INCR-02**: Before/After 비교 — "이전: critical 3개 → 현재: critical 1개"

### Multi-Language Enhancement

- **LANG-01**: 언어별 맞춤 탐색 명령 세트 (Django, Rails, Spring 등 프레임워크별)
- **LANG-02**: 사용자 힌트 제공 — "이것은 Django 프로젝트입니다" 수동 지정

## Out of Scope

| Feature | Reason |
|---------|--------|
| 실시간 코드 모니터링 | GSD는 커맨드 기반 도구, 데몬 모드 부적합 |
| 자동 일괄 수정 적용 | 사용자 라우팅 없는 자동 수정은 위험 |
| ESLint/SonarQube 통합 | 외부 도구 의존성 추가 — AI 에이전트가 직접 분석 |
| CVE 취약점 스캐닝 | 전문 보안 도구 영역 (Snyk, Dependabot) |
| 크로스 리포지토리 분석 | 스코프 폭발 — 패키지별 개별 분석 권장 |
| 코드 품질 점수 (A-F) | 환원적 점수는 오해 유발 — 카테고리별 심각도 사용 |
| 별도 커맨드 분리 | /gsd:new-project 하나에서 내부 분기로 처리 |

## Traceability

| Requirement | Phase | Phase Name | Status |
|-------------|-------|------------|--------|
| DETECT-01 | Phase 1 | Foundation | Pending |
| DETECT-02 | Phase 1 | Foundation | Pending |
| DETECT-03 | Phase 1 | Foundation | Pending |
| DETECT-04 | Phase 1 | Foundation | Pending |
| INFRA-01 | Phase 1 | Foundation | Pending |
| INFRA-03 | Phase 1 | Foundation | Pending |
| ANALYSIS-01 | Phase 2 | Analysis Pipeline | Pending |
| ANALYSIS-02 | Phase 2 | Analysis Pipeline | Pending |
| ANALYSIS-03 | Phase 2 | Analysis Pipeline | Pending |
| ANALYSIS-04 | Phase 2 | Analysis Pipeline | Pending |
| INFRA-02 | Phase 2 | Analysis Pipeline | Pending |
| ROUTE-01 | Phase 3 | Purpose Routing | Pending |
| ROUTE-02 | Phase 3 | Purpose Routing | Pending |
| ROUTE-03 | Phase 3 | Purpose Routing | Pending |
| ROUTE-04 | Phase 3 | Purpose Routing | Pending |
| INFRA-04 | Phase 4 | Command Integration | Pending |
| STATE-03 | Phase 4 | Command Integration | Pending |
| STATE-01 | Phase 5 | State Integration | Pending |
| STATE-02 | Phase 5 | State Integration | Pending |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0 ✓

**Phase summary:**
- Phase 1 (Foundation): 6 requirements — DETECT-01~04, INFRA-01, INFRA-03
- Phase 2 (Analysis Pipeline): 5 requirements — ANALYSIS-01~04, INFRA-02
- Phase 3 (Purpose Routing): 4 requirements — ROUTE-01~04
- Phase 4 (Command Integration): 2 requirements — INFRA-04, STATE-03
- Phase 5 (State Integration): 2 requirements — STATE-01, STATE-02

---
*Requirements defined: 2026-02-08*
*Last updated: 2026-02-08 after roadmap phase mapping*
