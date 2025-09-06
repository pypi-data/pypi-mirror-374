from typing import Self
from telegram import Bot
from telegram import Message as PTBMessage

from ..button_rows import ButtonRows
from ...message import SimpleMessage    as BaseSimpleMessage
from ...message import SentSimpleMessage    as BaseSentSimpleMessage
from ...callback_data import CallbackDataMapping
from .message import HasButtonRows, Message, SentMessage

class SimpleMessage(BaseSimpleMessage, HasButtonRows, Message):
    async def send(self, user_id: int, bot: Bot, mapping: CallbackDataMapping):
        ptb_message = await bot.send_message(user_id, self.text
            , reply_markup=self.get_reply_markup(mapping)
            , parse_mode=self.parse_mode)
        return SentSimpleMessage(
            self.text, self.button_rows, ptb_message, self.parse_mode)
    
    def __eq__(self, other: Self):
        return self.text == other.text and \
            self.button_rows == other.button_rows and \
            self.parse_mode == other.parse_mode
    
    def __repr__(self):
        return f"{type(self).__name__}({self.text!r}, {self.button_rows!r}, {self.parse_mode!r})"
    
    def clone(self):
        button_rows = None
        if self.button_rows:
            button_rows = self.button_rows.clone()
        return SimpleMessage(self.text, button_rows, self.parse_mode)

    def transform(self, old: "SentMessage"):
        return SentSimpleMessage(self.text, self.button_rows,
            old.ptb_message, self.parse_mode)
    
class SentSimpleMessage(BaseSentSimpleMessage, HasButtonRows, SentMessage):
    def __init__(self, text: str, button_rows: ButtonRows
        , ptb_message: PTBMessage, parse_mode: str = None):
        super().__init__(text, button_rows, parse_mode)
        self.ptb_message = ptb_message 
    
    async def edit(self, bot: Bot, mapping: CallbackDataMapping):
        orig = self.ptb_message
        reply_markup = self.get_reply_markup(mapping)
        if orig.text_html == self.text and orig.reply_markup == reply_markup:
            return
        self.ptb_message = await bot.edit_message_text(
            text = self.text,
            reply_markup = reply_markup,
            parse_mode = self.parse_mode,
            chat_id=self.ptb_message.chat_id,
            message_id=self.ptb_message.message_id)
    
    def __eq__(self, other: Self):
        return self.text == other.text and \
            self.button_rows == other.button_rows and \
            self.parse_mode == other.parse_mode
            
    def __repr__(self):
        return f"{type(self).__name__}({self.text!r}, {self.button_rows!r})"
    
    def clone(self):
        return SentSimpleMessage(self.text, self.button_rows, self.ptb_message, 
            self.parse_mode)

    def get_unsent(self):
        return SimpleMessage(
              self.text
            , self.button_rows
            , self.parse_mode)