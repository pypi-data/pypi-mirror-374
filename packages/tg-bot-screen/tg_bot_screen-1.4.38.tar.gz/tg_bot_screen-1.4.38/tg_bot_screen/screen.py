from inspect import iscoroutinefunction
from abc import ABC, abstractmethod
from typing import Callable, Iterable, Self

from .error_info import check_bad_value
from .callback_data import CallbackData
from .message import Message, SentMessage

class HasCallbackData(ABC):
    @abstractmethod
    def __init__(self): ...
    
    def get_callback_data(self):
        result: list[CallbackData] = []
        for message in self.messages:
            result.extend(message.get_callback_data())
        return result

class ReadyScreen(HasCallbackData):
    def __init__(self, *messages: Message):
        self.messages: list[Message] = []
        self.extend(messages)
    
    def extend(self, messages: list[Message]):
        for message in messages:
            self.append(message)
        
    def append(self, message: Message):
        check_bad_value(message, Message, self, "message")
        self.messages.append(message)
    
    def __repr__(self):
        return f"{type(self).__name__}({self.messages!r})"
    
    def clone(self) -> "ReadyScreen":
        return ReadyScreen(*[message.clone() for message in self.messages])

class SentScreen(HasCallbackData):
    def __init__(self, *messages: SentMessage):
        self.messages: list[SentMessage] = []
        self.extend(messages)
    
    def extend(self, messages: list[SentMessage]):
        for message in messages:
            self.append(message)
        
    def append(self, message: SentMessage):
        check_bad_value(message, SentMessage, self, "message")
        self.messages.append(message)
        
    def clone(self) -> Self:
        return SentScreen(*[message.clone() for message in self.messages])
    
    def __repr__(self):
        return f"{type(self).__name__}({self.messages!r})"
    
    @abstractmethod
    async def delete(self): ...
    
    @abstractmethod
    def get_unsent(self) -> ReadyScreen: ...

class ProtoScreen(ABC):
    def __init__(self, name: str = None):
        self.name = name
        self.messages: list[Message] = []
    
    def append(self, message: Message):
        check_bad_value(message, Message, self, "message")
        self.messages.append(message)
    
    def extend(self, messages: list[Message]):
        for message in messages:
            self.append(message)
    
    @abstractmethod
    async def evaluate(self, user_id: int, **kwargs) -> ReadyScreen: ...

class StaticScreen(ProtoScreen):
    def __init__(self, name: str, *messages: Message):
        super().__init__(name = name)
        self.extend(messages)
    
    async def evaluate(self, _):
        messages = []
        for message in self.messages:
            new_message = message.clone()
            messages.append(new_message)
        return ReadyScreen(*messages)
    
    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, {self.messages!r})"

class DynamicScreen(ProtoScreen):
    def __init__(self, name: str, 
            function: Callable[[int], Iterable[Message]]):
        super().__init__(name)
        if not iscoroutinefunction(function):
            print(f"Экран {name} был создан с не async функцией")
        self.function = function
    
    async def evaluate(self, user_id: int, **kwargs):
        messages = await self.function(user_id=user_id, **kwargs)
        return ReadyScreen(*messages)

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, {self.function!r})"

