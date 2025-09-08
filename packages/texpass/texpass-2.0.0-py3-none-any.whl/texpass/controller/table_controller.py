from secrets import choice
from string import printable
from pyperclip import copy

from texpass.model.table import Table, Columns
from texpass.helper.account import Account


class TableController:
    def __init__(self, account: Account):
        self.account = account
        self.table = Table()

    def get_column_ordering(self) -> Columns:
        return self.table.columns

    def populate_internal_table(self):
        records = self.account.get_all_records()
        self.table.populate_table(records)

    def generate_rows(self):
        """
        Generator for filling up UI table

        Key being the ID of the row
        """
        generator = self.table.generator()

        for row in generator:
            yield (row, self.table.get_key(row))

    def generate_fuzzied_rows(self, query: str):
        """
        Generator for filling up table after fuzzy search

        Does not check if query is empty
        """
        # don't care about fuzzy score right now
        for record, _ in self.table.get_fuzzied_records(query):
            yield (record, self.table.get_key(record))

    def make_password(self) -> str:
        """
        This is currently a simple function that will be worked on in the future
        """
        return ''.join(choice(printable) for _ in range(30))
    
    def encrypt_password(self, password: str) -> bytes:
        """
        To be used when encrypting passwords to store within this account
        """
        key = self.account.get_key()
        return key.encrypt(password.encode())
    
    def add_entry(self, username: str, website: str, plain_password: str) -> int:
        """
        Adds password entry for this account. Also adds it to internal table.

        Returns ID of internal table record

        Raises EntryAlreadyExists if username and website is not unique
        """
        encrypted = self.encrypt_password(plain_password)
        self.account.add_entry(username, website, encrypted.decode())
        id = self.table.add_record(website, username)

        return id

    def copy_password_at(self, username: str, website: str):
        """
        Copy password with specified website and username
        """
        password = self.account.get_entry_password(username, website)

        copy(password)
    
    def delete_entry(self, username: str, website: str):
        """
        Deletes entry for specified website and username

        Updates internal table
        """
        self.account.delete_entry(username, website)

        self.populate_internal_table()