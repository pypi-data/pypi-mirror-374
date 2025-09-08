from textual.containers import Vertical
from textual.widgets import Button, Static
from textual import on
from textual.app import ComposeResult

from texpass.widgets.submit_input import SubmitInput
from texpass.controller.register import RegisterController
from texpass.helper.switch_message import Switch


class VerticalButtons(Vertical):
    """
    Vertical consisting of two buttons

    Additional keybinds up and down to focus on previous/next widget respectively
    """
    def __init__(self, msg_widget: Static):
        self.msg_widget = msg_widget
        super().__init__()
        
    BINDINGS = [
        ("up", "app.focus_previous", "Focus on previous widget"),
        ("down", "app.focus_next", "Focus on next widget")
    ]

    def __send_update(self, value: str):
        self.msg_widget.update(value)

    def compose(self) -> ComposeResult:
        yield Button("Register",id="register_button", classes="submit elements")
        yield Button("Back", id="back_button", classes = "elements")

    def field_empty(self, value: str) -> bool:
        return value.strip() == ""

    @on(Button.Pressed, "#back_button")
    def on_back(self):
        # switch to login
        self.post_message(Switch(switch_else=True))

    @on(Button.Pressed, "#register_button")
    def on_register(self):
        controller = RegisterController()
        first_password = ""

        for input_ in self.parent.query("SubmitInput").results(SubmitInput):
            # empty field check
            if self.field_empty(input_.value):
                self.__send_update(f"Please fill {input_.name} field")
                return

            # new_username checks
            if input_.id == "new_username":
                username = input_.value
            
            # password/repeat password check
            elif input_.id == "new_password":
                # save password for check later
                first_password = input_.value

            elif input_.id == "new_password_again":
                # check password match
                if first_password == input_.value:
                    break
                else:
                    self.__send_update("Passwords don't match")
                    return
        
        # details are entered correctly
        register_status = controller.register(username, first_password)
        self.__send_update(register_status.message)

        if register_status.status:
            self.post_message(Switch(account=register_status.account))


class RegisterWidget(Vertical):
    def __init__(self):
        super().__init__(classes="centered first_screen_main")

    def compose(self) -> ComposeResult:
        # username submitInput widget
        username = SubmitInput(
            placeholder="Enter new username", 
            classes="input elements",
            max_length=100,
            id = "new_username",
            name = "username"
        )

        username.border_title = "Username"

        # password submitInput widget
        password = SubmitInput(
            placeholder="Enter new password", 
            password=True, 
            classes="input elements",
            id="new_password",
            name = "password"    
        )

        password.border_title = "Password"

        # retype password submitInput widget
        re_password = SubmitInput(
            placeholder="Enter password again", 
            password=True, 
            classes="input elements",
            id="new_password_again",
            name = "password"
        )

        re_password.border_title = "Password Again"


        add_msg = Static(id = "additional_message", classes = "elements")
        
        # yield it all
        yield Static("<< Password Manager >>", classes="elements", id = "title")
        yield username
        yield password
        yield re_password
        yield VerticalButtons(add_msg)
        yield add_msg
