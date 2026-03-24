#!/bin/bash
# Claude Session Navigator — tmux sidebar launcher

CSN_DIR="$HOME/Documents/claude-session-navigator"

if [ -z "$TMUX" ]; then
    echo "Error: tmux 세션 안에서 실행해주세요."
    exit 1
fi

# 오른쪽에 50-column pane으로 분할하여 navigator 실행
tmux split-window -h -l 50 "cd $CSN_DIR && uv run python -m src.app"
