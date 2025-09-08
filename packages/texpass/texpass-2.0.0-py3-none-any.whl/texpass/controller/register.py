from secrets import choice
import string

from texpass.helper.account import Account
from texpass.helper.status import Status
from texpass.exceptions.exceptions import UsernameAlreadyExists


class RegisterController:
    def register(self, username: str, password: str) -> Status:
        try:
            account = Account.from_register(username, password, self.make_salt())
        except UsernameAlreadyExists:
            return Status(False, message="Username already exists")
        else:
            return Status(True, account=account, message="Registering and logging you in...")

    def make_salt(self, length: int = 16) -> str:
        """
        Make a salt string
        """
        return ''.join([choice(string.ascii_letters + string.digits) for _ in range(length)])
