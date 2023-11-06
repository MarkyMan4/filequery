from typing import Any, Coroutine

import duckdb
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Static, TextArea


class DuckUI(App):
    BINDINGS = [("f9", "execute_query", "Execute query")]
    CSS_PATH = "./styles/style.tcss"

    def __init__(self, conn: duckdb.DuckDBPyConnection = None):
        self.conn = conn

        if self.conn is None:
            self.conn = duckdb.connect(":memory:")

        self.cur = self.conn.cursor()
        super().__init__()

    def compose(self) -> ComposeResult:
        self.text_area = TextArea(language="sql", classes="box", theme="dracula")
        self.result_table = DataTable(classes="box")

        yield Horizontal(
            Vertical(
                Static("hello"),
                classes="browser-area",
            ),
            Vertical(
                self.text_area,
                self.result_table,
                classes="editor-area",
            ),
        )

        yield Footer()

    def action_execute_query(self):
        queries = self.text_area.text.split(";")
        result = None

        for query in queries:
            if query.strip() != "":
                self.cur.execute(query)
                result = self.cur.fetchall()

        try:
            col_names = [col[0] for col in self.cur.description]
            self.result_table.clear(columns=True)
            self.result_table.add_columns(*col_names)
            self.result_table.add_rows(result)
        except:
            # ignore errors for now
            pass


if __name__ == "__main__":
    app = DuckUI("hello")
    app.run()
