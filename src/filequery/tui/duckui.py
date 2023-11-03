from typing import Any, Coroutine

import duckdb

# from editor import SQLEditor
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Static, TextArea

ROWS = [
    ("lane", "swimmer", "country", "time"),
    (4, "Joseph Schooling", "Singapore", 50.39),
    (2, "Michael Phelps", "United States", 51.14),
    (5, "Chad le Clos", "South Africa", 51.14),
    (6, "László Cseh", "Hungary", 51.14),
    (3, "Li Zhuhao", "China", 51.26),
    (8, "Mehdy Metella", "France", 51.58),
    (7, "Tom Shields", "United States", 51.73),
    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
    (10, "Darren Burns", "Scotland", 51.84),
]


class DuckUI(App):
    BINDINGS = [("f9", "execute_query", "Execute query")]
    CSS_PATH = "./styles/style.tcss"

    def on_mount(self):
        self.conn = duckdb.connect(":memory:")
        self.cur = self.conn.cursor()

    def compose(self) -> ComposeResult:
        self.text_area = TextArea(language="sql", classes="box", theme="dracula")
        self.result_table = DataTable(classes="box")

        yield Horizontal(
            Vertical(
                Static("one"),
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
            self.result_table.clear()
            self.result_table.add_columns(*col_names)
            self.result_table.add_rows(result)
        except:
            pass
        # self.result_table.add_columns(*ROWS[0])
        # self.result_table.add_rows(ROWS[1:])
        # if result is not None:
        #     try:
        #         self.result_table.clear()
        #         # self.result_table.add_rows(result)
        #         self.table.add_columns(*ROWS[0])
        #         self.table.add_rows(ROWS[1:])
        #     except:
        #         # just skip this for now
        #         pass


if __name__ == "__main__":
    app = DuckUI()
    app.run()
