# GSD-Opus46 설치 가이드

> Claude Code 전용. Opus 4.6 네이티브 기능(Agent Teams, Compaction, Adaptive Thinking)을 활용하는 GSD입니다.


## 요구 사항

- Claude Code (최신 버전)
- Node.js >= 16.7.0
- Python 3 (SessionStart 훅용)
- jq (settings.json 병합용, 선택)


## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/sonamoose/gsd-opus46.git
cd gsd-opus46
git checkout opus46-refactor
```

### 2. 기본 GSD 설치

```bash
node bin/install.js --claude --global
```

설치되는 항목:
- `~/.claude/commands/gsd/` — 슬래시 커맨드 (30개)
- `~/.claude/agents/` — 서브에이전트 (11개)
- `~/.claude/get-shit-done/` — 워크플로우, 레퍼런스, 템플릿
- `~/.claude/hooks/` — statusline, update-check (JS)
- `~/.claude/settings.json` — 훅 및 statusline 등록

### 3. Opus 4.6 확장 설치

`bin/install.js`는 Opus 4.6 추가분을 복사하지 않으므로 수동으로 설치합니다.

```bash
# Skills
mkdir -p ~/.claude/skills
cp -r .claude/skills/* ~/.claude/skills/

# SessionStart 훅 (Python)
cp .claude/hooks/gsd-context-loader.py ~/.claude/hooks/

# settings.json에 context-loader 훅 등록
if command -v jq &> /dev/null; then
  jq 'if (.hooks.SessionStart | map(select(.hooks[].command | contains("gsd-context-loader"))) | length) == 0
      then .hooks.SessionStart += [{"hooks":[{"type":"command","command":"python3 .claude/hooks/gsd-context-loader.py"}]}]
      else . end' ~/.claude/settings.json > /tmp/gsd-settings.tmp && mv /tmp/gsd-settings.tmp ~/.claude/settings.json
  echo "context-loader hook registered."
else
  echo "jq not found. Add manually to ~/.claude/settings.json:"
  echo '  {"hooks":[{"type":"command","command":"python3 .claude/hooks/gsd-context-loader.py"}]}'
fi
```

### 설치 확인

Claude Code를 실행하고 아래 항목을 확인합니다.

```
claude
```

**1) 슬래시 커맨드 확인:**

```
/gsd:help
```

GSD 커맨드 목록이 표시되면 기본 설치 완료.
Opus 4.6 전용 커맨드 3종이 포함되어야 합니다:
- `/gsd:team-review`
- `/gsd:effort-report`
- `/gsd:compact-state`

**2) SessionStart 훅 확인:**

새 세션 시작 시 아래 메시지가 출력되면 context-loader 동작 확인:

```
GSD Context Loaded.
```

(`.planning/STATE.md` 또는 `.planning/codebase/CODEMAP.md`가 있는 프로젝트에서 실행해야 내용이 로딩됩니다.)

**3) Skills 확인:**

Claude Code에서 아래를 입력합니다:

```
.planning/ 디렉토리의 프로젝트 진행 상황을 분석해줘
```

`gsd-analyzer` Skill이 자동으로 호출되면 정상입니다.


## 설치 구조

```
~/.claude/
├── commands/gsd/           ← 슬래시 커맨드 (원본 + Opus 4.6 3종)
├── agents/                 ← 서브에이전트 (11개)
├── get-shit-done/          ← 워크플로우, 레퍼런스, 템플릿
├── hooks/
│   ├── gsd-statusline.js       ← 상태바 (원본)
│   ├── gsd-check-update.js     ← 버전 확인 (원본)
│   └── gsd-context-loader.py   ← STATE.md + CODEMAP.md 자동 로딩 (Opus 4.6)
├── skills/
│   ├── gsd-analyzer/SKILL.md       ← 프로젝트 분석 (Opus 4.6)
│   └── opus46-advisor/SKILL.md     ← 기능 추천 (Opus 4.6)
└── settings.json
```


## 제거

```bash
# 기본 GSD 제거
npx get-shit-done-cc --claude --global --uninstall

# Opus 4.6 확장 수동 제거
rm ~/.claude/hooks/gsd-context-loader.py
rm -rf ~/.claude/skills/gsd-analyzer ~/.claude/skills/opus46-advisor
```

settings.json에서 `gsd-context-loader` 항목을 수동으로 제거합니다.
