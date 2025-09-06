from abc import ABC
from typing import Callable

class InputCallback: ...

class FuncCallback(InputCallback):
    def __init__(self, function: Callable
        , one_time: bool = True, **kwargs):
        self.function = function
        self.one_time = one_time
        self.kwargs = kwargs
    
    def __call__(self, **kwds):
        return self.function(**self.kwargs, **kwds)

class ScreenCallback(InputCallback):
    def __init__(self, screen_name: str, stack: bool = False):
        self.screen_name = screen_name
        self.stack = stack