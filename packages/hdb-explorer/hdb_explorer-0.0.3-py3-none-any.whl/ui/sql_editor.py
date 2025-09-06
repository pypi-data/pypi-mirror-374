from textual.widgets import (
    TextArea
)
from common import (
    Config,
    Constants,
    DB_Systems,
    SQL_AutoSave,
    GlobalAccessor
)

class SQLEditor(TextArea):
    def __init__(self, *arg, **kwargs) -> None:
        GlobalAccessor.sql_editor_text = self.get_sql_text

        if not 'language' in kwargs:
            kwargs['language'] = 'sql'
        if not 'show_line_numbers' in kwargs:
            kwargs['show_line_numbers'] = True

        super().__init__(text=SQL_AutoSave.file_content, *arg, **kwargs)

    async def get_sql_text(self) -> str:
        t = self.selected_text
        if t.strip() == "":
            t = self.text
        
        return t