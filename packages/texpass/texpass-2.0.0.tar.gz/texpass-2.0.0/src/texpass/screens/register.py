from textual.app import ComposeResult
from textual.screen import Screen

from texpass.controller.screen_controller import ScreenController
from texpass.widgets.register import RegisterWidget
from texpass.helper.switch_message import Switch


class RegisterScreen(Screen):
    """
    The login screen. First screen when opening the app
    """
    CSS_PATH = "../styles/login.tcss"

    def __init__(self, screen_switcher: ScreenController):
        self.switcher = screen_switcher
        super().__init__(classes="centered first_screen")

    def compose(self) -> ComposeResult:
        yield RegisterWidget()

    def on_switch(self, message: Switch):
        if message.switch_else:
            self.switcher.to_login()
        else:
            self.switcher.to_table(message.account)
