import sqlite3


def setup_database():
    # Create login table; Store login info; Create password table
    con = sqlite3.connect('passwords.db')
    
    with con:
        con.execute("""CREATE TABLE IF NOT EXISTS user_login (
            account_name TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt TEXT
            );""")
        
        con.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                account_name TEXT,
                username TEXT,
                website TEXT,
                encrypted_password TEXT,

                PRIMARY KEY (account_name, username, website)
            );""")

    con.close()
