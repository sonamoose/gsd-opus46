# GSD-Opus46 모드 분기 개선

## What This Is

GSD-Opus46의 `/gsd:new-project` 커맨드가 기존 코드베이스(브라운필드)와 신규 프로젝트(그린필드)를 자동 감지하고, 각각 최적화된 워크플로우로 분기하는 시스템. 기존 코드가 있으면 5-signal 감지 → 4방면 분석 → 목적별 라우팅(Fix/Improve/Refactor) → 맞춤 로드맵 생성. 신규면 설계 중심 질문 → 연구 → 요구사항 → 로드맵 파이프라인.

## Core Value

코드 존재 여부에 따라 자동으로 최적의 워크플로우를 제공하여, 기존 코드의 통찰력을 유지하면서 작업하거나 신규 프로젝트를 꼼꼼하게 설계할 수 있게 한다.

## Requirements

### Validated

- ✓ 신규 프로젝트 모드 — 설계 중심 질문→연구→요구사항→로드맵 파이프라인 (existing)
- ✓ 브라운필드 감지 — 코드 파일/패키지 매니저 존재 여부 확인 (existing)
- ✓ 코드베이스 매핑 — /gsd:map-codebase로 구조 분석 (existing)
- ✓ 커맨드 체계 — 30개 슬래시 커맨드, 11개 에이전트, 워크플로우 구조 (existing)
- ✓ 연구 에이전트 — 4개 병렬 researcher 스폰 (existing)
- ✓ 자동 모드 감지 — 5-signal 복합 판단으로 greenfield/scaffolded/brownfield 자동 분류 — v1.0
- ✓ 기존 코드베이스 4방면 자동 분석 — 구조/아키텍처, 기술 스택, 문제점/기술부채, 테스트 상태 — v1.0
- ✓ 분석 결과 요약 대시보드 — 10줄 이내 health/dimension/concerns 인라인 제시 — v1.0
- ✓ 수정/개선/리팩토링 목적 확인 — 분석 기반 목적 추천 + 사용자 선택 — v1.0
- ✓ 목적별 맞춤 질문 흐름 — diagnostic partner 패턴으로 분석→행동 연결 — v1.0
- ✓ 목적별 워크플로우 분기 — severity/dependency/impact-effort 순 로드맵 자동 생성 — v1.0
- ✓ 기존 코드 통찰력 유지 — PROJECT.md/STATE.md Codebase Context로 planner/executor에 전파 — v1.0
- ✓ 문제점-디버그 브릿징 — CONCERNS.md 발견사항을 gsd-debugger 호환 형식으로 자동 프리필 — v1.0
- ✓ 그린필드 무변경 보장 — 기존 동작 회귀 없음 (MODE 기반 guard 시스템) — v1.0

### Active

(None — next milestone requirements to be defined via `/gsd:new-milestone`)

### Out of Scope

- 별도 커맨드 분리 — /gsd:new-project 하나에서 내부 분기로 처리
- 실시간 코드 모니터링 — 세션 중 코드 변경 자동 감지는 범위 밖
- 기존 에이전트 구조 변경 — 현재 에이전트 체계는 유지하고 새 에이전트/워크플로우만 추가
- ESLint/SonarQube 통합 — AI 에이전트가 직접 분석
- CVE 취약점 스캐닝 — 전문 보안 도구 영역
- 코드 품질 점수 (A-F) — 카테고리별 심각도 사용

## Context

- GSD-Opus46은 Claude Code 위에서 동작하는 프로젝트 관리 프레임워크
- v1.0 shipped: `/gsd:new-project`이 자동으로 brownfield/greenfield를 감지하고 최적 흐름으로 분기
- 커맨드(commands/) → 워크플로우(workflows/) → 에이전트(agents/) 3계층 아키텍처
- `.planning/` 디렉토리에 모든 프로젝트 상태가 저장됨
- v2 후보: 증분 분석(before/after 비교), 프레임워크별 맞춤 탐색

## Constraints

- **아키텍처**: commands → workflows → agents 3계층 구조를 따라야 함
- **진입점**: /gsd:new-project 하나의 커맨드에서 분기 — 별도 커맨드 추가 안 함
- **호환성**: 기존 신규 프로젝트 모드의 동작을 깨뜨리지 않아야 함
- **출력 형식**: GSD UI 브랜드 패턴(배너, 체크포인트, 상태 심볼) 준수

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| /gsd:new-project 내부 분기 | 사용자가 모드를 선택할 필요 없이 자동 감지로 최적 흐름 제공 | ✓ Good |
| 코드 존재 여부로 자동 감지 | 가장 직관적이고 정확한 판단 기준 | ✓ Good |
| 4방면 자동 분석 (구조, 스택, 문제점, 테스트) | 코드베이스의 전체 맥락을 빠짐없이 파악 | ✓ Good |
| 분석 후 수정/개선 선택 | 사용자 목적에 따라 이후 워크플로우가 달라져야 함 | ✓ Good |
| Severity criteria use observable conditions | Ensures any Claude instance classifies consistently | ✓ Good |
| Scope filtering at extraction time | Maintains agent's single-pass synthesis approach | ✓ Good |
| Diagnostic partner philosophy | Analysis provides observed state; questioning navigates to action | ✓ Good |
| Purpose routing defaults to true | Primary caller always wants full pipeline | ✓ Good |
| Debug bridging uses existing gsd-debugger format | Reuse > reinvent; immediate compatibility | ✓ Good |

---
*Last updated: 2026-02-08 after v1.0 milestone*
