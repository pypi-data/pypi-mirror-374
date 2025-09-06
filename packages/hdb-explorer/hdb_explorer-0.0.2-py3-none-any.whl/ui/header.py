import asyncio
from textual import work
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import (    
    Label,
    Button,
)
from textual.containers import (
    Container,
)

from textual.app import RenderResult
from textual.events import Click
from .add_system import AddSystem

from common import (
    Constants,
    SQL_AutoSave,
    GlobalAccessor
)
from db import DbPoolManager

class HeaderXClose(Widget):
    """Display an 'icon' on the right of the header."""

    DEFAULT_CSS = """
        HeaderXClose {
            dock: right;
            width: 3;
            padding: 0 0 0 1;
            align: center middle;
        }

        HeaderXClose:hover {
            color: red;
        }
    """

    icon = "✕"

    def on_mount(self) -> None:
        if self.app.ENABLE_COMMAND_PALETTE:
            self.tooltip = "Exit"
        else:
            self.disabled = True

    async def on_click(self, event: Click) -> None:
        sql_text = await GlobalAccessor.sql_editor_text()
        SQL_AutoSave.file_content = sql_text
        await SQL_AutoSave.save()
        self.app.exit()

    def render(self) -> RenderResult:
        return self.icon

class HeaderPlusAdd(Widget):
    """Display an 'icon' on the right of the header."""

    DEFAULT_CSS = """
        HeaderPlusAdd {
            dock: right;
            width: 6;
            padding: 0 0 0 1;
            align: center middle;
        }

        HeaderPlusAdd:hover {
            color: green;
        }
    """

    icon = "+"

    def __init__(self) -> None:
        GlobalAccessor.enable_header_plus_button = self.enable_button
        super().__init__()

    def on_mount(self) -> None:
        if self.app.ENABLE_COMMAND_PALETTE:
            self.tooltip = "Add System"
        else:
            self.disabled = True

    @work
    async def on_click(self, event: Click) -> None:
        #self.app.push_screen(AddSystem())
        r = await self.app.push_screen_wait(AddSystem())

    def render(self) -> RenderResult:
        return self.icon
    
    def enable_button(self, enable: bool = True) -> None:
        self.disabled = not enable
    
class HeaderRunSQL(Widget):
    """Display an 'icon' on the right of the header."""

    DEFAULT_CSS = """
        HeaderRunSQL {
            dock: right;
            width: 9;
            padding: 0 0 0 1;
            align: center middle;
        }

        HeaderRunSQL:hover {
            color: green;
        }
    """

    icon = "▶"

    def __init__(self) -> None:
        GlobalAccessor.enable_header_play_button = self.enable_button
        super().__init__()

    def on_mount(self) -> None:
        if self.app.ENABLE_COMMAND_PALETTE:
            self.tooltip = "Execute SQL"
        else:
            self.disabled = True

    @work
    async def on_click(self, event: Click) -> None:

        sql_text = await GlobalAccessor.sql_editor_text()
        SQL_AutoSave.file_content = sql_text
        asyncio.create_task(SQL_AutoSave.save())

        if GlobalAccessor.Header.db_sys_text_get() == "":
            self.notify("Please select a HANA Db System", title="No System selected", severity="warning", timeout=Constants.SET_NOTIFY_TIMEOUT)
        elif not GlobalAccessor.Header.db_sys_status_get():
            self.notify("Connection to SAP HANA Db is Not established", title="Connection Failed", severity="warning", timeout=Constants.SET_NOTIFY_TIMEOUT)
        else:
            if sql_text == "":
                self.notify("Please enter SQL in the editor", title="No SQL Provided", severity="warning", timeout=Constants.SET_NOTIFY_TIMEOUT)
            else:
                GlobalAccessor.enable_header_plus_button(False)
                GlobalAccessor.spinner_sql_editor()
                self.set_timer(Constants.SET_TIMER_TIME, self.execute_query)

    def render(self) -> RenderResult:
        return self.icon
    
    def enable_button(self, enable: bool=True) -> None:
        self.disabled = not enable

    @work(thread=True)
    async def execute_query(self) -> None:
        sql_text = await GlobalAccessor.sql_editor_text()
        result = DbPoolManager[GlobalAccessor.Header.db_sys_text_get()].execute(sql_text)
        await GlobalAccessor.sql_result_viewer_refresh(result)
        GlobalAccessor.enable_header_plus_button(True)
        GlobalAccessor.spinner_sql_editor(False)

class HeaderSystemName(Widget):

    DEFAULT_CSS = """
        HeaderSystemName {
            dock: left;
            width: auto;
            padding: 0 0 0 1;
            align: left middle;
        }
    """

    icon = "🔗"
    text = reactive("")

    def __init__(self) -> None:
        GlobalAccessor.Header.db_sys_text_update = self.update_text
        GlobalAccessor.Header.db_sys_text_get = self.get_text
        GlobalAccessor.Header.db_sys_status_get = self.get_status
        super().__init__()

    def on_mount(self) -> None:
        if self.app.ENABLE_COMMAND_PALETTE:
            self.tooltip = "Selected System"
        else:
            self.disabled = True

    def render(self) -> RenderResult:
        r_text = f"{self.icon} "
        if self.text.strip() == '':
            r_text += "[red]No SAP HANA Db Connected[/]. [italic]Select from the tree.[/]"
        else:
            if self.status:
                r_text += f"Connected to: [green]{self.text}[/]"
            else:
                r_text += f"Unable to connect to: [red]{self.text}[/]"
        return r_text
    
    def update_text(self, text, status: bool) -> None:
        self.status = status
        self.text = text

    def get_text(self) -> str:
        return self.text
    
    def get_status(self) -> bool:
        return self.status

    
class AppHeader(Container):
    DEFAULT_CSS = """
        AppHeader {
            height: 3;
            dock: top;
            border: round $foreground;
            align: center middle;
            text-align: center;
        }
        
        Label {
            text-style: bold;
        }
    """

    def compose(self):
        yield HeaderSystemName()
        #yield Label("SAP HANA Db Explorer")
        yield HeaderRunSQL()
        yield HeaderPlusAdd()
        yield HeaderXClose()
        return super().compose()
    