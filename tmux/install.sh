#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_SUFFIX=".bak.$(date +%Y-%m-%d)"

echo "=== tmux 설치 ==="

# tmux 설치
if ! command -v tmux &>/dev/null; then
    echo "→ tmux 설치 중..."
    brew install tmux
else
    echo "→ tmux 이미 설치됨"
fi

# .tmux.conf 배포
TMUX_CONF="$HOME/.tmux.conf"

if [ -f "$TMUX_CONF" ]; then
    echo "→ 기존 .tmux.conf 백업: ${TMUX_CONF}${BACKUP_SUFFIX}"
    cp "$TMUX_CONF" "${TMUX_CONF}${BACKUP_SUFFIX}"
fi

cp "$SCRIPT_DIR/.tmux.conf" "$TMUX_CONF"
echo "→ .tmux.conf 설치 완료"

# TPM (Tmux Plugin Manager) 설치
TPM_DIR="$HOME/.tmux/plugins/tpm"
if [ ! -d "$TPM_DIR" ]; then
    echo "→ TPM 설치 중..."
    git clone https://github.com/tmux-plugins/tpm "$TPM_DIR"
else
    echo "→ TPM 이미 설치됨"
fi

# 플러그인 자동 설치
echo "→ tmux 플러그인 설치 중..."
"$TPM_DIR/bin/install_plugins" || echo "  (tmux 서버가 없으면 플러그인은 첫 실행 시 자동 설치됩니다)"

echo "→ tmux 설치 완료"
