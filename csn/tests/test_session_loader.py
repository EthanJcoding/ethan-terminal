import json
import tempfile
from datetime import datetime
from pathlib import Path

from src.data.session_loader import load_sessions, group_by_project


def _write_history(entries: list[dict], path: Path):
    with open(path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def test_load_sessions_deduplicates_by_session_id():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        path = Path(f.name)

    now = int(datetime.now().timestamp() * 1000)
    _write_history([
        {"sessionId": "aaa", "display": "first", "timestamp": now - 5000, "project": "/a"},
        {"sessionId": "aaa", "display": "second", "timestamp": now, "project": "/a"},
    ], path)

    sessions = load_sessions(path)
    assert len(sessions) == 1
    assert sessions[0].display == "second"


def test_group_by_project():
    now = int(datetime.now().timestamp() * 1000)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        path = Path(f.name)

    _write_history([
        {"sessionId": "a", "display": "work1", "timestamp": now, "project": "/tmp/repo-a"},
        {"sessionId": "b", "display": "work2", "timestamp": now - 100000, "project": "/tmp/repo-b"},
        {"sessionId": "c", "display": "work3", "timestamp": now - 50000, "project": "/tmp/repo-a"},
    ], path)

    sessions = load_sessions(path)
    groups = group_by_project(sessions)

    assert groups[0].name == "repo-a"
    assert len(groups[0].sessions) == 2
    assert groups[1].name == "repo-b"


def test_project_name_home_directory():
    from src.data.models import Session
    home = str(Path.home())
    s = Session(session_id="x", display="test", timestamp=datetime.now(), project=home)
    assert s.project_name == "~"


def test_truncated_display():
    from src.data.models import Session
    s = Session(session_id="x", display="This is a very long session display text", timestamp=datetime.now(), project="/a")
    assert len(s.truncated_display(22)) <= 22
    assert s.truncated_display(22).endswith("…")
