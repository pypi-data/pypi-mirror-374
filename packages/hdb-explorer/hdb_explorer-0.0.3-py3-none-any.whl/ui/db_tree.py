import asyncio
from textual import (
    on,
    work
)
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import (
    Tree
)
from common import (
    Config,
    Constants,
    DB_Systems,
    GlobalAccessor
)
from db import (
    DbManager,
    DbPoolManager
)
from .edit_system import EditSystem

class DbTree(Widget):
    def __init__(self, *arg, **kwargs) -> None:
        self.selected_node = None
        GlobalAccessor.db_tree_refresh = self.refresh_tree
        super().__init__(*arg, **kwargs)

    def compose(self) -> ComposeResult:
        tree_root: Tree[str] = Tree(Constants.ROOT_FOLDER_NAME)
        #tree_root.root.expand()
        yield tree_root

    async def on_mount(self) -> None:
        await self.refresh_tree()

    async def refresh_tree(self) -> None:
        tree_root: Tree[str] = self.query_one(Tree)
        tree_root.clear()
        for _ in DB_Systems.file_content:
            tree_root.root.add(f"{_:}", allow_expand=False)

    @on(Tree.NodeExpanded)
    async def node_expanded(self, event: Tree.NodeSelected | Tree.NodeExpanded):
        ...

    @work
    @on(Tree.NodeSelected)
    async def node_selected(self, event: Tree.NodeSelected | Tree.NodeExpanded):
        #event.node.collapse() if event.node.is_expanded else event.node.expand()
        if not event.node.label.plain == Constants.ROOT_FOLDER_NAME:
            if self.selected_node == event.node.label.plain:
                await self.app.push_screen_wait(EditSystem(name=event.node.label.plain))
            
            if event.node.label.plain in DB_Systems.file_content.keys():
                self.selected_node = event.node.label.plain
                GlobalAccessor.spinner_db_tree()
                GlobalAccessor.spinner_sql_editor()
                self.set_timer(Constants.SET_TIMER_TIME, self.process_connection)
            else:
                self.selected_node = ""
                GlobalAccessor.Header.db_sys_text_update(self.selected_node, False)
        
        #self.notify(event.node.label.plain, title="Selection", severity="warning", timeout=Constants.SET_NOTIFY_TIMEOUT)

    @work(thread=True)
    async def process_connection(self) -> None:
        if not self.selected_node in DbPoolManager:
            DbManager.add_connection(self.selected_node)
        else:
            if not DbPoolManager[self.selected_node].connected:
                DbManager.add_connection(self.selected_node)
        
        GlobalAccessor.Header.db_sys_text_update(self.selected_node, DbPoolManager[self.selected_node].connected)
        GlobalAccessor.spinner_db_tree(False)
        GlobalAccessor.spinner_sql_editor(False)


