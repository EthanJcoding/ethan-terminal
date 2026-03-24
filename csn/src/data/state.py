import json
from pathlib import Path

STATE_PATH = Path.home() / ".claude" / "csn-state.json"


def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"group_mode": "project", "collapsed_groups": []}


def save_state(state: dict) -> None:
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, ensure_ascii=False)
