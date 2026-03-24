# ethan-terminal

Ghostty + tmux + Claude Session Navigator 터미널 세팅 패키지.

## Quick Setup

```bash
git clone https://github.com/EthanJcoding/ethan-terminal.git
cd ethan-terminal
./install.sh
```

이 한 줄로 아래 항목이 자동 설치됩니다:

- **Ghostty** — GPU 가속 터미널 (Catppuccin Mocha 테마, 한국어 렌더링 최적화)
- **tmux** — 터미널 멀티플렉서 (Catppuccin 상태바, TPM 플러그인)
- **Claude Session Navigator (CSN)** — Claude Code 세션 탐색 TUI (tmux sidebar 자동 실행)
- **폰트** — JetBrains Mono, Sarasa Gothic (한국어)
- **의존성** — Homebrew, uv, TPM 자동 설치

## 개별 설치

원하는 모듈만 설치할 수도 있습니다:

```bash
# Ghostty만
./ghostty/install.sh

# tmux만
./tmux/install.sh

# CSN만
./csn/install.sh
```

## 구성

### Ghostty (`ghostty/`)
- Catppuccin Mocha 테마
- JetBrains Mono + Sarasa Term K (한국어) 폰트
- `Cmd+S` 리더 키 바인딩

### tmux (`tmux/`)
- Prefix: `Ctrl+Space` (`Ctrl+B`도 유지)
- Vi 복사 모드 + pbcopy 연동
- Catppuccin 상태바: 세션 / 디렉토리 / Git 브랜치 / CPU / RAM / 배터리 / 시간
- `Option+hjkl` 패널 이동
- `Prefix+Tab` yazi 파일 탐색기
- 플러그인: catppuccin, cpu, battery, resurrect, continuum

### Claude Session Navigator (`csn/`)
- Claude Code 세션을 프로젝트/브랜치별로 탐색
- tmux 새 세션 시 자동 sidebar 실행 (50 columns)
- 키바인딩: `q` 종료 / `r` 새로고침 / `/` 검색 / `b` 브랜치 그룹 / `d` 숨기기

## 백업

설치 시 기존 설정 파일이 있으면 자동으로 `.bak.YYYY-MM-DD` 파일로 백업됩니다.
복원하려면:

```bash
# Ghostty
cp ~/Library/Application\ Support/com.mitchellh.ghostty/config.bak.2026-03-24 \
   ~/Library/Application\ Support/com.mitchellh.ghostty/config

# tmux
cp ~/.tmux.conf.bak.2026-03-24 ~/.tmux.conf
```

## Claude Code로 설치

팀원이 Claude Code에서 바로 설치할 수 있습니다:

```
https://github.com/EthanJcoding/ethan-terminal 레포를 클론해서 install.sh를 실행해줘
```
