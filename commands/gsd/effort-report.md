---
name: gsd:effort-report
description: 에이전트별 effort level 사용 현황과 권장 수준 대조 보고
argument-hint: "[phase number or 'all']"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

<objective>
프로젝트에서 사용된/사용될 에이전트들의 effort level 적합성을 분석.

현재 세션 effort level과 각 에이전트의 권장 effort를 대조하여
미스매치를 식별하고, 효율적인 effort 설정을 권장.
</objective>

<context>
대상: $ARGUMENTS (optional — 특정 페이즈 또는 'all', 기본값 'all')

참조 파일:
- 에이전트 권장 effort: agents/gsd-*.md 상단의 Recommended Effort Level
- 프로젝트 상태: .planning/STATE.md
- 페이즈 실행 기록: .planning/phases/*/SUMMARY.md
</context>

<process>

## 1. 현재 Effort Level 확인

```bash
echo $CLAUDE_CODE_EFFORT_LEVEL
```

미설정 시 기본값 'high'로 간주.

## 2. 에이전트별 권장 Effort 수집

에이전트 파일에서 Recommended Effort Level 추출:

```bash
grep -r "Recommended Effort" agents/gsd-*.md
```

권장 매핑 테이블 구성:
| Effort | 에이전트 |
|--------|----------|
| high | planner, plan-checker, debugger, research-synthesizer |
| medium | codebase-mapper, roadmapper, verifier, executor |
| low | project-researcher, phase-researcher, integration-checker |

## 3. 실행 기록 분석

$ARGUMENTS가 특정 페이즈인 경우 해당 페이즈만,
'all'이면 전체 페이즈의 SUMMARY.md에서 사용된 에이전트 추출.

```bash
grep -r "agent\|spawned\|Task(" .planning/phases/*/SUMMARY.md 2>/dev/null
```

## 4. 리포트 생성

현재 effort level과 각 에이전트 권장 effort를 대조:

### Effort 적합성 리포트

**현재 세션 effort:** {current_level}

| 에이전트 | 권장 | 현재 | 상태 |
|----------|------|------|------|
| gsd-planner | high | {current} | ✓ 적합 / ⚠ 과소 / △ 과다 |
| gsd-executor | medium | {current} | ... |
| ... | ... | ... | ... |

### 권장사항

- 과소 설정 에이전트가 있으면: "plan-checker는 high를 권장합니다.
  /model에서 effort를 높이거나 해당 작업 전에 조정하세요."
- 과다 설정이면: "phase-researcher는 low로 충분합니다.
  토큰 절약을 위해 effort를 낮추는 것을 고려하세요."

</process>

<success_criteria>
- [ ] 현재 effort level 확인
- [ ] 에이전트별 권장 effort 수집
- [ ] 적합성 대조 테이블 생성
- [ ] 미스매치 시 권장사항 제공
</success_criteria>
