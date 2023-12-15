import re
from collections import defaultdict
from typing import List, Tuple

import duckdb
from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (DataTable, Footer, Input, Markdown, Rule, Static,
                             Tab, Tabs, TextArea)
from textual.widgets.text_area import Selection

from .help_content import help_md
from .widgets.reactive_list import ReactiveList


class DuckUI(App):
    BINDINGS = [
        Binding(key="f2", action="toggle_help", description="help"),
        Binding(key="f9", action="execute_query", description="execute query"),
        Binding(key="ctrl+q", action="save_sql", description="save SQL"),
        Binding(key="ctrl+r", action="save_result", description="save result"),
        Binding(key="ctrl+p", action="close_dialog", description="close dialog"),
        Binding(key="ctrl+n", action="new_tab", description="new tab"),
        Binding(key="ctrl+t", action="close_tab", description="close tab"),
    ]
    CSS_PATH = "./styles/style.tcss"

    def __init__(self, conn: duckdb.DuckDBPyConnection = None):
        self.conn = conn

        if self.conn is None:
            self.conn = duckdb.connect(":memory:")

        # get the list of tables in the database to display them
        cur = self.conn.cursor()
        self.tables = []
        cur.execute("show all tables")

        for rec in cur.fetchall():
            self.tables.append(rec[2])  # third column is table name
            self.tables += "\n"

        cur.close()

        # mapping from tab ID to editor content, tab IDs are "tab-1", "tab-2" and so on
        self.tab_content = defaultdict(str)

        super().__init__()

    def _get_table_list(self) -> List[str]:
        """
        get the list of tables in the database

        :return: list of tables currently in the database
        :rtype: List[str]
        """
        cur = self.conn.cursor()
        tables = []
        cur.execute("show all tables")

        for rec in cur.fetchall():
            tables.append(rec[2])  # third column is table name

        cur.close()

        return tables

    def compose(self) -> ComposeResult:
        self.table_list = ReactiveList()
        self.table_list.items = self._get_table_list()

        self.text_area = TextArea(
            language="sql", classes="editor-box", theme="dracula", id="editor"
        )
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

        self.tabs = Tabs(Tab("tab 1"))

        yield Horizontal(
            Vertical(
                Static("tables", classes="title"),
                Rule(),
                self.table_list,
                classes="browser-area",
            ),
            Vertical(
                self.tabs,
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

    @on(TextArea.Changed, selector="#editor")
    def handle_editor_content_changed(self):
        cur_tab = self.tabs.active_tab.id
        self.tab_content[cur_tab] = self.text_area.text

    @on(Tabs.TabActivated)
    def handle_tab_activated(self, event: Tabs.TabActivated):
        self.text_area.text = self.tab_content[event.tab.id]
        self.result_table.clear(columns=True)

    def on_descendant_focus(self, event: events.DescendantFocus):
        if type(event.widget) == DataTable:
            self.result_table.add_class("focused")
            self.text_area.remove_class("focused")
            self.tabs.remove_class("focused")
        if type(event.widget) == TextArea:
            self.text_area.add_class("focused")
            self.result_table.remove_class("focused")
            self.tabs.remove_class("focused")
        if type(event.widget) == Tabs:
            self.result_table.remove_class("focused")
            self.text_area.remove_class("focused")

    # handle key events outside of bindings
    def on_key(self, event: events.Key):
        if event.key == "ctrl+shift+up":
            if self.text_area.has_focus:
                self.tabs.focus()
            elif self.result_table.has_focus:
                self.text_area.focus()
        elif event.key == "ctrl+shift+down":
            if self.tabs.has_focus:
                self.text_area.focus()
            elif self.text_area.has_focus:
                self.result_table = self.result_table.focus()
                self.text_area = self.text_area.blur()

    def action_close_dialog(self):
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

    async def action_new_tab(self):
        # find the max tab ID and add one to get the next tab ID
        # tab IDs are tab-<id>, so split on "-" and take the second element to get the ID
        tab_ids = [int(tab_id.split("-")[1]) for tab_id in self.tab_content.keys()]
        next_id = max(tab_ids) + 1
        await self.tabs.add_tab(
            Tab(f"tab {next_id}", id=f"tab-{next_id}"), after=self.tabs.active_tab
        )
        self.tabs.action_next_tab()

    async def action_close_tab(self):
        # don't allow closing if only one tab open
        if self.tabs.tab_count == 1:
            return

        active_tab_id = self.tabs.active_tab.id
        await self.tabs.remove_tab(active_tab_id)
        del self.tab_content[active_tab_id]
        self.tabs.action_previous_tab()

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
            cur.close()
            cur.close()

        # after executing a statement, update the table list in case any tables were created or dropped
        self.table_list.items = self._get_table_list()
