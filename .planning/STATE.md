# Project State

## Project Reference
See: .planning/PROJECT.md (updated 2026-02-08)
**Core value:** 코드 존재 여부에 따라 자동으로 최적의 워크플로우 제공
**Current focus:** Phase 1

## Current Status
**Milestone:** v1.0 — Brownfield Mode
**Phase:** 1 — Foundation (템플릿 + 에이전트 + 감지 로직)
**Status:** Not started

## Progress
| Phase | Name | Status | Plans | Progress |
|-------|------|--------|-------|----------|
| 1 | Foundation | ○ | 0/? | 0% |
| 2 | Analysis Pipeline | ○ | 0/? | 0% |
| 3 | Purpose Routing | ○ | 0/? | 0% |
| 4 | Command Integration | ○ | 0/? | 0% |
| 5 | State Integration + Polish | ○ | 0/? | 0% |

## Phase Details

### Phase 1: Foundation
**Requirements:** DETECT-01, DETECT-02, DETECT-03, DETECT-04, INFRA-01, INFRA-03
**Key artifacts:**
- `get-shit-done/templates/brownfield-summary.md` — 분석 요약 출력 템플릿
- `agents/gsd-brownfield-analyzer.md` — 코드베이스 분석 종합 에이전트
- Mode detection logic — 다중 시그널 감지 모듈

### Phase 2: Analysis Pipeline
**Requirements:** ANALYSIS-01, ANALYSIS-02, ANALYSIS-03, ANALYSIS-04, INFRA-02
**Key artifacts:**
- `get-shit-done/workflows/brownfield-flow.md` — 분석→결정→실행 파이프라인

### Phase 3: Purpose Routing
**Requirements:** ROUTE-01, ROUTE-02, ROUTE-03, ROUTE-04
**Key artifacts:**
- Purpose selection + purpose-aware questioning threads
- Problem-debug bridging + purpose-aware roadmap generation

### Phase 4: Command Integration
**Requirements:** INFRA-04, STATE-03
**Key artifacts:**
- `commands/gsd/new-project.md` — 브라운필드 분기 로직 통합

### Phase 5: State Integration + Polish
**Requirements:** STATE-01, STATE-02
**Key artifacts:**
- `get-shit-done/templates/project.md` — Codebase Mode 섹션 추가
- `get-shit-done/templates/state.md` — 브라운필드 컨텍스트 참조 추가

## Notes
- 빌드 순서는 ARCHITECTURE.md 연구의 의존성 그래프에 따름
- 각 Phase는 독립적으로 테스트 가능
- Phase 5+ (config, research, requirements, roadmap)는 그린필드/브라운필드 공유 경로

---
*State initialized: 2026-02-08*
*Last updated: 2026-02-08*
