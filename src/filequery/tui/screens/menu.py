from textual import on
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Static


class MenuModel(Screen):
    def compose(self):
        yield Vertical(
            Static("modal"),
            Button("close", id="close-btn")
        )

    @on(Button.Pressed, selector="#close-btn")
    def exit_modal(self, event):
        self.dismiss()
