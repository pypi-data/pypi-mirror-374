from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Label


class ConfirmScreen(ModalScreen):
    CSS_PATH = "../styles/modal_screens.tcss"

    BINDINGS = [
        ("escape", "dismiss(False)", "Cancel"),
    ]

    def __init__(self):
        super().__init__(classes = "centered")

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to delete this entry?", id="question"),
            Button("Delete", variant="error", id="delete"),
            Button("Cancel", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "delete":
            self.dismiss(True)
        else:
            self.dismiss(False)
