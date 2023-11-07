import duckdb
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Markdown, Static, TextArea

from .help_content import help_md


class DuckUI(App):
    BINDINGS = [
        Binding(key="f2", action="toggle_help", description="help"),
        Binding(key="f9", action="execute_query", description="execute query"),
    ]
    CSS_PATH = "./styles/style.tcss"

    def __init__(self, conn: duckdb.DuckDBPyConnection = None):
        self.conn = conn

        if self.conn is None:
            self.conn = duckdb.connect(":memory:")

        # get the list of tables in the database to display them
        cur = self.conn.cursor()
        self.tables = ""
        cur.execute("show all tables")

        for rec in cur.fetchall():
            self.tables += rec[2]  # third column is table name
            self.tables += "\n"

        cur.close()

        super().__init__()

    def compose(self) -> ComposeResult:
        self.text_area = TextArea(language="sql", classes="editor-box", theme="monokai")
        self.text_area.focus(True)
        self.result_table = DataTable(classes="result-box")
        self.help_box = Markdown(help_md, classes="popup-box")

        yield Horizontal(
            Vertical(
                Static("tables", classes="title"),
                Static(self.tables),
                classes="browser-area",
            ),
            Vertical(
                self.text_area,
                self.result_table,
                classes="editor-area",
            ),
        )

        yield self.help_box

        yield Footer()

    def action_toggle_help(self):
        self.help_box.visible = not self.help_box.visible

    def action_execute_query(self):
        queries = self.text_area.text.split(";")
        result = None
        cur = self.conn.cursor()

        def display_error_in_table(error: Exception):
            self.result_table.clear(columns=True)
            self.result_table.add_column("error")
            self.result_table.add_row(error)

        for query in queries:
            if query.strip() != "":
                try:
                    cur.execute(query)
                    result = cur.fetchall()
                except Exception as e:
                    display_error_in_table(e)
                    cur.close()
                    return

        try:
            col_names = [col[0] for col in cur.description]
            self.result_table.clear(columns=True)
            self.result_table.add_columns(*col_names)
            self.result_table.add_rows(result)
        except Exception as e:
            display_error_in_table(e)
        finally:
            cur.close()
