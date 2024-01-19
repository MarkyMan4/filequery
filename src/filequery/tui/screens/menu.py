from textual import on
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class MenuModal(ModalScreen):
    def compose(self):
        with Container():
            yield Vertical(
                Static("modal"),
                Button("close", id="close-btn")
            )

    @on(Button.Pressed, selector="#close-btn")
    def exit_modal(self, event):
        self.dismiss()
