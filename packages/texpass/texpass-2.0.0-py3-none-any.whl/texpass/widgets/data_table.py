from textual.widgets import DataTable
from textual import events
from textual.message import Message
from textual.widgets.data_table import RowDoesNotExist, ColumnKey
from textual.geometry import Size

from texpass.screens.confirm import ConfirmScreen
from texpass.controller.table_controller import TableController
from texpass.helper.timed_string import TimeString
from texpass.widgets.search_input import SearchInput

class MyTable(DataTable):
    class Fuzzied(Message):
        """Posted when a fuzzy search happens"""
        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    BINDINGS = [
        ("right", "page_down", "Move one page down"),
        ("left", "page_up", "Move one page up")
    ]

    def __init__(self, controller: TableController):
        self.controller = controller
        self.digit_presses = TimeString(400 * 10**6)

        super().__init__(cursor_type="row", zebra_stripes=True, header_height=2)

    def on_mount(self):
        self.controller.populate_internal_table()
        self.add_columns()
        self.fill_table()

        for column in self.columns_.columns:
            if column.ratio > 0:
                # since we will manually set these widths, I think its wise to set this to False. If I leave this to True, 
                # ... I need to set content width for things to take effect
                # and when downsizing table, confusing things happen when the content width > col width assigned by ratio
                # the table width becomes total of all column content widths but then it resizes the columns perfectly
                # this causes an empty region even after the columns ended, 
                # ... which i assume is for the content width i truncated when setting it to width
                self.columns[column.column_name].auto_width = False

    def on_resize(self):
        # prepare yourself, i myself have no idea how this works

        # width of columns with no ratio (i.e. auto width/minimum width)
        min_width_total = 0
        # width of all columns
        total_width = 0

        # iterate through no ratio columns 
        for column in self.columns_.columns:
            if column.ratio == 0:
                width = self.columns[ColumnKey(column.column_name)].width
                min_width_total += width
                total_width += width
        
        # get space we can use for filling out columns with ratioed width (ie table width - no ratio columns)
        # subtracting by 2 more because it sometimes causes the table to size more than the width of the visible table
        # this also prevents the horizontal scrollbar from appearing for split seconds which happened earlier
        free_column_space = self.columns_.get_free_column_space(self.cell_padding, min_width_total, self.size.width) - 2

        # now set width of columns with ratioed width
        for column in self.columns_.columns:
            # get width
            width = self.columns_.get_width(column.column_name, free_column_space)

            if column.ratio > 0:
                self.columns[ColumnKey(column.column_name)].width = width
                total_width += width
        
        # now heres what I don't understand. I need to manually size the datatable, which I don't get why
        # if I don't set the height, everytime I downsize the table, the height of the table increases by 1
        # ... or when i use fuzzy search on full screen, it increases the height by 1 only once
        # if I don't set the size at all, when downsizing after adding a row or adding rows via fuzzy search on full screen
        # ... the table width remains the same as the full screen width, while the column width adjusts to the new width
        # Theres more stuff I don't understand, please see on_mount > setting auto_width to False

        # BUG: when resizing the table/ adding/removing rows, 
        # ...for a split second, it will show the scrollbars (when it doesn't have to)

        # I think the bug and my confusion stems from the internal impl'tion of DataTable, e.g. look at _update_dimensions
        height = self.row_count + self.header_height
        self.virtual_size = Size(total_width, height)
        self.refresh()

    def add_columns(self):
        """
        Add this table's columns before filling table
        """
        # get Columns object
        # this kind of breaks the MVC because the view is directly interacting with the model
        self.columns_ = self.controller.get_column_ordering()

        for column in self.columns_.columns:
            super().add_column(column.column_name, key = column.column_name)

    def fill_table(self):
        """
        Adds all DataTable rows. Requires a populated internal table

        Note that this does not clear the table or add columns
        """
        rows = self.controller.generate_rows()
        
        for row, key in rows:
            self.add_row(*row, key = key)

    def show_fuzzy_result(self, message: Fuzzied):
        """
        Update table records based on new fuzzy search

        If empty, shows all records
        """
        # clear table
        self.clear()

        # if query is not ""
        if message.query:
            fuzzied_records = self.controller.generate_fuzzied_rows(message.query)
        else:
            # since there is no search, display all records
            self.fill_table()
            return
        
        for record, key in fuzzied_records:
            self.add_row(*record, key = key)

    def add_new_row(self, id: int, website: str, username: str):
        """
        Use when adding new entry to the DataTable.
        
        Note that this does not commit to database. Use controller for that.
        """
        self.add_row(id, website, username, key = str(id))

    def copy_cursor_password(self) -> None:
        """
        Copy password at cursor row
        """
        if self.row_count < 1:
            return
        try:
            _, website, username = self.get_row_at(self.cursor_row)
        except RowDoesNotExist:
            return
        
        self.controller.copy_password_at(username, website)
        self.notify("Password has been copied", title="Copy successful", timeout=3)

    def delete_cursor_row(self) -> None:
        """Delete entry at cursor row"""
        if self.row_count < 1:
            return
        try:
            _, website, username = self.get_row_at(self.cursor_row)
        except RowDoesNotExist:
            return

        def process_delete(confirmed: bool):
            if confirmed:
                # delete entry from database
                self.controller.delete_entry(username, website)
                # fill table from scratch
                self.clear()
                self.fill_table()
    
        # this currently works without screen_switcher as this is a simple true/false return
        self.app.push_screen(ConfirmScreen(), process_delete)

    def _on_key(self, event: events.Key):
        # move to a specific index
        # can move to double digit index cells within 400 ms
        if event.character in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            # rown as in row number
            id_key = self.digit_presses.send(event.character)

            # move cursor to final number
            try:
                # move to row index from ID (key)
                row_index = self.get_row_index(id_key)
                self.move_cursor(row = row_index)
            except RowDoesNotExist:
                pass
        # is a character, type it to Input
        elif event.is_printable:
            inp = self.parent.query_one("Input", SearchInput)
            inp.value += event.character
            # move cursor to end of input
            inp.action_cursor_right()
            # focus on input widget
            inp.focus()

        elif event.key == "backspace":
            inp = self.parent.query_one("Input", SearchInput)
            inp.focus()