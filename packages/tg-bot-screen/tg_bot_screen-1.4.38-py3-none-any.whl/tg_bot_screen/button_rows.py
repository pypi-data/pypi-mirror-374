from abc import abstractmethod
from typing import Self
from .callback_data import CallbackData
from .error_info import check_bad_text_and_len, check_bad_value

class Button:
    def __init__(self, text: str, callback_data: CallbackData, 
                 url: str | None = None, web_app = None):
        check_bad_text_and_len(text, self, "text")
        check_bad_value(callback_data, CallbackData, self, "callback_data")
        if url:
            check_bad_text_and_len(url, self, "url")

        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.web_app = web_app
    
    def clone(self) -> Self:
        return Button(self.text, self.callback_data.clone(), self.url, self.web_app)

    def __repr__(self):
        return f"{type(self).__name__}({self.text!r}, {self.callback_data!r}, url={self.url!r})"

    def __eq__(self, other: object):
        if not isinstance(other, Button):
            return False
        
        return (self.text == other.text and \
                self.callback_data == other.callback_data and \
                self.url == other.url and \
                self.web_app == other.web_app)

class ButtonRow:
    def __init__(self, *buttons: Button):
        self.buttons: list[Button] = []
        self.extend(buttons)
    
    def extend(self, buttons: list[Button]):
        for button in buttons:
            self.append(button)
        return self

    def append(self, button: Button):
        check_bad_value(button, Button, self, "button")
        self.buttons.append(button)
        return self
    
    def clone(self) -> Self:
        return ButtonRow().\
            extend([button.clone() for button in self.buttons])
    
    def __repr__(self):
        return f"{type(self).__name__}(*{self.buttons!r})"
    
    def __eq__(self, other: Self):
        return all([
            button1 == button2 
            for button1, button2
            in zip(self.buttons, other.buttons)])

class ButtonRows:
    def __init__(self, *rows: ButtonRow):
        self.rows: list[ButtonRow] = []
        self.extend(rows)
    
    def extend(self, rows: list[ButtonRow]):
        for row in rows:
            self.append(row)
    
    def append(self, row: ButtonRow):
        check_bad_value(row, ButtonRow, self, "row")
        self.rows.append(row)
    
    def clone(self) -> Self:
        return ButtonRows(*[row.clone() for row in self.rows])
    
    def __eq__(self, other: Self):
        return all([row1 == row2
            for row1, row2 in zip(self.rows,other.rows)])
        
    def __repr__(self):
        return f"{type(self).__name__}(*{self.rows!r})"
    
    @abstractmethod
    def to_reply_markup(self): ...
    
    def get_callback_data(self):
        result: list[CallbackData] = []
        for row in self.rows:
            for button in row.buttons:
                result.append(button.callback_data)
        return result