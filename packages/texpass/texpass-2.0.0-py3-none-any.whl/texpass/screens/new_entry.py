from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Static
from textual.screen import ModalScreen
from textual.app import ComposeResult

from texpass.controller.table_controller import TableController
from texpass.exceptions.exceptions import EntryAlreadyExists
from texpass.widgets.submit_input import SubmitInput

class NewEntryScreen(ModalScreen):
    """
    Screen when creating new password
    """
    CSS_PATH = "../styles/modal_screens.tcss"
    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen")
    ]

    def __init__(self, controller: TableController):
        self.controller = controller
        super().__init__(classes="centered", id="new_modal")

    def compose(self) -> ComposeResult:
        with Vertical(id="new_entry_vertical"):
            yield Static("Create Entry")
            
            username_input = SubmitInput(placeholder="Username", id = "usname")
            username_input.border_title = "Username"
            
            website_input = SubmitInput(placeholder="Website", id = "webs")
            website_input.border_title = "Website"

            password_input = SubmitInput(value=self.controller.make_password(), placeholder="Password", id="pword", password=True)
            password_input.border_title = "Password"

            yield username_input
            yield website_input
            yield password_input
            yield Static(id = "status")
            with Horizontal():
                yield Button("Submit", classes = "submit")
                yield Button("Cancel", id = "cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()

        username = self.query_one("#usname").value
        website = self.query_one("#webs").value
        password = self.query_one("#pword").value
        
        if username == "" or website == "":
            self.query_one("#status", Static).update("Please enter all fields")
            return
        
        try:
            id = self.controller.add_entry(username, website, password)
        except EntryAlreadyExists:
            self.query_one("#status", Static).update("Entry already exists")
            return

        record = {"id": id, "website": website, "username": username}
        self.screen.dismiss(record)
