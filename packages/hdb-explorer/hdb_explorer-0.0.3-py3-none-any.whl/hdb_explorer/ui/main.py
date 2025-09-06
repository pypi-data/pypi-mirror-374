from . import (
    Screen,
    ComposeResult,
    AppHeader
)
from common import (
    Config,
    Constants,
    DB_Systems,
    GlobalAccessor
)
from textual.widgets import (
    TextArea,
    RichLog
)
from textual.containers import (
    Container,
    Vertical,
    Grid
)

from rich.table import Table

from .db_tree import DbTree
from .sql_editor import SQLEditor
from .sql_result_viewer import SQLResultViewer

class Main(Screen):

    DEFAULT_CSS = """
        Grid {
            grid-size: 2;
            grid-columns: 30% 70%;
            height: 100%;
        }
        #con_db_tree {
            width: 100%;
            border: round $foreground;
        }
        #con_sql_editor {
            height: 50%;
            border: round $foreground;
        }
        #con_sql_viewer {
            height: 50%;
            border: round $foreground;
        }

    """

    def __init__(self) -> None:
        GlobalAccessor.spinner_db_tree = self.spinner_db_tree
        GlobalAccessor.spinner_sql_editor = self.spinner_sql_editor
        GlobalAccessor.spinner_sql_viewer = self.spinner_sql_editor
        super().__init__()

    def compose(self) -> ComposeResult:
        yield AppHeader(id="Header")
        yield Grid(
            Container(
                DbTree(id="tre_db_systems"),
                id="con_db_tree"
            ),
            Vertical(
                Container(
                    SQLEditor(id="sql_editor"),
                    id="con_sql_editor"
                ),
                Container(
                    SQLResultViewer(id="ta_result"),
                    id="con_sql_viewer"
                )
            )
        )

    async def on_mount(self) -> None:
        self.query_one("#con_sql_editor").border_title = "SQL Editor"
        self.query_one("#con_sql_viewer").border_title = "SQL Result"

        if not DB_Systems.file_loaded:
            self.notify(f"File content cannot be decoded. Please fix [italic]{Config.AddSystem.FILENAME}[/] and restart the app !", title="Error", severity="error", timeout=Constants.SET_NOTIFY_TIMEOUT)
        
    def spinner_db_tree(self, spin: bool=True) -> None:
        self.query_one("#con_db_tree").loading = spin
        GlobalAccessor.enable_header_plus_button(not spin)

    def spinner_sql_editor(self, spin: bool=True) -> None:
        self.query_one("#con_sql_editor").loading = spin
        GlobalAccessor.enable_header_play_button(not spin)

    def spinner_sql_viewer(self, spin: bool=True) -> None:
        self.query_one("#con_sql_viewer").loading = spin