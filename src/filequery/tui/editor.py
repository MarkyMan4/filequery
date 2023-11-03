from typing import Any, Coroutine

from textual import events
from textual.widgets import TextArea


class SQLEditor(TextArea):
    BINDINGS = [("f5", "execute_query", "Execute the query")]

    def _on_key(self, event: events.Key):
        event.
        if event.key == "c":
            self.clear()
