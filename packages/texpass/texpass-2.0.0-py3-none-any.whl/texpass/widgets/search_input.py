from textual.widgets import Input
from textual.binding import Binding

class SearchInput(Input):
    BINDINGS = [
        Binding("down", "to_table", "Go to table", show = False)
    ]

    def __init__(self):
        super().__init__(
            placeholder = "Search",
            select_on_focus = False
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Posts a Fuzzied message
        """
        from texpass.widgets.data_table import MyTable
        
        self.post_message(MyTable.Fuzzied(event.value))

    def action_to_table(self) -> None:
        from texpass.widgets.data_table import MyTable

        self.parent.query_one(MyTable).focus()