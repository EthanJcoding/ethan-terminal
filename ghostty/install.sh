#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_SUFFIX=".bak.$(date +%Y-%m-%d)"

echo "=== Ghostty 설치 ==="

# Ghostty 설치
if ! command -v ghostty &>/dev/null && [ ! -d "/Applications/Ghostty.app" ]; then
    echo "→ Ghostty 설치 중..."
    brew install --cask ghostty
else
    echo "→ Ghostty 이미 설치됨"
fi

# 폰트 설치
brew tap homebrew/cask-fonts 2>/dev/null || true

if ! brew list --cask font-jetbrains-mono &>/dev/null; then
    echo "→ JetBrains Mono 폰트 설치 중..."
    brew install --cask font-jetbrains-mono
else
    echo "→ JetBrains Mono 이미 설치됨"
fi

if ! brew list --cask font-sarasa-gothic &>/dev/null; then
    echo "→ Sarasa Gothic 폰트 설치 중..."
    brew install --cask font-sarasa-gothic
else
    echo "→ Sarasa Gothic 이미 설치됨"
fi

# config 배포
CONFIG_DIR="$HOME/Library/Application Support/com.mitchellh.ghostty"
CONFIG_FILE="$CONFIG_DIR/config"

mkdir -p "$CONFIG_DIR"

if [ -f "$CONFIG_FILE" ]; then
    echo "→ 기존 config 백업: ${CONFIG_FILE}${BACKUP_SUFFIX}"
    cp "$CONFIG_FILE" "${CONFIG_FILE}${BACKUP_SUFFIX}"
fi

cp "$SCRIPT_DIR/config" "$CONFIG_FILE"
echo "→ Ghostty config 설치 완료"
