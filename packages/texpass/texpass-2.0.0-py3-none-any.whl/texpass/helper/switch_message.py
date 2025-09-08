from textual.message import Message

from texpass.helper.account import Account


class Switch(Message):
    """
    Switch screen with account
    """
    def __init__(self, *, account: Account = None, switch_else: bool = False):
        """
        If login/register successful, set account
        If user wants to switch to the other screen (login/register),
            set switch_else to True
        """
        self.account = account
        self.switch_else = switch_else
        super().__init__()
