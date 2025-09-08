from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Footer

from texpass.widgets.login import LoginWidget
from texpass.helper.switch_message import Switch
from texpass.controller.login import LoginController
from texpass.controller.screen_controller import ScreenController


class LoginScreen(Screen):
    """
    The login screen. First screen when opening the app
    """
    CSS_PATH = "../styles/login.tcss"
    BINDINGS = [
        Binding("escape", "exit_app", "Exit app", priority=True),
    ]


    def __init__(self, controller: LoginController, switcher: ScreenController):
        self.controller = controller
        self.switcher = switcher
        super().__init__(classes="centered first_screen")

    def compose(self) -> ComposeResult:
        login_widget = LoginWidget(self.controller)
        
        yield login_widget
        
    def on_switch(self, message: Switch):
        if message.switch_else:
            self.switcher.to_register()
        else:
            self.switcher.to_table(message.account)

    def action_exit_app(self):
        self.app.exit()