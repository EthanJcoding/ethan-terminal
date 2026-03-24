---
name: morning
description: 출근 후 아침 루틴 자동화. tmux pane으로 stg(SSH 터널)/dev 서버 띄우고, 오늘의 브리핑(어제 컨텍스트 + 스프린트 티켓 + PR + D-day)을 한 섹션으로 출력. 사용 시점 - "출근했어", "아침 루틴", "morning", "/morning" 등으로 요청할 때.
---

# Morning Routine

출근 후 한 번에 환경 셋업 + 아침 브리핑을 처리한다.

## 실행 흐름

```
Phase 1: 환경 셋업 (tmux) ─── 병렬
Phase 2: 오늘의 브리핑 (출력) ─── 순차 수집 후 한 번에 출력
```

---

## Phase 1: 환경 셋업

tmux pane을 분리하여 장기 프로세스를 띄운다. Claude Code 세션을 블로킹하지 않는다.

### Step 1: stg SSH 터널 띄우기

먼저 `stg` alias가 존재하는지 확인한다:

```bash
alias stg 2>/dev/null
```

**alias가 있는 경우:**
```bash
tmux split-window -v 'zsh -l -c stg; echo "stg 종료"; read'
```

**alias가 없는 경우:**
사용자에게 SSH 터널 명령어를 물어본다:
```
stg alias가 설정되어 있지 않습니다.
SSH 터널 명령어를 입력해주세요 (예: ssh -i ~/.ssh/id_ed25519 -N -L 23306:db-host:3306 user@bastion-ip):
```
입력받은 명령어로 tmux pane을 띄운다:
```bash
tmux split-window -v '{입력받은 명령어}; echo "stg 종료"; read'
```

터널 pane을 띄운 후 사용자에게 안내:
```
stg 터널 pane을 띄웠습니다. 비밀번호를 입력해주세요.
입력 완료되면 알려주세요.
```

**사용자 응답을 기다린다.** 자동으로 다음 단계로 넘어가지 않는다.

### Step 2: 포트 확인 후 dev 서버 띄우기

사용자가 비밀번호 입력 완료를 알리면, 포트를 확인하고 dev 서버를 띄운다.

```bash
# 터널 연결 확인
nc -z localhost 23306 && echo "터널 OK" || echo "터널 실패"

# dev 서버
tmux split-window -v 'cd ~/Documents/taling-core-api && git pull origin main && npm run dev; echo "dev 서버 종료"; read'
```

> `zsh -l -c stg`로 로그인 셸을 사용하여 ssh-agent가 연결된 환경에서 실행한다.
> stg 터널이 먼저 연결되어야 dev 서버가 DB에 접근할 수 있다.

셋업 완료 후 출력:
```
── 환경 ──
  stg 터널: tmux pane 1
  dev 서버: tmux pane 2 (git pull 완료)
```

---

## Phase 2: 오늘의 브리핑

아래 4가지 정보를 수집하여 **하나의 섹션**으로 출력한다.

### 2-1. 어제 컨텍스트

1. 어제 날짜의 daily note 읽기:
   ```
   ~/Documents/Obsidian Vault/notes/dailies/YYYY-MM-DD.md
   ```
2. "작업 내역" 섹션에서 핵심 내용 1-3줄 요약
3. taling-* 디렉토리에서 uncommitted changes가 있는 브랜치 찾기:
   ```bash
   for dir in ~/Documents/taling-*/; do
     cd "$dir" 2>/dev/null && \
     branch=$(git branch --show-current 2>/dev/null) && \
     status=$(git status --porcelain 2>/dev/null) && \
     [ -n "$status" ] && echo "$(basename $dir)/$branch: $(echo "$status" | wc -l | tr -d ' ') files"
   done
   ```

### 2-2. 스프린트 티켓

Atlassian MCP로 내 진행 중/할 일 티켓 조회:
- `searchJiraIssuesUsingJql` 사용
- JQL: `project = TONE AND assignee = currentUser() AND sprint in openSprints() AND status != Done ORDER BY status ASC`
- In Progress / To Do 만 표시 (Done 제외)

### 2-3. PR 알림

```bash
# 내 PR 상태
gh pr status

# 리뷰 요청받은 PR
gh pr list --search "review-requested:@me"
```

### 2-4. D-day

`~/.claude/special-days.json` 읽어서 가장 가까운 미래 D-day를 섹션 제목에 포함.

---

## 출력 형식

모든 정보를 수집한 후 아래 형식으로 **한 번에** 출력한다:

```
Good Morning, Eden!

── 환경 ──
  stg 터널: tmux pane 1
  dev 서버: tmux pane 2 (git pull 완료)

── 오늘의 브리핑 (D-{N} {라벨}) ──

  어제: {daily note 요약}
  → 이어서: {브랜치명} ({N} uncommitted files)

  티켓:
    {상태 이모지} {티켓번호} {제목} ({상태})
    ...

  PR:
    {PR 번호} {제목} — {상태}
    ...
```

상태 이모지: In Progress → `🔵`, To Do → `⚪`

D-day가 없으면 섹션 제목에서 D-day 부분 생략.
어제 daily note가 없으면 "어제 기록 없음" 표시.
uncommitted changes가 없으면 "이어서" 줄 생략.
PR이 없으면 PR 섹션 생략.
