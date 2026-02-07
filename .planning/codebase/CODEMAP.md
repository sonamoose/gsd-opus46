# GSD CodeMap

> 초안: 핵심 구조·역할·의존관계 중심. 코드 변경 시 점진적 보강.
> 최종 갱신: 2026-02-07


## 1. Directory Structure Tree

```
refactored/
├── commands/gsd/           ← 슬래시 커맨드 (30개)
│   ├── new-project.md          사용자 진입점
│   ├── discuss-phase.md        메인 워크플로우
│   ├── plan-phase.md             ↓
│   ├── execute-phase.md          ↓
│   ├── verify-work.md            ↓
│   ├── team-review.md          Opus 4.6 신규
│   ├── effort-report.md          ↓
│   ├── compact-state.md          ↓
│   └── ...                     유틸리티 (progress, settings 등)
│
├── agents/                 ← 서브에이전트 정의 (11개)
│   ├── gsd-planner.md          핵심 판단 에이전트
│   ├── gsd-executor.md         코드 실행 에이전트
│   └── ...
│
├── get-shit-done/
│   ├── workflows/          ← 실행 로직 (12개)
│   │   ├── execute-phase.md    wave 분할·병렬 실행
│   │   ├── verify-work.md      UAT 수행
│   │   └── ...
│   ├── references/         ← 규칙·기준 문서 (9개)
│   │   ├── git-integration.md  커밋 규칙
│   │   ├── verification-patterns.md  검증 패턴
│   │   └── ...
│   └── templates/          ← .planning/ 문서 템플릿 (20+개)
│       ├── state.md            STATE.md 템플릿
│       ├── roadmap.md          ROADMAP.md 템플릿
│       ├── codebase/           코드베이스 분석 템플릿 (7개)
│       └── research-project/   리서치 템플릿 (5개)
│
├── .claude/                ← Claude Code 프로젝트 설정 (Opus 4.6 신규)
│   ├── settings.json           SessionStart 훅 등록
│   ├── hooks/
│   │   └── gsd-context-loader.py  STATE.md + CODEMAP.md 자동 로딩
│   └── skills/
│       ├── gsd-analyzer/SKILL.md      .planning/ 진행 상황 분석
│       └── opus46-advisor/SKILL.md    Opus 4.6 기능 추천
│
├── hooks/                  ← GSD 기본 Hooks (2개)
│   ├── gsd-statusline.js       상태바 표시
│   └── gsd-check-update.js     버전 확인
│
├── scripts/                ← 빌드 스크립트
│   └── build-hooks.js
├── bin/                    ← 설치
│   └── install.js
└── assets/                 ← 로고·이미지
```


## 2. Key Responsibilities

| 컴포넌트 | 역할 | 비고 |
|----------|------|------|
| **Commands** | 사용자 진입점. 인자 파싱 → 워크플로우 위임 또는 자체 오케스트레이션 | frontmatter로 allowed-tools 제한 |
| **Workflows** | 커맨드에서 위임받은 실행 로직. 에이전트 스폰 순서·조건 정의 | 커맨드와 1:1 또는 내부 전용 |
| **Agents** | Task()로 스폰되는 격리 작업자. 입력 → 출력 변환에 집중 | effort level별 권장 수준 보유 |
| **References** | 에이전트·워크플로우가 참조하는 규칙 문서 | git, 검증, TDD 등 |
| **Templates** | .planning/ 문서의 구조 정의 | 에이전트가 출력 시 참조 |
| **Skills** | Claude가 자동 또는 수동으로 호출하는 분석 도구 | allowed-tools로 권한 제한 |
| **Hooks** | 세션 이벤트에 자동 반응 | SessionStart, PreToolUse 등 |


## 3. Dependency Graph

```
[사용자] ──→ Commands ──→ Workflows ──→ Agents
                │              │            │
                │              │            ├─→ References (규칙 참조)
                │              │            └─→ Templates (출력 형식)
                │              │
                │              └─→ Agents (직접 스폰)
                │
                └─→ Agents (자체 오케스트레이션)
```

### 커맨드 → 워크플로우 → 에이전트 상세

```
new-project ──→ (자체) ──→ project-researcher ×4
                          → research-synthesizer
                          → roadmapper

discuss-phase ──→ discuss-phase.md ──→ (에이전트 없음)

plan-phase ──→ (자체) ──→ phase-researcher
                        → planner
                        → plan-checker (검증 루프)

execute-phase ──→ execute-phase.md ──→ executor ×N (wave 병렬)
                                    → verifier

verify-work ──→ verify-work.md ──→ planner (이슈 시)
                                 → plan-checker (이슈 시)

map-codebase ──→ map-codebase.md ──→ codebase-mapper ×4

debug ──→ (자체) ──→ debugger

audit-milestone ──→ (자체) ──→ integration-checker

quick ──→ (자체) ──→ planner → executor

team-review ──→ (Agent Teams) ──→ 리뷰어 ×3 (신규)
```

### 에이전트 → .planning/ 출력

```
project-researcher  → research/{STACK,FEATURES,ARCHITECTURE,PITFALLS}.md
research-synthesizer → research/SUMMARY.md
roadmapper          → ROADMAP.md, STATE.md
planner             → phases/XX/PLAN.md
executor            → phases/XX/SUMMARY.md, 코드, git commit
verifier            → phases/XX/VERIFICATION.md
codebase-mapper     → codebase/{stack,architecture,structure,...}.md
debugger            → debug/{slug}.md
integration-checker → MILESTONE-AUDIT.md
```


---

*CodeMap 초안: 2026-02-07*
*코드 변경 시 관련 섹션 갱신 필요*
