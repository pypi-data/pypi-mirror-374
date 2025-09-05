import pathlib
from typing import Self
from telegram import Bot, InputFile
import telegram
from telegram import Message as PTBMessage

from ..button_rows import ButtonRows

from ...callback_data import CallbackDataMapping
from ...message import AudioMessage     as BaseAudioMessage
from ...message import SentAudioMessage     as BaseSentAudioMessage
from .message import HasButtonRows, Message, SentMessage


# TODO: Доработать классы, сейчас они вообще не готовы

class AudioMessage(BaseAudioMessage, HasButtonRows, Message):
    def __init__(self, 
            audio: InputFile | bytes | pathlib.Path | telegram.Audio, 
            caption: str, button_rows: ButtonRows = None, parse_mode: str = None):
        super().__init__(caption, button_rows, parse_mode)
        self.audio = audio
    
    async def send(self, user_id: int, bot: Bot, mapping: CallbackDataMapping):
        ptb_message = await bot.send_audio(user_id, self.audio
            , caption = self.caption
            , reply_markup=self.get_reply_markup(mapping)\
            , parse_mode = self.parse_mode)
        return SentAudioMessage( # TODO: fix
            self.text, self.button_rows, ptb_message)
    
    def __eq__(self, other: Self):
        return self.caption == other.caption and \
            self.audio == other.audio and \
            self.button_rows == other.button_rows
    
    def clone(self):
        button_rows = None
        if self.button_rows:
            button_rows = self.button_rows.clone()
        return AudioMessage(self.audio, self.caption, button_rows, 
            self.parse_mode)

class SentAudioMessage(BaseSentAudioMessage, HasButtonRows, SentMessage):
    def __init__(self, 
            audio: str, 
            button_rows: ButtonRows
        , ptb_message: PTBMessage):
        super().__init__(button_rows)
        self.ptb_message = ptb_message 
    
    async def edit(self, bot: Bot, mapping: CallbackDataMapping):
        orig = self.ptb_message
        reply_markup = self.get_reply_markup(mapping)
        if orig.text == self.text and orig.reply_markup == reply_markup:
            return
        self.ptb_message = await bot.edit_message_text(
            text = self.text,
            reply_markup = reply_markup,
            chat_id=self.ptb_message.chat_id,
            message_id=self.ptb_message.message_id)
    
    async def delete(self, bot: Bot):
        await bot.delete_message(
            chat_id=self.ptb_message.chat_id,
            message_id=self.ptb_message.message_id)
    
    def __eq__(self, other: Self):
        return self.text == other.text and \
            self.button_rows == other.button_rows
    
    def clone(self):
        return SentAudioMessage(self.text, self.button_rows, self.ptb_message)

    def get_unsent(self):
        return AudioMessage(
              self.text
            , self.button_rows)