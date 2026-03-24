from textual.widgets import Input


class SearchBar(Input):
    DEFAULT_CSS = """
    SearchBar {
        dock: top;
        height: 3;
        display: none;
        border: solid green;
    }
    SearchBar.visible {
        display: block;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(placeholder="Search...", **kwargs)
