from typing import Any, Callable, Self
from abc import ABC, abstractmethod
from .input_callback import FuncCallback
from .error_info import check_bad_text_and_len, check_bad_value, check_pre_post_func

class CallbackData(ABC):
    @abstractmethod
    def clone(self) -> Self: ...
    
    @abstractmethod
    def __repr__(self) -> str: ...

class Dummy(CallbackData):
    def clone(self):
        return Dummy()
    
    def __repr__(self):
        return f"{type(self).__name__}()"

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

class StepBack(CallbackData):
    def __init__(self, times: int = 1, clear_input_callback: bool = True
            , pop_last_input: bool = True
            , pre_func: FuncCallback = None
            , post_func: FuncCallback = None):

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

class CallbackDataMapping:
    def __init__(self):
        self.items = []
    
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