from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Static
from textual.screen import ModalScreen
from textual.app import ComposeResult

from texpass.helper.account import Account
from texpass.widgets.submit_input import SubmitInput

class DeleteController:
    def __init__(self, account: Account):
        self.account = account

    def delete_account(self, input_password: str) -> bool:
        if self.account.verify_password(input_password):
            self.account.delete_account()
            return True
        else:
            return False


class DeleteAccountScreen(ModalScreen):
    """
    Screen when deleting account
    """
    CSS_PATH = "../styles/modal_screens.tcss"
    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen")
    ]

    def __init__(self, controller: DeleteController):
        self.controller = controller
        super().__init__(classes = "centered")

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Are you sure you want to delete your account?\nType in your master password to confirm.", id = "delete_title")
            yield Static("Once your account is deleted, all records will be deleted forever", id = "warning")
            yield SubmitInput(placeholder="Password", password=True, id = "pword")
            yield Static(id="status")
            with Horizontal():
                yield Button("Cancel", id="cancel")
                yield Button("Delete account", id="submit", classes="submit", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            result = self.controller.delete_account(self.query_one(SubmitInput).value)
            
            if result:
                self.screen.dismiss(result)
            else:
                self.query_one("#status", Static).update("Wrong password entered")
            
        elif event.button.id == "cancel":
            self.screen.dismiss(False)
