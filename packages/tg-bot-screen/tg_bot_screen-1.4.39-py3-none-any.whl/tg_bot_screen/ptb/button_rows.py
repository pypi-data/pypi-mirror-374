from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from tg_bot_screen.callback_data import CallbackData

from ..callback_data import CallbackDataMapping
from ..button_rows import ButtonRows as BaseButtonRows
from ..button_rows import Button as BaseButton
from ..button_rows import ButtonRow as BaseButtonRow

class ButtonRows(BaseButtonRows):
    def to_reply_markup(self, mapping: CallbackDataMapping
            ) -> InlineKeyboardMarkup:
        result = []
        for row in self.rows:
            row_list = []
            for button in row.buttons:
                button: Button
                row_list.append(button.to_inline_button(mapping))
            result.append(row_list)
        return InlineKeyboardMarkup(result)
    
    def clone(self) -> "ButtonRows":
        return ButtonRows(*[row.clone() for row in self.rows])

class Button(BaseButton):
    def __init__(self, text: str, callback_data: CallbackData, 
                 url: str | None = None, web_app: WebAppInfo|None=None):
        super().__init__(text, callback_data, url, web_app)
        self.web_app = web_app
        
        
    def to_inline_button(self, mapping: CallbackDataMapping
            ) -> InlineKeyboardButton:
        if self.web_app:
            uuid = None
        else:
            uuid = mapping.get_by_callback(self.callback_data)
        
        return InlineKeyboardButton(self.text
            , callback_data = uuid, url = self.url, web_app=self.web_app)
    
    def clone(self):
        return Button(self.text, self.callback_data.clone(), 
                      self.url, self.web_app)
        

class ButtonRow(BaseButtonRow): ...