from texpass.helper.account import Account

class Status:
    def __init__(self, status: bool, *, account: Account = None, message: str = None):
        self.status = status
        self.account = account
        self.message = message
