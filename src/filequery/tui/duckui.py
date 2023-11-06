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

        # get the list of tables in the database to display them
        cur = self.conn.cursor()
        self.tables = "tables\n----------\n"
        cur.execute("show all tables")

        for rec in cur.fetchall():
            self.tables += rec[2]  # third column is table name
            self.tables += "\n"

        cur.close()

        super().__init__()

    def compose(self) -> ComposeResult:
        self.text_area = TextArea(language="sql", classes="box", theme="dracula")
        self.result_table = DataTable(classes="box")

        yield Horizontal(
            Vertical(
                # TODO make a custom class extending static, and make the content reactive
                Static(self.tables),
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
        cur = self.conn.cursor()

        for query in queries:
            if query.strip() != "":
                try:
                    cur.execute(query)
                    result = cur.fetchall()
                except:
                    # TODO display an error message on screen
                    pass

        try:
            col_names = [col[0] for col in cur.description]
            self.result_table.clear(columns=True)
            self.result_table.add_columns(*col_names)
            self.result_table.add_rows(result)
        except:
            # ignore errors for now
            pass
        finally:
            cur.close()


if __name__ == "__main__":
    app = DuckUI("hello")
    app.run()
