from .common import *

def create_model(proj_gen: ProjectGenerator, cwd: Path): 
    proj_gen.mkpackage(cwd)
    proj_gen.mkmodule(cwd / "bot_manager.py", """\
from typing import Callable
from telegram.ext import Application
from tg_bot_screen.ptb import BotManager as BaseBotManager
from .user_data import UserDataManager
from .config_manager import ConfigManager

class BotManager(BaseBotManager):
    def __init__(self, application: Application):
        super().__init__(application)
        self.user_data_m = UserDataManager()
        self.config = ConfigManager()
        self.config.load()
        
        self.start_inner: Callable = None
    
    def get_user_data(self, user_id: int):
        return self.user_data_m.get(user_id)

    def reset_user_data(self, user_id: int):
        self.user_data_m.reset(user_id)
        
    async def mapping_key_error(self, user_id: int):
        await self.start_inner(user_id)""")
    
    proj_gen.mkmodule(cwd / "config_manager.py", """\
from json import dumps, loads
from pathlib import Path
from typing import Any

class ConfigManager:
    def __init__(self, path: str = "config/config.json"):
        self.__path = Path(path)
        self.__json: dict[str, Any]
        self.defaults = {
            "development_mode" : False,
            "admin_list": []
        }
    
    def load(self):
        file_path = self.__path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        defaults = self.defaults
        check_fields = False # Для оптимизации
        if file_path.exists():
            try:
                json = loads(file_path.read_text("utf-8"))
                check_fields = True
            except Exception as e:
                print(f"ConfigManager Error {e!r}")
                json = defaults
        else:
            json = defaults
        
        self.__json = json

        if check_fields:
            for name in defaults:
                if name not in json:
                    json[name] = defaults[name]
            self.dump_to_file()

    def dump_to_file(self):
        self.__path.touch(exist_ok=True)
        self.__path.write_text(
            dumps(self.__json, indent=4, ensure_ascii=False), 
            encoding="utf-8")
    
    @property
    def development_mode(self) -> bool:
        return self.__json["development_mode"]
    
    @property
    def admin_list(self) -> list[int]:
        return self.__json["admin_list"]
        
    """)
    proj_gen.mkmodule(cwd / "user_data.py", """\
class UserData:
    def __init__(self):
        self.last_error: str = None 

class UserDataManager:
    def __init__(self):
        self.users_data: dict[int, UserData] = {}
    
    def get(self, user_id: int):
        if user_id not in self.users_data:
            ud = UserData()
            self.users_data[user_id] = ud
            return ud
        
        return self.users_data[user_id]

    def reset(self, user_id: int):
        self.users_data[user_id] = UserData()""")