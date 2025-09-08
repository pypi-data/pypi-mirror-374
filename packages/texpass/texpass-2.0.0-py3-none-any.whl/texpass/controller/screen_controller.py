from textual.app import App
from texpass.helper.account import Account


class ScreenController:
    def __init__(self, app: App) -> None:
        self.app = app
        self.account = None

    def to_login(self):
        from texpass.screens.login import LoginScreen, LoginController

        self.app.switch_screen(LoginScreen(LoginController(), self))
    
    def to_register(self):
        from texpass.screens.register import RegisterScreen

        self.app.switch_screen(RegisterScreen(self))

    def to_table(self, account: Account):
        """
        Switch to table (main) screen

        Sets Account object for this screen controller
        """
        from texpass.screens.table import TableScreen
        from texpass.controller.table_controller import TableController

        self.account = account
        self.app.switch_screen(TableScreen(TableController(account), self))

    def push_login(self):
        """
        First thing pushed when opening app
        """
        from texpass.screens.login import LoginScreen
        from texpass.controller.login import LoginController

        self.app.push_screen(LoginScreen(LoginController(), self))

    def push_delete(self):
        """
        Pushes DeleteAccountScreen

        If successful, switches to login screen
        """
        from texpass.screens.delete_account import DeleteAccountScreen, DeleteController
        
        def logout(status: bool):
            if status:
                self.account = None
                self.to_login()

        self.app.push_screen(DeleteAccountScreen(DeleteController(self.account)), logout)
