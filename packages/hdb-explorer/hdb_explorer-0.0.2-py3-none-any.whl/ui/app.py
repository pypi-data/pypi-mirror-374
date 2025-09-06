from . import (
    App,
    Main
)
               

class HanaDbExolorer(App):
    def on_ready(self) -> None:
        self.theme = "nord"
        self.push_screen(Main())