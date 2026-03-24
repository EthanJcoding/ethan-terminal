import subprocess

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Tree

from src.data.session_loader import load_sessions, group_by_project, group_by_branch, save_hidden_id
from src.data.state import load_state, save_state
from src.widgets.search_bar import SearchBar
from src.widgets.session_list import SessionTree


class SessionNavigator(App):
    CSS = """
    SessionTree {
        width: 100%;
        height: 1fr;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("/", "search", "Search"),
        ("b", "toggle_group", "Branch"),
        ("d", "hide_session", "Hide"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        state = load_state()
        self.group_mode = state.get("group_mode", "project")
        self.collapsed_groups: set[str] = set(state.get("collapsed_groups", []))

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield SearchBar(id="search-bar")
        sessions = load_sessions()
        groups = group_by_project(sessions)
        yield SessionTree(
            groups,
            group_mode=self.group_mode,
            collapsed_groups=self.collapsed_groups,
            id="session-tree",
        )
        yield Footer()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        tree = self.query_one(SessionTree)
        session = tree.get_selected_session(event.node)
        if session:
            if not session.is_valid:
                self.notify("세션이 만료되었습니다", severity="warning")
                return
            self.resume_session(session)

    def resume_session(self, session: "Session") -> None:
        """새 tmux window에서 세션의 project 경로로 이동 후 claude --resume 실행."""
        window_name = session.project_name
        if session.branch:
            window_name = f"{window_name}:{session.branch}"
        try:
            subprocess.run(
                ["tmux", "new-window", "-n", window_name, "-c", session.project,
                 f"claude --dangerously-skip-permissions --teammate-mode tmux --resume {session.session_id}; exec $SHELL"],
                capture_output=True, text=True,
            )
        except FileNotFoundError:
            self.notify("tmux not found", severity="error")

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        self._save_current_state()

    def on_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        self._save_current_state()

    def _save_current_state(self) -> None:
        tree = self.query_one(SessionTree)
        collapsed = tree.get_collapsed_groups()
        self.collapsed_groups = set(collapsed)
        save_state({
            "group_mode": self.group_mode,
            "collapsed_groups": collapsed,
        })

    def action_search(self) -> None:
        search_bar = self.query_one(SearchBar)
        if search_bar.has_class("visible"):
            search_bar.remove_class("visible")
            search_bar.value = ""
            tree = self.query_one(SessionTree)
            tree.filter_sessions("")
        else:
            search_bar.add_class("visible")
            search_bar.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-bar":
            tree = self.query_one(SessionTree)
            tree.filter_sessions(event.value)

    def on_key(self, event) -> None:
        if event.key == "escape":
            search_bar = self.query_one(SearchBar)
            if search_bar.has_class("visible"):
                search_bar.remove_class("visible")
                search_bar.value = ""
                tree = self.query_one(SessionTree)
                tree.filter_sessions("")
                event.prevent_default()

    def action_hide_session(self) -> None:
        tree = self.query_one(SessionTree)
        session = tree.get_cursor_session()
        if session:
            save_hidden_id(session.session_id)
            self._rebuild_tree()
            self.notify("세션을 숨겼습니다", timeout=2)
            return
        group_sessions = tree.get_cursor_group_sessions()
        if group_sessions:
            for s in group_sessions:
                save_hidden_id(s.session_id)
            self._rebuild_tree()
            self.notify(f"{len(group_sessions)}개 세션을 숨겼습니다", timeout=2)

    def action_toggle_group(self) -> None:
        self.group_mode = "branch" if self.group_mode == "project" else "project"
        self.collapsed_groups = set()
        self._rebuild_tree()
        self._save_current_state()
        mode_label = "Branch" if self.group_mode == "branch" else "Project"
        self.notify(f"Group: {mode_label}", timeout=2)

    def action_refresh(self) -> None:
        self._rebuild_tree()

    def _rebuild_tree(self) -> None:
        try:
            sessions = load_sessions()
            if self.group_mode == "branch":
                groups = group_by_branch(sessions)
            else:
                groups = group_by_project(sessions)

            tree = self.query_one(SessionTree)
            tree.groups = groups
            tree.group_mode = self.group_mode
            tree.collapsed_groups = self.collapsed_groups
            tree.root.remove_children()
            tree.session_map.clear()
            tree._build_tree(groups)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")


def main():
    app = SessionNavigator()
    app.run()


if __name__ == "__main__":
    main()
