import re
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

import duckdb
from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (DataTable, Footer, Input, Markdown, Tab, Tabs,
                             TextArea, Tree)
from textual.widgets.text_area import Selection

from .help_content import help_md
from .screens.file_browser import FileBrowser
from .screens.menu import MenuModal
from .screens.menu_events import MenuEvent


class DuckUI(App):
    BINDINGS = [
        Binding(key="f1", action="toggle_menu", description="menu"),
        Binding(key="f2", action="toggle_help", description="help"),
        Binding(key="f9", action="execute_query", description="execute query"),
        Binding(key="ctrl+p", action="close_dialog", description="close dialog"),
    ]
    CSS_PATH = "./styles/style.tcss"

    def __init__(self, conn: duckdb.DuckDBPyConnection = None):
        self.conn = conn

        if self.conn is None:
            self.conn = duckdb.connect(":memory:")

        # mapping from tab ID to editor content, tab IDs are "tab-1", "tab-2" and so on
        self.tab_content = defaultdict(str)
        
        # keep track of last query ran, so if user exports result, can use a duckdb copy statement
        self.last_query = ""

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

    def _refresh_table_tree(self):
        # refreshing causes the tree to get recreated, which makes all nodes collapsed
        # keep track of what is expanded right now and expand them again after recreation
        nodes_to_expand = []

        for child in self.tables.root.children:
            if child.is_expanded:
                nodes_to_expand.append(str(child.label))

        self.tables.root.remove_children()
        cur = self.conn.cursor()

        for table in self._get_table_list():
            table_node = self.tables.root.add(table)
            
            cur.execute(f"describe table {table}")

            for rec in cur.fetchall():
                table_node.add_leaf(f"{rec[0]}: {rec[1]}")

            # expand the table_node if it was expanded before recreation
            if table in nodes_to_expand:
                table_node.expand()

        cur.close()

    def compose(self) -> ComposeResult:
        self.tables = Tree("tables", classes="table-browser-area")
        self.tables.root.expand()
        self._refresh_table_tree()

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
                self.tables,
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
            self.conn.execute(f"copy ({self.last_query}) to '{self.save_result_input.value}' (header)")
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
            self.tables.remove_class("focused")
        if type(event.widget) == TextArea:
            self.text_area.add_class("focused")
            self.result_table.remove_class("focused")
            self.tables.remove_class("focused")
        if type(event.widget) == Tabs:
            self.result_table.remove_class("focused")
            self.text_area.remove_class("focused")
            self.tables.remove_class("focused")
        if type(event.widget) == Tree:
            self.tables.add_class("focused")
            self.result_table.remove_class("focused")
            self.text_area.remove_class("focused")

    # handle key events outside of bindings
    async def on_key(self, event: events.Key):
        if event.key == "ctrl+shift+up":
            if self.text_area.has_focus:
                self.tabs.focus()
            elif self.result_table.has_focus:
                self.text_area.focus()
        elif event.key == "ctrl+shift+down":
            if self.tabs.has_focus:
                self.text_area.focus()
            elif self.text_area.has_focus:
                self.result_table.focus()
        elif event.key == "ctrl+shift+left":
            self.tables.focus()
        elif event.key == "ctrl+shift+right":
            self.text_area.focus()
        elif event.key == "ctrl+n":
            await self.action_new_tab()
        elif event.key == "ctrl+t":
            await self.action_close_tab()

    def handle_menu_event(self, event: MenuEvent):
        if event == MenuEvent.SAVE_SQL:
            self.save_sql_input.display = True
            self.save_sql_input.focus()
        elif event == MenuEvent.LOAD_SQL:
            self.push_screen(FileBrowser(), callback=self.handle_file_browser_event)
        elif event == MenuEvent.SAVE_RESULT:
            self.save_result_input.display = True
            self.save_result_input.focus()
        elif event == MenuEvent.EXIT:
            self.exit()

    def handle_file_browser_event(self, path: Path):
        if path is None:
            return
    
        with open(path) as file:
            self.text_area.text = file.read()

            # manually call this to ensure tab content is saved
            self.handle_editor_content_changed()

    def action_toggle_menu(self):
        self.push_screen(MenuModal(), callback=self.handle_menu_event)

    def action_close_dialog(self):
        # close help and file name inputs and refocus on editor
        self.help_box.display = False
        self.save_sql_input.display = False
        self.save_result_input.display = False
        self.text_area.focus()

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
            self.last_query = query
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

        # after executing a statement, update the table list in case any tables were created or dropped
        self._refresh_table_tree()
