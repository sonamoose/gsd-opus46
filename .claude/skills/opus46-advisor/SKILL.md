---
name: opus46-advisor
description: 현재 작업 맥락에 맞는 Opus 4.6 기능을 추천. GSD 작업 중 어떤 Opus 4.6 기능을 활용할지 조언이 필요할 때 사용.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash
---

# Opus 4.6 Feature Advisor

현재 작업 맥락을 분석하여 적합한 Opus 4.6 기능을 추천합니다.

## 분석 절차

1. **현재 작업 맥락 파악**
   - .planning/STATE.md 읽기 (현재 단계)
   - .planning/ROADMAP.md 읽기 (전체 진행 상황)

2. **단계별 Opus 4.6 기능 매칭**

   | GSD 단계 | 추천 기능 | 이유 |
   |----------|-----------|------|
   | discuss-phase | Adaptive Thinking (high effort) | 깊은 분석과 질문 생성 필요 |
   | plan-phase | Adaptive Thinking (high effort) | 복잡한 계획 수립에 심층 사고 필요 |
   | execute-phase (병렬) | Agent Teams | wave 내 독립 플랜 병렬 실행 |
   | execute-phase (순차) | Sub-agents (Task) | 의존성 있는 작업은 순차 실행 |
   | verify-work | Adaptive Thinking (medium effort) | 검증은 중간 수준 사고로 충분 |
   | map-codebase | Agent Teams | 4개 focus area 병렬 분석 |
   | debug | Adaptive Thinking (high effort) | 원인 추적에 심층 사고 필요 |
   | 장시간 작업 후 | Compaction (/compact) | 컨텍스트 정리 |
   | 세션 시작 시 | SessionStart Hook | STATE.md + CODEMAP.md 자동 로딩 |

3. **상황별 추천 로직**

   현재 환경변수와 작업 맥락을 확인합니다:
   ```bash
   echo $CLAUDE_CODE_EFFORT_LEVEL
   echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
   ```

   | 상황 | 추천 기능 | 설정 방법 |
   |------|-----------|-----------|
   | 대규모 리팩토링 중 | **Agent Teams** (병렬 처리) | `export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
   | 컨텍스트가 길어짐 | **Compaction** (요약) | `/compact` 실행 또는 자동 compaction 대기 |
   | 반복적인 단순 작업 | **Effort Level Medium** (비용 절감) | `/model`에서 effort 슬라이더 조절 |
   | 복잡한 설계 단계 | **Plan Mode + High Effort** | Shift+Tab으로 Plan Mode 진입, effort high 설정 |

4. **현재 상태 기반 추천 출력**

   현재 단계가 {phase}이므로:
   - **추천 기능:** {feature}
   - **설정 방법:** {how-to}
   - **주의사항:** {caveat}

## 제약사항

- 읽기 전용 분석만 수행합니다.
- 추천은 .planning/ 상태 기반이며, 상태 파일이 없으면 일반 가이드를 제공합니다.
