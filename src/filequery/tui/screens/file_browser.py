from textual import on
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Rule, Static


class FileBrowser(ModalScreen):
    BINDINGS = [
        Binding("escape", "exit")
    ]

    def compose(self):
        with Container():
            yield Vertical(
                Static("Select file to load", id="menu-title"),
                Static("(esc to close this)", classes="centered"),
                Rule(),
                DirectoryTree("./"),
            )

    def action_exit(self):
        self.dismiss()

    @on(DirectoryTree.FileSelected)
    def handle_file_selected(self, event: DirectoryTree.FileSelected):
        self.dismiss(event.path)
