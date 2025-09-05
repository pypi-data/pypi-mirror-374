from pathlib import Path
from .common import ProjectGenerator

def create_init(proj_gen: ProjectGenerator, cwd: Path): 
    proj_gen.mkpackage(cwd)
    proj_gen.mkmodule(cwd / "app.py", """\
from os import environ
from telegram.ext import Application
from src.model.bot_manager import BotManager

token = environ.get("BOT_TOKEN")

application = Application.builder().token(token).build()

bot = application.bot

botm = BotManager(application).build()""")
    
    
    proj_gen.mkmodule(cwd / "main.py", """\
from telegram.ext import CommandHandler
from .app import botm, application
from .screens import load_screens
from .start import start, start_inner

load_screens()

botm.start_inner = start_inner

# application.job_queue.run_repeating(action, interval=60, first=1)

application.add_handler(CommandHandler("start", start), 0)
botm.add_handlers()

print("Запрашивание...")
application.run_polling(0.1)""")

    proj_gen.mkmodule(cwd / "screens.py", R"""\
import importlib
from pathlib import Path

def load_screens():
    p = Path("src/screen")
    for path in p.rglob("*.py"):
        if path.name.startswith("_"):
            continue
        fullpath = str(path)
        module_name = fullpath[:-3].replace("/", ".").replace("\\", ".")
        importlib.import_module(module_name)""")
    
    proj_gen.mkmodule(cwd / "start.py", """\
from telegram import Update, User
from src.init.app import botm

async def start(update: Update, _):
    chat = update.effective_chat
    if chat and chat.type != "private":
        print(f"{chat.id} написал /start не в личном чате")
        return
    
    if update.message:
        user = update.message.from_user
    elif update.callback_query:
        user = update.callback_query.from_user
    else:
        print("Пользователь написал, но не было ни message, ни callback_query")
        return
    assert isinstance(user, User)
    
    user_id = user.id
    await start_inner(user_id)

async def start_inner(user_id: int):  
    if botm.config.development_mode and \
        user_id not in botm.config.admin_list:
        print(f"{user_id} написал /start и не был допущен [development mode]")
        return
    
    print(f"{user_id} написал /start")
    
    sud = botm.system_user_data.get(user_id)
    if sud and sud.screen:
        try: await sud.screen.delete(botm.bot)
        except: ...
    
    botm.system_user_data.reset(user_id)
    botm.reset_user_data(user_id)
    
    await botm.screen.set_by_name(user_id, "welcome")""")