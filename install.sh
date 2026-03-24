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
bash "$SCRIPT_DIR/skills/install.sh"

echo ""
echo "============================================"
echo "  설치 완료!"
echo "============================================"
echo ""
echo "다음 단계:"
echo "  1. Ghostty에서 Cmd+S → R 을 눌러 config를 reload 하세요"
echo "  2. 터미널에 tmux 를 입력하세요"
echo "  3. Session Navigator가 자동으로 sidebar에 표시됩니다"
echo ""
echo "기존 설정은 .bak.$(date +%Y-%m-%d) 파일로 백업되었습니다."
echo ""
echo "============================================"
echo "  tmux 기본 사용법"
echo "============================================"
echo ""
echo "Prefix 키: Ctrl+Space (또는 Ctrl+B)"
echo "모든 tmux 명령은 Prefix를 먼저 누른 뒤 키를 입력합니다."
echo ""
echo "  Prefix + c        새 윈도우"
echo "  Prefix + n / p    다음 / 이전 윈도우"
echo "  Prefix + |        세로 분할"
echo "  Prefix + -        가로 분할"
echo "  Prefix + x        현재 패널 닫기"
echo "  Prefix + Tab      yazi 파일 탐색기"
echo "  Option + h/j/k/l  패널 이동 (Prefix 없이)"
echo ""
echo "  Prefix + [        복사 모드 진입 (vi 키바인딩)"
echo "  q                 복사 모드 나가기"
echo ""
echo "  tmux detach       세션에서 빠져나오기 (Prefix + d)"
echo "  tmux attach       마지막 세션으로 다시 돌아가기"
