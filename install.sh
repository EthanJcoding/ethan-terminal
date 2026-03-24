#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================"
echo "  ethan-terminal 설치"
echo "============================================"
echo ""

# Homebrew 확인
if ! command -v brew &>/dev/null; then
    echo "⚠️  Homebrew가 설치되어 있지 않습니다."
    echo "   Ghostty, tmux, 폰트 설치에 Homebrew가 필요합니다."
    echo ""
    read -rp "Homebrew를 설치할까요? [y/N] " answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo "→ Homebrew 설치 중..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo "→ Homebrew 설치를 건너뜁니다. Ghostty/tmux/폰트는 수동으로 설치해주세요."
        echo "  CSN만 설치합니다."
        echo ""
        bash "$SCRIPT_DIR/csn/install.sh"
        echo ""
        echo "설치 완료 (CSN만)"
        exit 0
    fi
else
    echo "→ Homebrew 이미 설치됨"
fi

echo ""

# 각 모듈 설치
bash "$SCRIPT_DIR/ghostty/install.sh"
echo ""
bash "$SCRIPT_DIR/tmux/install.sh"
echo ""
bash "$SCRIPT_DIR/csn/install.sh"

echo ""
echo "============================================"
echo "  설치 완료!"
echo "============================================"
echo ""
echo "다음 단계:"
echo "  1. Ghostty를 실행하세요"
echo "  2. tmux를 시작하세요: tmux new -s main"
echo "  3. Session Navigator가 자동으로 sidebar에 표시됩니다"
echo ""
echo "기존 설정은 .bak.$(date +%Y-%m-%d) 파일로 백업되었습니다."
