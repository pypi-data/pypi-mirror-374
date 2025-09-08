from secrets import choice
from string import printable

# for password generation

def make_password() -> str:
    """
    This is currently a simple function that will be worked on in the future
    """
    return ''.join(choice(printable) for _ in range(30))