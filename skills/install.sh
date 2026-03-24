#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_TARGET="$HOME/.claude/skills"

echo "=== Claude Code 스킬 설치 ==="

# morning 스킬 설치
MORNING_TARGET="$SKILLS_TARGET/morning"
mkdir -p "$MORNING_TARGET"
cp "$SCRIPT_DIR/morning/SKILL.md" "$MORNING_TARGET/SKILL.md"
echo "→ morning 스킬 설치 완료"

# SSH 터널 alias 설정
echo ""
echo "── SSH 터널 alias 설정 ──"
echo ""
echo "morning 스킬은 stg(staging DB 터널)를 사용합니다."
echo "alias를 설정하면 터미널에서 stg/pstg 명령으로 바로 터널을 열 수 있습니다."
echo ""
read -rp "stg/pstg alias를 .zshrc에 설정할까요? [y/N] " answer

if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo ""
    echo "SSH 터널 명령어를 입력해주세요."
    echo "예: ssh -i ~/.ssh/id_ed25519 -N -L 23306:db-host:3306 user@bastion-ip"
    echo ""

    read -rp "stg 명령어: " stg_cmd
    if [ -n "$stg_cmd" ]; then
        # 기존 stg alias가 있으면 교체, 없으면 추가
        if grep -q "^alias stg=" ~/.zshrc 2>/dev/null; then
            sed -i '' "s|^alias stg=.*|alias stg='$stg_cmd'|" ~/.zshrc
            echo "→ stg alias 업데이트 완료"
        else
            echo "" >> ~/.zshrc
            echo "# SSH tunnel (ethan-terminal)" >> ~/.zshrc
            echo "alias stg='$stg_cmd'" >> ~/.zshrc
            echo "→ stg alias 추가 완료"
        fi
    fi

    echo ""
    read -rp "pstg 명령어 (선택, Enter로 건너뛰기): " pstg_cmd
    if [ -n "$pstg_cmd" ]; then
        if grep -q "^alias pstg=" ~/.zshrc 2>/dev/null; then
            sed -i '' "s|^alias pstg=.*|alias pstg='$pstg_cmd'|" ~/.zshrc
            echo "→ pstg alias 업데이트 완료"
        else
            echo "alias pstg='$pstg_cmd'" >> ~/.zshrc
            echo "→ pstg alias 추가 완료"
        fi
    fi

    echo ""
    echo "→ .zshrc에 alias가 설정되었습니다."
    echo "  새 터미널을 열거나 source ~/.zshrc 를 실행해주세요."
else
    echo ""
    echo "→ alias 설정을 건너뜁니다."
    echo "  /morning 실행 시 SSH 명령어를 직접 물어봅니다."
fi
