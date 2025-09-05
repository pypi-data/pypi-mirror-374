import pathlib
from typing import Self
from telegram import Bot, InputFile, InputMediaPhoto, Message as PTBMessage
import telegram
from ..button_rows import ButtonRows

from ...callback_data import CallbackDataMapping
from ...message import PhotoMessage     as BasePhotoMessage
from ...message import SentPhotoMessage     as BaseSentPhotoMessage
from .message import HasButtonRows, Message, SentMessage

class PhotoMessage(BasePhotoMessage, HasButtonRows, Message):
    def __init__(self,
            photo: bytes | InputFile | pathlib.Path | telegram.PhotoSize, 
            caption: str = None, 
            button_rows: ButtonRows = None, *,
            parse_mode: str = None):
        super().__init__(caption, button_rows, parse_mode)
        self.photo = photo
        
    async def send(self, user_id: int, bot: Bot, mapping: CallbackDataMapping):
        ptb_message = await bot.send_photo(user_id, self.photo
            , self.caption, reply_markup=self.get_reply_markup(mapping)
            , parse_mode=self.parse_mode)
        return SentPhotoMessage(self.photo, 
            ptb_message = ptb_message, 
            caption = self.caption,
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode)
    
    def __eq__(self, other: Self):
        return self.caption == other.caption and \
            self.photo == other.photo and \
            self.button_rows == other.button_rows and \
            self.parse_mode == other.parse_mode
    
    def __repr__(self):
        return f"{type(self).__name__}({self.caption=!r}, {self.button_rows=!r}, {self.parse_mode=!r})"
    
    def clone(self) -> Self: 
        return self.__class__(self.photo, self.caption, self.button_rows, 
            self.parse_mode)
    
    def transform(self, old: "SentMessage"):
        return SentPhotoMessage(
            self.photo, 
            ptb_message = old.ptb_message, 
            caption = self.caption,
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode)


class SentPhotoMessage(BaseSentPhotoMessage, HasButtonRows, SentMessage):
    def __init__(self, 
            photo: bytes | InputFile | pathlib.Path | telegram.PhotoSize, 
            ptb_message: PTBMessage, 
            caption: str = None, 
            button_rows: ButtonRows = None, *, 
            parse_mode: str = None,
        ):
        super().__init__(caption, button_rows, parse_mode)
        self.photo = photo
        self.ptb_message = ptb_message
        self.__ptb_message_photo = photo
    
    async def edit(self, bot: Bot, mapping: CallbackDataMapping):
        orig = self.ptb_message
        reply_markup = self.get_reply_markup(mapping)
        if orig.caption_html == self.caption and orig.reply_markup == reply_markup \
                and self.__ptb_message_photo == self.photo:
            return
        self.ptb_message = await bot.edit_message_media(
            media=InputMediaPhoto(self.photo, self.caption, self.parse_mode),
            chat_id=self.ptb_message.chat_id,
            message_id=self.ptb_message.message_id,
            reply_markup = reply_markup)
        self.__ptb_message_photo = self.photo
    
    def __eq__(self, other: Self):
        return self.caption == other.caption and \
            self.photo == other.photo and \
            self.button_rows == other.button_rows and \
            self.parse_mode == other.parse_mode
    
    def __repr__(self):
        return f"{type(self).__name__}({self.caption=!r}, {self.button_rows=!r}, {self.parse_mode=!r})"
    
    def clone(self):
        return self.__class__(self.photo, self.ptb_message, 
            caption = self.caption, 
            button_rows = self.button_rows,
            parse_mode = self.parse_mode)

    def get_unsent(self):
        return PhotoMessage(
            self.photo, 
            caption = self.caption, 
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode)