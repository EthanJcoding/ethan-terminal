import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

from .models import Session, ProjectGroup

HISTORY_PATH = Path.home() / ".claude" / "history.jsonl"
HIDDEN_PATH = Path.home() / ".claude" / "csn-hidden.json"


def get_valid_session_ids() -> set[str]:
    """~/.claude/projects/ 아래 존재하는 세션 transcript 파일의 ID를 수집."""
    projects_dir = Path.home() / ".claude" / "projects"
    valid_ids = set()
    if projects_dir.exists():
        for jsonl_file in projects_dir.rglob("*.jsonl"):
            valid_ids.add(jsonl_file.stem)
    return valid_ids


def load_hidden_ids() -> set[str]:
    if HIDDEN_PATH.exists():
        with open(HIDDEN_PATH) as f:
            return set(json.load(f))
    return set()


def save_hidden_id(session_id: str) -> None:
    hidden = load_hidden_ids()
    hidden.add(session_id)
    with open(HIDDEN_PATH, "w") as f:
        json.dump(sorted(hidden), f)


def extract_branch(display: str, project_path: str) -> str:
    """세션 메시지에서 브랜치/티켓 정보 추출. 못 찾으면 빈 문자열."""
    # 1. 브랜치명 패턴 (feat/TONE-1234, fix/TONE-5678 등)
    branch_match = re.search(r'(feat|fix|chore|refactor|style|docs)/TONE-\d+', display)
    if branch_match:
        return branch_match.group(0)

    # 2. 티켓번호 패턴 (TONE-1234)
    ticket_match = re.search(r'TONE-\d+', display)
    if ticket_match:
        return ticket_match.group(0)

    return ""


# Branch cache to avoid repeated git calls
_branch_cache: dict[str, str] = {}


def get_current_branch(project_path: str) -> str:
    """프로젝트 경로의 현재 git branch를 캐시하여 반환."""
    if project_path in _branch_cache:
        return _branch_cache[project_path]
    try:
        result = subprocess.run(
            ["git", "-C", project_path, "branch", "--show-current"],
            capture_output=True, text=True, timeout=2,
        )
        branch = result.stdout.strip() if result.returncode == 0 else ""
        _branch_cache[project_path] = branch
        return branch
    except (FileNotFoundError, subprocess.TimeoutExpired):
        _branch_cache[project_path] = ""
        return ""


def load_sessions(path: Path = HISTORY_PATH) -> list[Session]:
    sessions_map: dict[str, Session] = {}
    # Collect all displays per session for branch extraction
    session_displays: dict[str, list[str]] = {}

    hidden_ids = load_hidden_ids()
    valid_ids = get_valid_session_ids()

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            session_id = data.get("sessionId", "")
            if not session_id:
                continue

            # Filter out hidden sessions
            if session_id in hidden_ids:
                continue

            display = data.get("display", "")
            project = data.get("project", "")

            if session_id not in session_displays:
                session_displays[session_id] = []
            session_displays[session_id].append(display)

            sessions_map[session_id] = Session(
                session_id=session_id,
                display=display,
                timestamp=datetime.fromtimestamp(data["timestamp"] / 1000),
                project=project,
                is_valid=session_id in valid_ids,
            )

    # Extract branch from all messages in session (check all messages, not just last)
    for session_id, session in sessions_map.items():
        displays = session_displays.get(session_id, [])
        branch = ""
        for d in displays:
            branch = extract_branch(d, session.project)
            if branch:
                break
        session.branch = branch

    return sorted(sessions_map.values(), key=lambda s: s.timestamp, reverse=True)


def group_by_project(sessions: list[Session]) -> list[ProjectGroup]:
    groups: dict[str, list[Session]] = {}
    for session in sessions:
        name = session.project_name
        if name not in groups:
            groups[name] = []
        groups[name].append(session)

    project_groups = [
        ProjectGroup(name=name, sessions=sessions)
        for name, sessions in groups.items()
    ]

    return sorted(project_groups, key=lambda g: g.latest_timestamp, reverse=True)


def group_by_branch(sessions: list[Session]) -> list[ProjectGroup]:
    """프로젝트 > 브랜치 순으로 중첩 그룹핑."""
    # First group by project
    project_map: dict[str, list[Session]] = {}
    for session in sessions:
        name = session.project_name
        if name not in project_map:
            project_map[name] = []
        project_map[name].append(session)

    project_groups = []
    for name, proj_sessions in project_map.items():
        # Within each project, group by branch
        branch_map: dict[str, list[Session]] = {}
        for s in proj_sessions:
            b = s.branch or "(no branch)"
            if b not in branch_map:
                branch_map[b] = []
            branch_map[b].append(s)

        # Sort branches by latest timestamp, (no branch) always last
        sorted_branches = sorted(
            branch_map.items(),
            key=lambda x: (x[0] == "(no branch)", -max(s.timestamp for s in x[1]).timestamp()),
        )

        pg = ProjectGroup(name=name, sessions=proj_sessions)
        pg.branch_groups = sorted_branches
        project_groups.append(pg)

    return sorted(project_groups, key=lambda g: g.latest_timestamp, reverse=True)
