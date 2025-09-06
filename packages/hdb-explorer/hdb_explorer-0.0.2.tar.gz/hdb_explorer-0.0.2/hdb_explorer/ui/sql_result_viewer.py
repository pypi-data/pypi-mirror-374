from textual import (
    on, 
    work
)
from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import (
    DataTable,
    Label,
    Button,
    TextArea
)
from textual.containers import (
    Container,
    Vertical
)
from common import (
    Config,
    Constants,
    DB_Systems,
    GlobalAccessor
)

class SQLResultViewer(Widget):

    def __init__(self, *args, **kwargs) -> None:
        self.selected_index = {
            'row_index': -1, 
            'col_index': -1,
            'count': 0
        }
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        GlobalAccessor.sql_result_viewer_refresh = self.refresh_data
        yield DataTable()

    async def refresh_data(self, data: list) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns(*data[0])
        table.add_rows(data[1:])

    @work
    @on(DataTable.CellSelected)
    async def participant_selected(self, event: DataTable.CellSelected) -> None:
        selected_index = {
            'row_index': event.data_table.get_row_index(event.cell_key.row_key),
            'col_index': event.data_table.get_column_index(event.cell_key.column_key)
        }
        if (
            selected_index['row_index'] == self.selected_index['row_index'] and 
            selected_index['col_index'] == self.selected_index['col_index']
        ):
            self.selected_index['count'] += 1
        else:
            self.selected_index['row_index'] = selected_index['row_index'] 
            self.selected_index['col_index'] = selected_index['col_index']
            self.selected_index['count'] = 0

        if self.selected_index['count'] > 0:
            selected_cell = event.data_table.get_cell(event.cell_key.row_key, event.cell_key.column_key)
            await self.app.push_screen_wait(SelectedCellDisplay(selected_cell))


class SelectedCellDisplay(ModalScreen):
    CSS = """
        SelectedCellDisplay {
            align: center middle;
        }
        Container {
            align: center middle;
            width: 60%;
            height: 50%;
            border: round $foreground;
            padding: 0 1;
        }
    """
    def __init__(self, selected_cell) -> None:
        self.selected_cell = selected_cell
        super().__init__()
        
    def compose(self) -> ComposeResult:
        yield Container(
            TextArea(
                text=self.selected_cell,
                read_only=True,
                id="ta_selected_cell"
            ),
            Button("Close", id="btn_close_dcell")
        )

    @on(Button.Pressed, "#btn_close_dcell")
    async def button_pressed_cancel(self, event: Button.Pressed) -> None:
        self.dismiss()