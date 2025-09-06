import asyncio
from . import (
    Config,
    Constants
)
import json
from json.decoder import JSONDecodeError

from textual import work
from textual.timer import Timer

class DBSystems:
    filename: str = Config.AddSystem.FILENAME
    file_content: list = {}
    file_loaded: bool = True

    def __init__(self) -> None:
        try:
            with open(self.filename, "r") as f:
                self.file_content = json.load(f)
        except FileNotFoundError:
            with open(self.filename, "w") as f:
                json.dump(self.file_content, f)
        except JSONDecodeError:
            self.file_loaded = False

    async def reset(self) -> None:
        if not self.file_loaded:
            await self.save()
    
    async def save(self) -> None:
        with open(self.filename, "w") as f:
            json.dump(self.file_content, f)
    
    async def update(self, system: dict, force: bool=False) -> dict | None:
        name = system["name"]

        if force:
            self.file_content[name] = {}
        else:
            if name in self.file_content.keys():
                return self.file_content[name]
            self.file_content[name] = {}
        self.file_content[name]["host"] = system["host"]
        self.file_content[name]["port"] = system["port"]
        self.file_content[name]["user"] = system["user"]
        self.file_content[name]["password"] = system["password"]
        asyncio.create_task(self.save())
        return None
    
    async def delete(self, name: dict) -> dict | None:
        if name in self.file_content.keys():
                del self.file_content[name]

        asyncio.create_task(self.save())
        return None
    
class SQLAutoSave:
    filename: str = Config.SQLAutoSave.FILENAME

    def __init__(self) -> None:
        try:
            with open(self.filename, "r") as f:
                self.file_content = f.read()
        except FileNotFoundError:
            self.file_content = ""

    async def save(self) -> None:
        with open(self.filename, "w") as f:
            f.write(self.file_content)
