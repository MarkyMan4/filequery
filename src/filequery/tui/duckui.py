import re
from typing import Any, Coroutine, Tuple

import duckdb
from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Input, Markdown, Rule, Static, TextArea
from textual.widgets.text_area import Selection

from .help_content import help_md


class DuckUI(App):
    BINDINGS = [
        Binding(key="f2", action="toggle_help", description="help"),
        Binding(key="f9", action="execute_query", description="execute query"),
        Binding(key="ctrl+q", action="save_sql", description="save SQL"),
        Binding(key="ctrl+r", action="save_result", description="save result"),
        Binding(
            key="ctrl+p", action="close_all_popups", description="close all popups"
        ),
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
        self.text_area = TextArea(language="sql", classes="editor-box", theme="dracula")
        self.text_area.focus()
        self.result_table = DataTable(classes="result-box")
        self.result_table.zebra_stripes = True
        self.help_box = Markdown(help_md, classes="popup-box")
        self.save_sql_input = Input(
            placeholder="sql file name...",
            classes="file-name-input",
            id="sql-file-input",
        )
        self.save_result_input = Input(
            placeholder="result file name...",
            classes="file-name-input",
            id="result-file-input",
        )

        yield Horizontal(
            Vertical(
                Static("tables", classes="title"),
                Rule(),
                Static(
                    self.tables
                ),  # TODO make this a custom component with content being reactive
                classes="browser-area",
            ),
            Vertical(
                self.text_area,
                self.result_table,
                classes="editor-area",
            ),
        )

        yield self.help_box
        yield self.save_sql_input
        yield self.save_result_input

        yield Footer()

    @on(Input.Submitted, selector="#sql-file-input")
    def handle_sql_file_name_input(self):
        try:
            with open(self.save_sql_input.value, "w") as f:
                f.write(self.text_area.text)
        except:
            # ignore for now, find a way to display an error message
            pass

        # after submit, hide this dialog and refocus on text editor
        self.save_sql_input.display = False
        self.text_area.focus()

    @on(Input.Submitted, selector="#result-file-input")
    def handle_result_file_name_input(self):
        try:
            with open(self.save_result_input.value, "w") as f:
                cols = self.result_table.columns
                rows = self.result_table._data

                formatted_cols = [f'"{cols[col].label}"' for col in cols]
                f.write(",".join(formatted_cols))
                f.write("\n")

                for row in rows:
                    row_data = rows[row]
                    formatted_row = [f'"{row_data[col]}"' for col in row_data]
                    f.write(",".join(formatted_row))
                    f.write("\n")
        except:
            # ignore for now, find a way to display an error message
            pass

        # after submit, hide this dialog and refocus on text editor
        self.save_result_input.display = False
        self.text_area.focus()

    def action_close_all_popups(self):
        # close help and file name inputs and refocus on editor
        self.help_box.display = False
        self.save_sql_input.display = False
        self.save_result_input.display = False
        self.text_area.focus()

    def action_save_sql(self):
        self.save_sql_input.display = True
        self.save_sql_input.focus()

    def action_save_result(self):
        self.save_result_input.display = True
        self.save_result_input.focus()

    def action_toggle_help(self):
        self.help_box.display = not self.help_box.display

    def _display_error_in_table(self, error_msg: str):
        """
        Displays an error message in the result table

        :param error_msg: error message to display
        :type error: str
        """
        self.result_table.clear(columns=True)
        self.result_table.add_column("error")
        self.result_table.add_row(error_msg)

    def _find_query_at_cursor(
        self, cursor_x: int, cursor_y: int
    ) -> Tuple[str, Selection]:
        """
        Find the query at cursor_x, cursor_y

        :param cursor_x: line cursor is on
        :type cursor_x: int
        :param cursor_y: column cursor is on
        :type cursor_y: int
        :return: tuple with the query selection and the span of the query given as a Selection which
                 can be used to highlight the query
        :rtype: Tuple[str, Selection]
        """
        # remove comments
        text = re.sub("--.+", "", self.text_area.text)
        queries = text.split(";")

        # add character to the end of each query so that query is selected if cursor
        # is right before semicolon
        queries = [q + " " for q in queries]

        line = 0
        col = 0
        query_idx_to_run = -1
        found_query = False
        selection_start = (0, 0)
        selection_end = (0, 0)

        for i, query in enumerate(queries):
            selection_start = (line, col)

            # whether we've seen any characters in the current query besides newline and space
            found_non_empty_chars = False

            for c in query:
                if line == cursor_x and col == cursor_y:
                    query_idx_to_run = i
                    found_query = True

                if c == "\n":
                    col = 0
                    line += 1
                else:
                    col += 1
                    if c != " ":
                        found_non_empty_chars = True

                # if we've only seen newlines and whitespace, keep incrementing selection start
                # this way the highlighted portion actually starts at the code
                if (c == " " or c == "\n") and not found_non_empty_chars:
                    selection_start = (line, col)

            selection_end = (line, col)

            if found_query:
                break

        query = queries[query_idx_to_run] if query_idx_to_run != -1 else ""

        return query, Selection(selection_start, selection_end)

    def action_execute_query(self):
        """
        Executes the query at the cursor
        """
        cursor_x, cursor_y = self.text_area.cursor_location
        query, selection = self._find_query_at_cursor(cursor_x, cursor_y)

        if query.strip() == "":
            self._display_error_in_table("no query to run")
            return

        self.text_area.selection = selection

        result = None
        cur = self.conn.cursor()

        try:
            cur.execute(query)
            result = cur.fetchall()
        except Exception as e:
            self._display_error_in_table(str(e))
            cur.close()
            return

        try:
            col_names = [col[0] for col in cur.description]
            self.result_table.clear(columns=True)
            self.result_table.add_columns(*col_names)
            self.result_table.add_rows(result)
        except Exception as e:
            self._display_error_in_table(str(e))
        finally:
            cur.close()
