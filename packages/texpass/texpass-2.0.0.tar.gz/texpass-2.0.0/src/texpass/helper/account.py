from argon2.low_level import hash_secret
from argon2 import Type, PasswordHasher
from argon2.exceptions import VerifyMismatchError

from sqlite3 import connect, IntegrityError
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

from texpass.exceptions.exceptions import *

# TODO use some kind of config file to get name 
PASSWORDS_DATABASE = "passwords.db"


class Account:
    def __init__(self, username: str = None, password: str = None, salt: str = None):
        self.username = username
        self.password = password
        self.salt = salt

    def get_hashed_password(self) -> bytes:
        hashed_password = hash_secret(
            secret = self.password.encode(), 
            salt = self.salt.encode(), 
            time_cost = 3,
            memory_cost = 65536, 
            parallelism = 4, hash_len = 30, 
            type = Type.ID
        )

        return hashed_password[-32:]
    
    def get_all_records(self) -> list[tuple]:
        con = connect(PASSWORDS_DATABASE)

        records = con.execute(
            "SELECT website, username FROM passwords WHERE account_name = ?;",
            (self.username,)
        ).fetchall()
        
        con.close()

        return records

    def get_key(self) -> Fernet:
        """
        To be used for creating key for password encryption/decryption    
        """
        return Fernet(urlsafe_b64encode(self.get_hashed_password()))
    
    def get_entry_password(self, entry_username: str, entry_website: str) -> str:
        """
        Get fetched plaintext password from entry username and website
        """
        con = connect(PASSWORDS_DATABASE)

        enc_pass = con.execute("SELECT encrypted_password FROM passwords \
                               WHERE account_name = ? \
                               AND username = ? \
                               AND website = ?;", 
                               (self.username, entry_username, entry_website)
                               ).fetchone()[0]
        con.close()
        
        password = self.get_key().decrypt(enc_pass).decode()

        return password

    def add_entry(self, entry_username: str, entry_website: str, entry_password: str):
        con = connect(PASSWORDS_DATABASE)

        try:
            with con:
                con.execute(
                    "INSERT INTO passwords (account_name, username, website, encrypted_password) \
                        VALUES (?, ?, ?, ?)", 
                        (self.username, entry_username, entry_website, entry_password)
                )
        except IntegrityError:
            con.close()
            raise EntryAlreadyExists()
        else:
            con.close()

    def delete_entry(self, entry_username: str, entry_website):
        con = connect(PASSWORDS_DATABASE)

        with con:
            con.execute(
                "DELETE FROM passwords WHERE account_name = ? AND username = ? AND website = ?", 
                (self.username, entry_username, entry_website)
            )
        
        con.close()


    def verify_password(self, password_to_verify: str) -> bool:
        """
        Simply does an equality expression over stored plaintext and given password
        """
        return password_to_verify == self.password

    @classmethod
    def from_login(cls, username: str, password: str):
        """
        Create account object from login details
        """
        # select from database
        con = connect(PASSWORDS_DATABASE)
        query = con.execute("SELECT password_hash, salt FROM user_login WHERE account_name = ?;", (username,)).fetchone()
        con.close()

        # check username
        if query is None:
            raise UsernameDoesNotExist()
        else:
            # username exists, now verify password
            hash_, salt = query

            try:
                PasswordHasher().verify(hash_, password)
            except VerifyMismatchError:
                raise WrongPassword
            else:
                # password verified
                return cls(username, password, salt)
    
    @classmethod
    def from_register(cls, username: str, password: str, salt: str):
        """
        Create account object from register details

        Saves new account to database if username is unique
        """
        con = connect(PASSWORDS_DATABASE)
        try:
            # insert to database
            with con:
                con.execute(
                    "INSERT INTO user_login (account_name, password_hash, salt) \
                        VALUES (?, ?, ?);",
                        (username, PasswordHasher().hash(password), salt)
                    )
        except IntegrityError:
            # if username already exists
            con.close()
            raise UsernameAlreadyExists("Username already exists!")
        else:
            # successful. close and return
            con.close()
            return cls(username, password, salt)

    def delete_account(self):
        con = connect(PASSWORDS_DATABASE)
        
        with con:
            con.execute("DELETE FROM passwords WHERE account_name = ?", (self.username,))
            con.execute("DELETE FROM user_login WHERE account_name = ?", (self.username,))
        
        con.close()