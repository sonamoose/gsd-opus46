---
name: gsd:compact-state
description: .planning/ 상태를 요약하고 STATE.md를 갱신하여 컴팩션 대비
argument-hint: "[focus: 'full' or 'current-phase']"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Write
---

<objective>
.planning/ 디렉토리의 상태 문서를 읽고 현재 프로젝트 상태를 압축 요약.
STATE.md를 최신 상태로 갱신하여, 컴팩션이나 세션 재개 시 핵심 정보가 유지되도록 보장.

사용 시점:
- 장시간 작업 후 컨텍스트 정리 전
- /compact 실행 전 상태 보존
- 세션 종료 전 진행 상태 기록
</objective>

<context>
범위: $ARGUMENTS (optional — 'full' 또는 'current-phase', 기본값 'full')

- full: PROJECT.md, ROADMAP.md, STATE.md, 전체 페이즈 요약
- current-phase: 현재 진행 중인 페이즈만 요약

읽기 대상:
- .planning/PROJECT.md
- .planning/ROADMAP.md
- .planning/STATE.md
- .planning/REQUIREMENTS.md
- .planning/phases/*/SUMMARY.md
- .planning/phases/*/PLAN.md (현재 페이즈만)
</context>

<process>

## 1. .planning/ 존재 확인

```bash
ls .planning/PROJECT.md .planning/STATE.md 2>/dev/null
```

없으면 에러: "GSD 프로젝트가 초기화되지 않았습니다. /gsd:new-project로 시작하세요."

## 2. 현재 상태 수집

핵심 파일 읽기:
```bash
cat .planning/PROJECT.md
cat .planning/ROADMAP.md
cat .planning/STATE.md
ls .planning/phases/*/SUMMARY.md 2>/dev/null
```

각 파일에서 추출할 정보:
- PROJECT.md: 프로젝트명, 핵심 목표
- ROADMAP.md: 전체 페이즈 목록, 현재 마일스톤
- STATE.md: 현재 페이즈, 완료/진행/대기 상태
- SUMMARY.md: 완료된 페이즈의 결과 요약

## 3. 미커밋 변경 확인

```bash
git status --short 2>/dev/null
git log --oneline -5 2>/dev/null
```

미커밋 변경이 있으면 경고에 포함.

## 4. STATE.md 갱신

수집한 정보를 기반으로 STATE.md를 최신 상태로 업데이트:

```markdown
## Current State (auto-updated by /gsd:compact-state)

**Project:** {project_name}
**Milestone:** {current_milestone}
**Phase:** {current_phase} — {phase_status}
**Last commit:** {last_commit_hash} {last_commit_message}
**Uncommitted changes:** {yes/no — file count}

### Phase Progress
| Phase | Status | Summary |
|-------|--------|---------|
| 01 | ✓ done | {one-line summary} |
| 02 | → active | {current task} |
| 03 | ○ pending | — |

### Decisions
{recent decisions from existing STATE.md}

### Blockers
{active blockers if any}
```

## 5. 요약 출력

갱신된 STATE.md의 핵심 내용을 화면에 출력.
사용자에게 안내: "STATE.md가 갱신되었습니다. /compact를 실행하면
이 상태가 컴팩션 후에도 CLAUDE.md와 함께 유지됩니다."

</process>

<success_criteria>
- [ ] .planning/ 파일 존재 확인
- [ ] 핵심 상태 정보 수집
- [ ] 미커밋 변경 확인
- [ ] STATE.md 최신 상태로 갱신
- [ ] 요약 출력 및 /compact 안내
</success_criteria>
