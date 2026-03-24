import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.data.state import load_state, save_state


def test_load_state_default_when_no_file():
    with patch("src.data.state.STATE_PATH", Path("/tmp/nonexistent-csn-state.json")):
        state = load_state()
    assert state == {"group_mode": "project", "collapsed_groups": []}


def test_save_and_load_state():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        tmp_path = Path(f.name)

    with patch("src.data.state.STATE_PATH", tmp_path):
        save_state({"group_mode": "branch", "collapsed_groups": ["repo-a", "repo-b"]})
        state = load_state()

    assert state["group_mode"] == "branch"
    assert state["collapsed_groups"] == ["repo-a", "repo-b"]
    tmp_path.unlink(missing_ok=True)


def test_save_state_overwrites():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        tmp_path = Path(f.name)

    with patch("src.data.state.STATE_PATH", tmp_path):
        save_state({"group_mode": "project", "collapsed_groups": ["a"]})
        save_state({"group_mode": "branch", "collapsed_groups": []})
        state = load_state()

    assert state["group_mode"] == "branch"
    assert state["collapsed_groups"] == []
    tmp_path.unlink(missing_ok=True)
