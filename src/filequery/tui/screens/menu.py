import sys

from textual import on
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Rule, Static

from .menu_events import MenuEvent


class MenuModal(ModalScreen):
    BINDINGS = [
        Binding("up", "focus_previous"),
        Binding("down", "focus_next"),
    ]

    def compose(self):
        with Container():
            yield Vertical(
                Static("Menu", id="menu-title"),
                Rule(),
                Button("save SQL", id="save-sql-btn", classes="menu-btn"),
                Button("save query result", id="save-result-btn", classes="menu-btn"),
                Button("close menu", id="close-btn", classes="menu-btn"),
                Button("exit filequery", id="exit-btn", classes="menu-btn menu-exit-btn"),
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

    @on(Button.Pressed, selector="#exit-btn")
    def exit_modal(self, event):
        self.dismiss(MenuEvent.EXIT)
