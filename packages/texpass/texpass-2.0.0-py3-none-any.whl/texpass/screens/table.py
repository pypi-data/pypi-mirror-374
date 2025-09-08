from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Footer
from textual.binding import Binding

from texpass.widgets.data_table import MyTable
from texpass.widgets.search_input import SearchInput
from texpass.screens.new_entry import NewEntryScreen
from texpass.controller.screen_controller import ScreenController
from texpass.controller.table_controller import TableController


class TableScreen(Screen):

    CSS_PATH = "../styles/main_screen.tcss"

    BINDINGS = [
        Binding("ctrl+e", "new_entry", "New entry", priority=True),
        Binding("ctrl+c", "copy", "Copy password", priority=True),
        Binding("ctrl+d", "delete_entry", "Delete entry", priority=True),
        Binding("escape", "logout", "Log out", priority=True),
        Binding("ctrl+delete", "delete_profile", "Delete profile", priority=True),
    ]

    def __init__(self, controller: TableController, screen_switcher: ScreenController):
        self.screen_switcher = screen_switcher
        self.controller = controller
        self.table = None
        super().__init__()

    def compose(self) -> ComposeResult:
        self.table = MyTable(self.controller)

        yield SearchInput()
        yield self.table
        yield Footer(show_command_palette=False)

    def on_my_table_fuzzied(self, message: MyTable.Fuzzied):
        self.table.show_fuzzy_result(message)

    def action_new_entry(self) -> None:
        def add_record(record: dict):
            self.table.add_new_row(**record)

        # this currently works without screen_switcher as it can directly be fed this controller
        self.app.push_screen(NewEntryScreen(self.controller), add_record)

    def action_copy(self) -> None:
        self.table.copy_cursor_password()
    
    def action_delete_entry(self) -> None:
        self.table.delete_cursor_row()

    def action_logout(self) -> None:
        self.screen_switcher.to_login()

    def action_delete_profile(self) -> None:
        self.screen_switcher.push_delete()
