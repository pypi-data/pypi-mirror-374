import pathlib
from typing import Self
from telegram import Bot, InputFile, InputMediaDocument, InputMediaVideo, Message as PTBMessage
import telegram
from ..button_rows import ButtonRows
from ...callback_data import CallbackDataMapping
from telegram import Message as PTBMessage

from .message import HasButtonRows, Message, SentMessage
from ...message import DocumentMessage  as BaseDocumentMessage
from ...message import SentDocumentMessage  as BaseSentDocumentMessage

class DocumentMessage(BaseDocumentMessage, HasButtonRows, Message):
    def __init__(self, 
            document: bytes | InputFile | pathlib.Path | telegram.Document, 
            caption: str = None, 
            button_rows: ButtonRows = None, *,
            parse_mode: str = None, 
            filename: str = None):
        super().__init__(caption, button_rows, parse_mode)
        self.document = document
        self.filename = filename
        
    async def send(self, user_id: int, bot: Bot, mapping: CallbackDataMapping):
        ptb_message = await bot.send_document(user_id, self.document, 
            caption = self.caption, 
            reply_markup=self.get_reply_markup(mapping),
            parse_mode=self.parse_mode,
            filename = self.filename)
        return SentDocumentMessage(
            self.document,
            ptb_message, 
            caption = self.caption,
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode, 
            filename = self.filename)
    
    def __eq__(self, other: Self):
        return self.caption == other.caption and \
            self.document == other.document and \
            self.button_rows == other.button_rows and \
            self.parse_mode == other.parse_mode and \
            self.filename == other.filename
    
    def __repr__(self):
        return f"{type(self).__name__}{{{self.filename}}}({self.caption=!r}, {self.button_rows=!r}, {self.parse_mode=!r})"
    
    def clone(self) -> Self: 
        return self.__class__(self.document, 
            caption = self.caption, 
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode, 
            filename = self.filename)
    
    def transform(self, old: "SentMessage"):
        return SentDocumentMessage(
            self.document, old.ptb_message, 
            caption = self.caption,
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode, 
            filename = self.filename)

class SentDocumentMessage(BaseSentDocumentMessage, HasButtonRows, SentMessage):
    def __init__(self, 
            document: bytes | InputFile | pathlib.Path | telegram.Document, 
            ptb_message: PTBMessage, 
            caption: str = None, 
            button_rows: ButtonRows = None, *,
            parse_mode: str = None, 
            filename: str = None
        ):
        super().__init__(caption, button_rows, parse_mode)
        self.document = document
        self.ptb_message = ptb_message
        self.__ptb_message_document = document
        self.filename = filename
    
    async def edit(self, bot: Bot, mapping: CallbackDataMapping):
        orig = self.ptb_message
        reply_markup = self.get_reply_markup(mapping)
        if orig.caption_html == self.caption and orig.reply_markup == reply_markup \
                and self.__ptb_message_document == self.document \
                and self.__ptb_message_document.filename == self.filename:
            return
        self.ptb_message = await bot.edit_message_media(
            media=InputMediaDocument(self.document, self.caption, 
                parse_mode=self.parse_mode, filename=self.filename),
            chat_id=self.ptb_message.chat_id,
            message_id=self.ptb_message.message_id,
            reply_markup = reply_markup)
        self.__ptb_message_document = self.document
    
    def __eq__(self, other: Self):
        return self.caption == other.caption and \
            self.document == other.document and \
            self.button_rows == other.button_rows and \
            self.parse_mode == other.parse_mode and \
            self.filename == other.filename
    
    def __repr__(self):
        return f"{type(self).__name__}{{{self.filename}}}({self.caption=!r}, \
{self.button_rows=!r}, {self.parse_mode=!r})"
    
    def clone(self):
        return self.__class__(self.document, self.ptb_message, 
            caption = self.caption, 
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode, 
            filename = self.filename)

    def get_unsent(self):
        return DocumentMessage(
            self.document, 
            caption = self.caption, 
            button_rows = self.button_rows, 
            parse_mode = self.parse_mode, 
            filename=self.filename)