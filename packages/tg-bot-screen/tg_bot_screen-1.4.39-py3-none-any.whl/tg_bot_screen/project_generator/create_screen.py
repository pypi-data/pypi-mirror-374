from .common import *

def create_screen(proj_gen: ProjectGenerator, cwd: Path): 
    proj_gen.mkpackage(cwd)
    proj_gen.mkmodule(cwd / "welcome.py", """\
from .common import *

@botm.dynamic_screen()
async def welcome(user_id: int, **kwargs):
    return [SimpleMessage("Меню", 
        ButtonRows(
             ButtonRow(Button("Пусто", Dummy()))
        ))]
""")
    proj_gen.mkmodule(cwd / "common.py", """\
from typing import Callable
from telegram import Message as TgMessage
from tg_bot_screen.ptb import SimpleMessage, PhotoMessage, ButtonRows, \\
    ButtonRow, Button, GoToScreen, RunFunc, StepBack, ScreenCallback, \\
    FuncCallback, InputSession, FuncCallback, Message, DocumentMessage, \\
    VideoMessage, InputCallback 
from tg_bot_screen.callback_data import Dummy
from tg_bot_screen.ptb.user_data import UserData as SysUserData
from src.init.app import botm

def step_back_button_row(text: str = "↖️ Вернуться назад", 
        times: int = 1):
    return ButtonRow(Button(text, StepBack(times)))

def mdbq(text: str):
    "Добавить blockquote к тексту"
    return f"<blockquote>{text}</blockquote>"

def mdb(text: str):
    "Добавить bold к тексту"
    return f"<b>{text}</b>"

def mdi(text: str):
    "Добавить italic к тексту"
    return f"<i>{text}</i>"

async def is_bad_text(user_id: int, message: TgMessage = None, stack = True):
    if message.text is None:
        await botm.screen.set_by_name(user_id, "bad_text", stack=stack)
        return True
    return False

@botm.dynamic_screen()
async def screen_bad_text(user_id: int, message: TgMessage = None, **kwargs):
    return [SimpleMessage("😔 Неподходящий текст или он отсутствует",
            ButtonRows(step_back_button_row()))]

async def is_bad_image(user_id: int, message: TgMessage = None, stack = True):
    if message.photo == ():
        await botm.screen.set_by_name(user_id, "bad_image", stack=stack)
        return True
    return False

@botm.dynamic_screen()
async def screen_bad_image(user_id: int, message: TgMessage = None, **kwargs):
    return [SimpleMessage("😔 Неподходящая картинка или она отсутствует",
            ButtonRows(step_back_button_row()))]

def simple_screen(text: str, has_step_back = True, parse_mode: str = None,
        step_back_times: int = 1):
    button_rows = ButtonRows()
    if has_step_back:
        button_rows.append(step_back_button_row(times=step_back_times))
    return [SimpleMessage(text, button_rows, parse_mode)]

def select_screen(text: str, yes_func: Callable, parse_mode: str = None):
    return [SimpleMessage(text, 
        ButtonRows(
             ButtonRow(Button("Да", RunFunc(yes_func)))
            ,step_back_button_row())
        , parse_mode)]

def simple_multi_screen(text: str, has_step_back = True, parse_mode: str = None,
        step_back_times: int = 1):
    button_rows = ButtonRows()
    if has_step_back:
        button_rows.append(step_back_button_row(times=step_back_times))
    texts: list[str] = []
    cap = 4096
    while text != "":
        texts.append(text[:cap])
        text = text[cap:]
    msgs = [SimpleMessage(text, parse_mode=parse_mode) for text in texts]
    msgs[-1].button_rows = button_rows
    return msgs

@botm.dynamic_screen()
async def screen_error_screen(user_id: int, **kwargs):
    user_data = botm.get_user_data(user_id)
    return [SimpleMessage(f"😔 Ошибка: {user_data.last_error}",
            ButtonRows(step_back_button_row()))]""")