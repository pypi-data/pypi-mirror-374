from typing import Any
from ..session import InputSession as BaseInputSession
from telegram import Message as TgMessage


class InputSession(BaseInputSession):
    def __init__(self, id: str, delete_if_level_decreased=True, delete_if_last_dir_changed=False, 
            add_new_messages=True, may_pop_last_input=True):
        super().__init__(id, delete_if_level_decreased, delete_if_last_dir_changed, 
            add_new_messages, may_pop_last_input)
        
        self.messages: list[TgMessage] = []
    
    def append(self, message: TgMessage):
        self.messages.append(message)
        
    def __repr__(self):
        texts = []
        for message in self.messages:
            texts.append(message.text)
        return f"{type(self).__name__}(id={self.id!r}, texts={texts!r})"