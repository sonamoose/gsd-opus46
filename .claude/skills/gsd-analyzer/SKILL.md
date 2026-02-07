---
name: gsd-analyzer
description: .planning/ 디렉토리의 프로젝트 진행 상황을 분석하여 리포트 생성. 프로젝트 상태 확인, 페이즈 진행률, 미완료 항목 파악 시 사용.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
---

# GSD Project Analyzer

.planning/ 디렉토리를 분석하여 프로젝트 진행 상황 리포트를 생성합니다.

## 분석 절차

1. **프로젝트 기본 정보 확인**
   - .planning/PROJECT.md 읽기 (프로젝트명, 목표)
   - .planning/ROADMAP.md 읽기 (전체 페이즈 목록)
   - .planning/STATE.md 읽기 (현재 상태)
   - .planning/codebase/CODEMAP.md 읽기 (코드 구조)

2. **페이즈별 진행 상황 수집**
   - .planning/phases/*/PLAN.md 존재 여부 (계획 완료?)
   - .planning/phases/*/SUMMARY.md 존재 여부 (실행 완료?)
   - .planning/phases/*/VERIFICATION.md 존재 여부 (검증 완료?)
   - .planning/phases/*/UAT.md 존재 여부 (UAT 완료?)

3. **리포트 출력**

   ### GSD Project Analysis Report

   **Project:** {name}
   **Milestone:** {current}
   **Overall Progress:** {completed}/{total} phases

   | Phase | Plan | Execute | Verify | UAT |
   |-------|------|---------|--------|-----|
   | 01-name | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ |

   **Current Phase:** {phase} — {status}
   **Blockers:** {if any}
   **Next Action:** {recommendation}

   ### CodeMap Status
   - **CODEMAP.md:** 존재/미존재
   - **최종 갱신:** {date from file}
   - **포함 섹션:** Directory Structure / Key Responsibilities / Dependency Graph
   - **갱신 필요 여부:** {코드 변경 후 CODEMAP.md 미갱신 시 경고}

## 제약사항

- 읽기 전용 분석만 수행합니다. 파일을 수정하지 않습니다.
- .planning/ 디렉토리가 없으면 안내합니다.
