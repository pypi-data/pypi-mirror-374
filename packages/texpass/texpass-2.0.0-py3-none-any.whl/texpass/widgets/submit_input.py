from textual.widgets import Input, Button


class SubmitInput(Input):
    """
    Custom input class that has modified keybind where ENTER key  
    presses the button with default class "submit" on the screen
    """
    BINDINGS = [("enter", "press_submit", "Presses button with class submit")]

    def __init__(self, *, class_name = "submit", **kwargs):
        """
        Prefixes class_name with "." to query it on the screen
        """
        self.class_ = "." + class_name
        super().__init__(**kwargs)

    def action_press_submit(self):
        self.screen.query_one(self.class_, Button).press()
