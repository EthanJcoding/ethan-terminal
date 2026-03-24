from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Session:
    session_id: str
    display: str
    timestamp: datetime
    project: str
    branch: str = ""
    is_valid: bool = True  # transcript file exists

    @property
    def project_name(self) -> str:
        parts = self.project.rstrip("/").split("/")
        name = parts[-1] if parts[-1] else "~"
        home = str(Path.home())
        if self.project.rstrip("/") == home:
            return "~"
        return name

    @property
    def relative_time(self) -> str:
        diff = datetime.now() - self.timestamp
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m"
        elif seconds < 86400:
            return f"{seconds // 3600}h"
        elif seconds < 604800:
            return f"{seconds // 86400}d"
        else:
            return f"{seconds // 604800}w"

    @property
    def is_today(self) -> bool:
        return self.timestamp.date() == datetime.now().date()

    def truncated_display(self, max_len: int = 22) -> str:
        text = self.display.split("\n")[0]
        if len(text) > max_len:
            return text[:max_len - 1] + "…"
        return text


@dataclass
class BranchGroup:
    branch: str  # e.g. "fix/TONE-1361", "TONE-1234", "main"
    sessions: list[Session]

    @property
    def latest_timestamp(self) -> datetime:
        return max(s.timestamp for s in self.sessions) if self.sessions else datetime.min


@dataclass
class ProjectGroup:
    name: str
    sessions: list[Session]
    branch_groups: list[tuple[str, list[Session]]] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.branch_groups is None:
            self.branch_groups = []

    @property
    def latest_timestamp(self) -> datetime:
        return max(s.timestamp for s in self.sessions) if self.sessions else datetime.min
