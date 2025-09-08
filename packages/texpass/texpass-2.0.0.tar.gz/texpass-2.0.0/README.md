# Texpass - Password Manager for the Terminal

Texpass is a password manager written in Python with a text-based user interface. It uses the Textual framework for the UI.

### Security features
- Uses Argon2 hashing to store master password in database.
- Encryption keys are derived from the master password, and hence never stored in database.
- Can generate securely random passwords

### Installation
This is currently available as a CLI tool and as a TUI.

For the CLI version, please see the [v1.x branch](https://github.com/Rinceri/password-manager/tree/v1.x)

The most up-to-date and actively maintained version is the TUI version. Available on PyPI:
```sh
python3 -m pip install -U texpass 
```
And run with:
```sh
texpass
```
The application can be quit by pressing the escape key.

### Contributing
Feel free to report any bugs or additional features.
