from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static
from textual import on

from texpass.widgets.submit_input import SubmitInput
from texpass.controller.login import LoginController
from texpass.helper.switch_message import Switch


class VerticalButtons(Vertical):
    BINDINGS = [
        ("up", "app.focus_previous", "Focus on previous widget"),
        ("down", "app.focus_next", "Focus on next widget")
    ]

    def __init__(self, controller: LoginController, add_msg: Static):
        self.msg_widget = add_msg
        self.controller = controller
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Button("Login",id="login_button", classes="submit elements")
        yield Button("Create account", id="register_button", classes="elements")

    @on(Button.Pressed, "#register_button")
    def on_register(self):
        self.post_message(Switch(switch_else=True))

    def field_empty(self, value: str) -> bool:
        return value.strip() == ""

    @on(Button.Pressed, "#login_button")
    def on_login(self):        
        # getting inputs and storing them
        for input_ in self.parent.query("SubmitInput").results(SubmitInput):
            # empty field check
            if self.field_empty(input_.value):
                self.msg_widget.update(f"Please fill {input_.name} field")
                return

            # get username
            if input_.id == "username":
                username = input_.value
                continue
            
            # password
            elif input_.id == "inp_password":
                password = input_.value
                break
        
        login_status = self.controller.log_in(username, password)
        self.msg_widget.update(login_status.message)

        if login_status.status:
            self.post_message(Switch(account=login_status.account))


class LoginWidget(Vertical):
    def __init__(self, controller: LoginController) -> None:
        self.controller = controller
        super().__init__(classes="centered first_screen_main")

    def compose(self) -> ComposeResult:
        username = SubmitInput(
            placeholder="Enter username", 
            classes="input elements",
            id = "username",
            name = "username"
        )
        username.border_title = "Username"
        
        password = SubmitInput(
            placeholder="Enter password", 
            password=True, 
            classes="input elements",
            id="inp_password",
            name="password"
        )
        password.border_title = "Password"

        add_msg = Static(id = "additional_message", classes="elements")
        
        yield Static("<< Password Manager >>", classes="elements", id = "title")
        yield username
        yield password
        yield VerticalButtons(self.controller, add_msg)
        yield add_msg
