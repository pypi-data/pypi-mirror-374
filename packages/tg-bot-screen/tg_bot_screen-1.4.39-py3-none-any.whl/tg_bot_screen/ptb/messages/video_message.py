import pathlib
from typing import Self
from telegram import Bot, InputFile, InputMediaVideo, Message as PTBMessage
import telegram
from ..button_rows import ButtonRows

from ...callback_data import CallbackDataMapping
from telegram import Message as PTBMessage

from .message import HasButtonRows, Message, SentMessage
from ...message import VideoMessage         as BaseVideoMessage
from ...message import SentVideoMessage     as BaseSentVideoMessage

class VideoMessage(BaseVideoMessage, HasButtonRows, Message):
    def __init__(self, 
            video: bytes | InputFile | pathlib.Path | telegram.Video, 
            caption: str = None, 
            button_rows: ButtonRows = None, *,
            parse_mode: str = None):
        super().__init__(caption, button_rows, parse_mode)
        self.video = video
        
    async def send(self, user_id: int, bot: Bot, mapping: CallbackDataMapping):
        ptb_message = await bot.send_video(user_id, self.video, 
            caption = self.caption, 
            reply_markup=self.get_reply_markup(mapping),
            parse_mode=self.parse_mode)
        return SentVideoMessage(self.video, ptb_message, 
            caption = self.caption, 
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode)
    
    def __eq__(self, other: Self):
        return self.caption == other.caption and \
            self.video == other.video and \
            self.button_rows == other.button_rows and \
            self.parse_mode == other.parse_mode
    
    def __repr__(self):
        return f"{type(self).__name__}({self.caption=!r}, {self.button_rows=!r}, {self.parse_mode=!r})"
    
    def clone(self) -> Self: 
        return self.__class__(self.video, 
            caption = self.caption, 
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode)
    
    def transform(self, old: "SentMessage"):
        return SentVideoMessage(self.video, old.ptb_message, 
            caption = self.caption, 
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode)

class SentVideoMessage(BaseSentVideoMessage, HasButtonRows, SentMessage):
    def __init__(self, video: bytes | InputFile | pathlib.Path | telegram.Video,
            ptb_message: PTBMessage,
            caption: str = None, 
            button_rows: ButtonRows = None, *,
            parse_mode: str = None,
        ):
        super().__init__(caption, button_rows, parse_mode)
        self.video = video
        self.ptb_message = ptb_message
        self.__ptb_message_video = video
    
    async def edit(self, bot: Bot, mapping: CallbackDataMapping):
        orig = self.ptb_message
        reply_markup = self.get_reply_markup(mapping)
        if orig.caption_html == self.caption and orig.reply_markup == reply_markup \
                and self.__ptb_message_video == self.video:
            return
        self.ptb_message = await bot.edit_message_media(
            media=InputMediaVideo(self.video, self.caption, 
                parse_mode=self.parse_mode),
            chat_id=self.ptb_message.chat_id,
            message_id=self.ptb_message.message_id,
            reply_markup = reply_markup)
        self.__ptb_message_video = self.video
    
    def __eq__(self, other: Self):
        return self.caption == other.caption and \
            self.video == other.video and \
            self.button_rows == other.button_rows and \
            self.parse_mode == other.parse_mode
    
    def __repr__(self):
        return f"{type(self).__name__}({self.caption=!r}, {self.button_rows=!r}, {self.parse_mode=!r})"
    
    def clone(self):
        return self.__class__(self.video, self.ptb_message, 
            caption = self.caption, 
            button_rows = self.button_rows,
            parse_mode = self.parse_mode)

    def get_unsent(self):
        return VideoMessage(
            self.video, 
            caption = self.caption, 
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode)