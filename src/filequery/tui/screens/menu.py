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
                Button("load SQL", id="load-sql-btn", classes="menu-btn"),
                Button("save SQL", id="save-sql-btn", classes="menu-btn"),
                Button("save query result", id="save-result-btn", classes="menu-btn"),
                Button("close menu", id="close-btn", classes="menu-btn"),
                Button("exit filequery", id="exit-btn", classes="menu-btn menu-exit-btn"),
            )
    
    @on(Button.Pressed)
    def handle_button(self, event: Button.Pressed):
        if event.button.id == "load-sql-btn":
            self.dismiss(MenuEvent.LOAD_SQL)
        elif event.button.id == "save-sql-btn":
            self.dismiss(MenuEvent.SAVE_SQL)
        elif event.button.id == "save-result-btn":
            self.dismiss(MenuEvent.SAVE_RESULT)
        elif event.button.id == "close-btn":
            self.dismiss()
        elif event.button.id == "exit-btn":
            self.dismiss(MenuEvent.EXIT)
