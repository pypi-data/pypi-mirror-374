from abc import ABC, abstractmethod
from telegram import Bot, Message as PTBMessage
import telegram

from ..button_rows import ButtonRows
from ...callback_data import CallbackDataMapping
from ...message import Message as BaseMessage
from ...message import SentMessage as BaseSentMessage

class HasButtonRows(ABC):
    def __init__(self):
        self.button_rows: ButtonRows = None
    def get_reply_markup(self, mapping: CallbackDataMapping):
        if self.button_rows:
            return self.button_rows.to_reply_markup(mapping)
        return None


class Message(BaseMessage, ABC):
    @abstractmethod
    def transform(self, old: "SentMessage") -> "SentMessage":
        ...
    

class SentMessage(BaseSentMessage):
    def __init__(self):
        self.ptb_message: PTBMessage = None
    
    async def delete(self, bot: Bot):
        try:
            await bot.delete_message(
                chat_id=self.ptb_message.chat_id,
                message_id=self.ptb_message.message_id)
        except telegram.error.BadRequest as e:
            print(f"{self} не получилось удалить: {e!r}")
    
    @abstractmethod
    async def edit(self, bot: Bot, mapping: CallbackDataMapping): ...