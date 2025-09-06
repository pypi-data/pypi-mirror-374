from typing import Callable, Self, Sequence
from abc import ABC, abstractmethod

from .session import InputSession

from .input_callback import FuncCallback
from .error_info import check_bad_text_and_len, check_bad_value, check_pre_post_func

class CallbackData(ABC):
    @abstractmethod
    def clone(self) -> Self: ...
    
    @abstractmethod
    def __repr__(self) -> str: ...
    
    @abstractmethod
    async def use(self, *, user_id: int,
                  input_sessions: Sequence[InputSession],
                  screen_set_by_name: Callable, 
                  screen_step_back: Callable, 
                  reset_input_callback: Callable,
                  update_sessions: Callable,
                  **kwargs):
        ...

class Dummy(CallbackData):
    def clone(self):
        return Dummy()
    
    def __repr__(self):
        return f"{type(self).__name__}()"
    
    async def use(self, *, user_id: int,
                  input_sessions: Sequence[InputSession],
                  screen_set_by_name: Callable, 
                  screen_step_back: Callable, 
                  reset_input_callback: Callable,
                  update_sessions: Callable,
                  **kwargs):
        pass

class RunFunc(CallbackData):
    def __init__(self, function: Callable, **kwargs):
        """Использование:  
            function - Функция для выполнения при нажатии кнопки  
            **kwargs - keyword аргументы функции
        """
        check_bad_value(function, Callable, self, "function")
        self.function = function
        self.kwargs = kwargs
    
    def clone(self):
        return RunFunc(self.function, **self.kwargs)
    
    def __repr__(self):
        return f"{type(self).__name__}({self.function!r})"
    
    def __eq__(self, other: object):
        return isinstance(other, RunFunc) and \
            self.function == other.function and self.kwargs == other.kwargs
            
    async def use(self, *, user_id: int,
                  input_sessions: Sequence[InputSession],
                  screen_set_by_name: Callable, 
                  screen_step_back: Callable, 
                  reset_input_callback: Callable,
                  update_sessions: Callable,
                  **kwargs):
        await self.function(user_id=user_id, **self.kwargs, **kwargs)

class GoToScreen(CallbackData):
    def __init__(self, screen_name: str, *
            , pre_func:  FuncCallback | None = None
            , post_func: FuncCallback | None = None):
        check_bad_text_and_len(screen_name, self, "screen_name")
        check_pre_post_func(pre_func, post_func, self)
        
        self.screen_name = screen_name
        self.pre_func = pre_func
        self.post_func = post_func
    
    def clone(self):
        return GoToScreen(self.screen_name)
    
    def __repr__(self):
        return f"{type(self).__name__}({self.screen_name!r}, \
{self.pre_func}, {self.post_func})"
    
    def __eq__(self, other: object):
        return isinstance(other, GoToScreen) and \
            self.screen_name == other.screen_name

    async def use(self, *, user_id: int,
                  input_sessions: Sequence[InputSession],
                  screen_set_by_name: Callable, 
                  screen_step_back: Callable, 
                  reset_input_callback: Callable,
                  update_sessions: Callable,
                  **kwargs):
        if self.pre_func:
            await self.pre_func(user_id=user_id, **kwargs)
        
        await screen_set_by_name(user_id, self.screen_name, 
                                 **kwargs)
        
        if self.post_func:
            await self.post_func(user_id=user_id, **kwargs)
            
        update_sessions()

class StepBack(CallbackData):
    def __init__(self, times: int = 1, clear_input_callback: bool = True
            , pop_last_input: bool = True
            , pre_func: FuncCallback | None = None
            , post_func: FuncCallback | None = None):

        check_bad_value(times, int, self, "times")
        self.times = times

        check_bad_value(clear_input_callback, bool, self, "clear_input_callback")
        self.clear_input_callback = clear_input_callback

        check_bad_value(pop_last_input, bool, self, "pop_last_input")
        self.pop_last_input = pop_last_input

        check_pre_post_func(pre_func, post_func, self)
        
        self.pre_func = pre_func
        self.post_func = post_func

    def clone(self):
        return StepBack()
    
    def __repr__(self):
        return f"{type(self).__name__}({self.times!r}, {self.clear_input_callback}, \
{self.pop_last_input}, {self.pre_func}, {self.post_func})"
    
    def __eq__(self, other: object):
        return isinstance(other, StepBack)
    
    async def use(self, *, user_id: int,
                  input_sessions: Sequence[InputSession],
                  screen_set_by_name: Callable, 
                  screen_step_back: Callable, 
                  reset_input_callback: Callable,
                  update_sessions: Callable,
                  **kwargs):
        if self.clear_input_callback:
            reset_input_callback()
        
        for session in input_sessions:
            if self.pop_last_input and session.may_pop_last_input:
                for i in range(self.times):
                    if session.messages == []:
                        break
                    session.messages.pop()
        
        if self.pre_func:
            await self.pre_func(user_id=user_id, **kwargs)
        
        await screen_step_back(user_id, self.times)
        
        if self.post_func:
            await self.post_func(user_id=user_id, **kwargs)
        
        update_sessions()

class CallbackDataMapping:
    def __init__(self):
        self.items: list[tuple[CallbackData, str]] = []
    
    def add(self, callback: CallbackData, uuid: str):
        self.items.append((callback, uuid))
    
    def get_by_callback(self, callback: CallbackData):
        for i_callback, uuid in self.items:
            if callback is i_callback:
                return uuid
        raise KeyError(callback)
    
    def get_by_uuid(self, uuid: str):
        for callback, i_uuid in self.items:
            if uuid == i_uuid:
                return callback
        return None