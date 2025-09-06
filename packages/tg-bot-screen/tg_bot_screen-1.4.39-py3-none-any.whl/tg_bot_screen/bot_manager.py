from abc import abstractmethod, ABC
from typing import Callable
from .screen import DynamicScreen
from .input_callback import FuncCallback, InputCallback, ScreenCallback
from .callback_data import GoToScreen, RunFunc, StepBack, CallbackData
from .user_data import UserDataManager
from .user_screen import UserScreen

class BotManager(ABC):
    def __init__(self):
        self.system_user_data: UserDataManager = None
        self.screen: UserScreen = None
        
    def config_delete_old_messages(self, user_id: int):
        input_callback = self.get_system_user_data(user_id).input_callback
        if input_callback is not None:
            return False
        return True
    
    def build(self):
        user_datam = UserDataManager()
        screen = UserScreen(user_datam)
        self.system_user_data = user_datam
        self.screen = screen
        return self
    
    @abstractmethod
    def add_handlers(self): ...
    
    def get_system_user_data(self, user_id: int):
        return self.system_user_data.get(user_id)

    @abstractmethod
    def get_message_handler(self): ...

    async def _handle_message(self, user_id: int, **kwargs):
        user_data = self.get_system_user_data(user_id)
        delete_old: bool = self.config_delete_old_messages(user_id)
        if delete_old:
            await self.delete_message(**kwargs)
        
        input_callback: InputCallback = user_data.input_callback
        if input_callback is None:
            return
        
        await self.screen.clear(user_id, delete_old)
        
        for session in user_data.input_sessions:
            if not session.add_new_messages:
                continue
            message = kwargs["message"]
            session.append(message)
        
        if isinstance(input_callback, FuncCallback):
            if input_callback.one_time:
                user_data.input_callback = None
            await input_callback.function(user_id=user_id
                , **input_callback.kwargs, **kwargs)
        elif isinstance(input_callback, ScreenCallback):
            user_data.input_callback = None
            await self.screen.set_by_name(user_id, input_callback.screen_name,
                input_callback.stack, **kwargs)
            

    @abstractmethod
    def get_callback_query_handler(self): ...
    
    @abstractmethod
    async def delete_message(self, message): ...
    
    async def mapping_key_error(self, user_id: int): ...
    
    async def _handle_callback_query(self, user_id: int, query_data: str, **kwargs):
        sud = self.get_system_user_data(user_id)
        mapping = sud.callback_mapping
        data: CallbackData | None = mapping.get_by_uuid(query_data)
        if data is None:
            await self.mapping_key_error(user_id)
            return
        
        await data.use(user_id=user_id,
                  input_sessions=sud.input_sessions,
                  screen_set_by_name=self.screen.set_by_name,
                  screen_step_back=self.screen.step_back,
                  reset_input_callback=sud.reset_input_callback,
                  update_sessions=sud.update_sessions,
                  **kwargs)
    
    def dynamic_screen(self, name: str | None = None):
        def decorator(func: Callable):
            nonlocal name
            if name is None:
                name = func.__name__
            self.screen.append_screen(DynamicScreen(name, func))
        return decorator


    
    
