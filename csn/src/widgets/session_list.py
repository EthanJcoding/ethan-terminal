from thefuzz import fuzz
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

from src.data.models import ProjectGroup, Session


class SessionTree(Tree):
    """프로젝트별 세션 트리 위젯."""

    def __init__(
        self,
        groups: list[ProjectGroup],
        group_mode: str = "project",
        collapsed_groups: set[str] | None = None,
        **kwargs,
    ):
        super().__init__("Sessions", **kwargs)
        self.groups = groups
        self.group_mode = group_mode  # "project" or "branch"
        self.collapsed_groups: set[str] = collapsed_groups or set()
        self.session_map: dict[str, Session] = {}

    def _format_label(self, session: Session) -> str:
        if not session.is_valid:
            marker = "✕"
        elif session.is_today:
            marker = "●"
        else:
            marker = "○"
        if self.group_mode == "branch":
            return f"{marker} {session.relative_time:>3}  {session.truncated_display()}"
        else:
            branch_tag = f"[{session.branch}] " if session.branch else ""
            display = session.truncated_display(18 if session.branch else 22)
            return f"{marker} {session.relative_time:>3} {branch_tag}{display}"

    def _build_tree(self, groups: list[ProjectGroup]) -> None:
        self.root.remove_children()
        self.session_map.clear()

        if self.group_mode == "branch":
            self._build_branch_tree(groups)
        else:
            self._build_project_tree(groups)

    def _build_project_tree(self, groups: list[ProjectGroup]) -> None:
        for group in groups:
            expand = group.name not in self.collapsed_groups
            branch = self.root.add(group.name, expand=expand)
            for session in group.sessions:
                label = self._format_label(session)
                node = branch.add_leaf(label)
                self.session_map[str(node.id)] = session

    def _build_branch_tree(self, groups: list[ProjectGroup]) -> None:
        for group in groups:
            expand_project = group.name not in self.collapsed_groups
            project_node = self.root.add(group.name, expand=expand_project)
            branch_groups = getattr(group, 'branch_groups', [])
            if branch_groups:
                for branch_name, sessions in branch_groups:
                    branch_label = f"  {branch_name}"
                    expand_branch = branch_label not in self.collapsed_groups
                    branch_node = project_node.add(branch_label, expand=expand_branch)
                    for session in sessions:
                        label = self._format_label(session)
                        node = branch_node.add_leaf(label)
                        self.session_map[str(node.id)] = session
            else:
                for session in group.sessions:
                    label = self._format_label(session)
                    node = project_node.add_leaf(label)
                    self.session_map[str(node.id)] = session

    def on_mount(self) -> None:
        self.root.expand()
        self._build_tree(self.groups)

    def filter_sessions(self, query: str) -> None:
        self.root.remove_children()
        self.session_map.clear()

        if not query:
            self._build_tree(self.groups)
            return

        q = query.lower()
        for group in self.groups:
            matching = [
                s for s in group.sessions
                if self._matches(q, s, group.name)
            ]
            if matching:
                branch = self.root.add(group.name, expand=True)
                for session in matching:
                    label = self._format_label(session)
                    node = branch.add_leaf(label)
                    self.session_map[str(node.id)] = session

    @staticmethod
    def _matches(query: str, session: Session, group_name: str) -> bool:
        """exact substring first, fuzzy fallback for short queries."""
        targets = [session.display.lower(), group_name.lower()]
        if session.branch:
            targets.append(session.branch.lower())

        for t in targets:
            if query in t:
                return True

        if len(query) <= 3:
            for t in targets:
                if fuzz.partial_ratio(query, t) > 70:
                    return True

        return False

    def get_selected_session(self, node: TreeNode) -> Session | None:
        return self.session_map.get(str(node.id))

    def get_cursor_session(self) -> Session | None:
        """현재 커서(하이라이트) 위치의 세션을 반환."""
        node = self.cursor_node
        if node is None:
            return None
        return self.session_map.get(str(node.id))

    def get_cursor_group_sessions(self) -> list[Session]:
        """현재 커서가 그룹 노드(프로젝트/브랜치)에 있으면 하위 세션 전체를 반환."""
        node = self.cursor_node
        if node is None:
            return []

        sessions = []
        self._collect_sessions(node, sessions)
        return sessions

    def _collect_sessions(self, node: TreeNode, sessions: list[Session]) -> None:
        """노드와 모든 자식에서 세션을 재귀적으로 수집."""
        session = self.session_map.get(str(node.id))
        if session:
            sessions.append(session)
        for child in node.children:
            self._collect_sessions(child, sessions)

    def get_collapsed_groups(self) -> list[str]:
        """현재 접힌(collapsed) 그룹 노드의 label 목록을 반환."""
        collapsed = []
        for top_node in self.root.children:
            if not top_node.is_expanded:
                collapsed.append(str(top_node.label))
            for child_node in top_node.children:
                if child_node.children and not child_node.is_expanded:
                    collapsed.append(str(child_node.label))
        return collapsed
