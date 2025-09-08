from textual.app import App

from texpass.controller.screen_controller import ScreenController


class MainApp(App):

    def on_mount(self):
        ScreenController(self).push_login()


def main():
    """
    Creates the App and runs it
    """
    from texpass import setup_app

    setup_app.setup_database()

    app = MainApp()
    app.run()

if __name__ == "__main__":
    main()
