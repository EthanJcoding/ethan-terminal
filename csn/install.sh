#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CSN_TARGET="$HOME/Documents/claude-session-navigator"

echo "=== Claude Session Navigator 설치 ==="

# uv 설치
if ! command -v uv &>/dev/null; then
    echo "→ uv 설치 중..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # 현재 세션에서 uv 사용 가능하도록 PATH 갱신
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "→ uv 이미 설치됨"
fi

# CSN 프로젝트 배포
if [ -d "$CSN_TARGET" ]; then
    BACKUP_DIR="${CSN_TARGET}.bak.$(date +%Y-%m-%d)"
    echo "→ 기존 CSN 백업: $BACKUP_DIR"
    mv "$CSN_TARGET" "$BACKUP_DIR"
fi

echo "→ CSN 프로젝트 복사 중..."
mkdir -p "$CSN_TARGET"
cp -r "$SCRIPT_DIR"/src "$CSN_TARGET/"
cp -r "$SCRIPT_DIR"/scripts "$CSN_TARGET/"
cp -r "$SCRIPT_DIR"/tests "$CSN_TARGET/"
cp "$SCRIPT_DIR"/pyproject.toml "$CSN_TARGET/"
cp "$SCRIPT_DIR"/.python-version "$CSN_TARGET/"

# 의존성 설치
echo "→ Python 의존성 설치 중..."
cd "$CSN_TARGET" && uv sync

echo "→ CSN 설치 완료"
echo "  tmux 새 세션 시작 시 자동으로 sidebar가 열립니다."
