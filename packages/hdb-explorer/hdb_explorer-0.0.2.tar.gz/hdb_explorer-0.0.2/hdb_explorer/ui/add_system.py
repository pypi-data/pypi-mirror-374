from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import (
    Container,
    Horizontal,
    Grid
)
from textual.widgets import (
    Label,
    Input,
    Button
)
from textual import (
    on
)

from common import (
    Config,
    Constants,
    DB_Systems,
    GlobalAccessor
)

class AddSystem(ModalScreen):
    CSS = """
        AddSystem {
            align: center middle;
        }
        Container {
            align: left middle;
            width: 60%;
            height: auto;
            border: round $foreground;
            padding: 0 1;
        }
        Label {
            width: auto;
        }
        #lbl_add_sys_header {
            background: $foreground 10%;
            width: 100%;
            text-align: center;
            margin: 0 0 1 0;
        }
        Input {
            min-width: 80%;
            height: 1;
            padding: 0;
            margin: 0;
            border: none;
        }
        Horizontal {
            height: 5;
            padding: 1;
            align: center middle;
        }
        Grid {
            grid-size: 2;
            grid-columns: auto 1fr;
            height: auto;
        }

        Button {
            margin: 0 1 0 1;  # Top, right, bottom, left
        }  
    """
    def compose(self) -> ComposeResult:
        with Container() as _:
            yield Label("Add SAP HANA Db System", id="lbl_add_sys_header")

            yield Grid(
                Label("Name:"),
                Input("", id="inp_name"),

                Label("Address:"),
                Input("", id="inp_host"),

                Label("Port:"),
                Input("", id="inp_port", type="number"),

                Label("User:"),
                Input("", id="inp_user"),

                Label("Password:"),
                Input("", id="inp_password"),
            )

            yield Horizontal(
                Button("Add System", id="btn_add_sys"),
                Button("Cancel", id="btn_cancel_sys")
            )

    async def on_mount(self) -> None:
        if not DB_Systems.file_loaded:
            self.notify(f"File content cannot be decoded. Please fix [italic]{Config.AddSystem.FILENAME}[/] and restart the app !", title="Error", severity="error", timeout=Constants.SET_NOTIFY_TIMEOUT)
            self.query_one("#btn_add_sys").disabled = True

    @on(Button.Pressed, "#btn_cancel_sys")
    async def button_pressed_cancel(self, event: Button.Pressed) -> None:
        self.dismiss()

    @on(Button.Pressed, "#btn_add_sys")
    async def button_pressed_add(self, event: Button.Pressed) -> None:
        name: str = self.query_one("#inp_name").value.strip()
        if len(name) == 0:
            self.notify(f"Name cannot be empty!", title="Error", severity="error", timeout=Constants.SET_NOTIFY_TIMEOUT)
        else:
            result = await DB_Systems.update(
                {
                    "name": name,
                    "host": self.query_one("#inp_host").value,
                    "port": self.query_one("#inp_port").value,
                    "user": self.query_one("#inp_user").value,
                    "password": self.query_one("#inp_password").value
                }
            )
            if not result == None:
                self.notify(f"Record already present with {name.strip()}", title="Status", severity="error", timeout=Constants.SET_NOTIFY_TIMEOUT)
            else:
                self.notify(f"Added Successfully", title="Status", severity="information", timeout=Constants.SET_NOTIFY_TIMEOUT)
                await GlobalAccessor.db_tree_refresh()
                self.dismiss()
