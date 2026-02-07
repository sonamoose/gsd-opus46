---
name: gsd:team-review
description: Agent Teams를 활용한 병렬 코드 리뷰 (보안/성능/가독성)
argument-hint: "<path to review>"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Task
---

<objective>
Agent Teams로 3명의 리뷰어를 스폰하여 코드를 병렬 리뷰.

리뷰어 구성:
1. 보안 리뷰어 — OWASP Top 10, 인젝션, 인증/인가 취약점
2. 성능 리뷰어 — N+1 쿼리, 메모리 누수, 불필요한 연산
3. 가독성 리뷰어 — 네이밍, 구조, 복잡도, 프로젝트 컨벤션

각 리뷰어가 독립적으로 분석 후 결과를 공유 태스크 리스트에 기록.
리드가 결과를 종합하여 우선순위별 리뷰 리포트 생성.
</objective>

<context>
리뷰 대상: $ARGUMENTS (required — 파일 경로 또는 디렉토리)

예시:
  /gsd:team-review src/auth/
  /gsd:team-review src/api/routes.ts
</context>

<process>

## 1. 인자 검증

$ARGUMENTS가 없으면 에러:
"리뷰 대상 경로를 지정해주세요. 예: /gsd:team-review src/auth/"

경로 존재 여부 확인:
```bash
ls $ARGUMENTS 2>/dev/null
```

## 2. 리뷰 대상 파일 수집

```bash
# 디렉토리면 하위 파일 목록, 파일이면 단일 파일
find $ARGUMENTS -type f -name "*.ts" -o -name "*.js" -o -name "*.py" \
  -o -name "*.go" -o -name "*.rs" 2>/dev/null | head -50
```

파일이 50개 초과 시 사용자에게 범위 축소 요청.

## 3. Agent Teams 리뷰어 스폰

3개 태스크를 공유 태스크 리스트에 등록하고 팀원 3명을 스폰:

**태스크 1: 보안 리뷰**
- OWASP Top 10 취약점 점검
- 인젝션 (SQL, XSS, Command), 인증/인가, 시크릿 노출
- 심각도: critical / high / medium / low

**태스크 2: 성능 리뷰**
- N+1 쿼리, 불필요한 루프, 메모리 누수 패턴
- 비동기 처리, 캐싱 기회, 알고리즘 복잡도
- 영향도: high / medium / low

**태스크 3: 가독성 리뷰**
- 네이밍 일관성, 함수 크기, 복잡도 (인지 복잡도)
- 프로젝트 컨벤션 준수, 중복 코드
- 개선도: high / medium / low

## 4. 결과 종합

팀원 완료 후 결과를 수집하여 우선순위별 정리:

1. Critical/High 이슈 (즉시 수정 필요)
2. Medium 이슈 (권장 수정)
3. Low 이슈 (참고)

각 이슈에 파일:라인, 설명, 제안 포함.

</process>

<success_criteria>
- [ ] 리뷰 대상 경로 검증 완료
- [ ] 3명의 리뷰어 스폰 완료
- [ ] 보안/성능/가독성 각 영역 리뷰 완료
- [ ] 우선순위별 종합 리포트 제공
</success_criteria>
