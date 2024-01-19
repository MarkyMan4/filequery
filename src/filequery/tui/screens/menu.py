from textual import on
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from .menu_events import MenuEvent


class MenuModal(ModalScreen):
    def compose(self):
        with Container():
            yield Vertical(
                Static("modal"),
                Button("save SQL", id="save-sql-btn"),
                Button("save query result", id="save-result-btn"),
                Button("close", id="close-btn"),
            )
    
    @on(Button.Pressed, selector="#save-sql-btn")
    def save_sql(self, event):
        self.dismiss(MenuEvent.SAVE_SQL)

    @on(Button.Pressed, selector="#save-result-btn")
    def save_result(self, event):
        self.dismiss(MenuEvent.SAVE_RESULT)

    @on(Button.Pressed, selector="#close-btn")
    def exit_modal(self, event):
        self.dismiss()
