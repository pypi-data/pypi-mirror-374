# Менеджер экранов для Телеграм-ботов

tg_bot_screen - это Python библиотека для упрощения создания телеграм ботов 
на базе python-telegram-bot и других фреймворках.

## Ссылки
### GitHub
https://github.com/Neveix/tg_bot_base  

### PyPI (pip)
https://pypi.org/project/tg-bot-screen/


## Table of Contents
- [Менеджер экранов для Телеграм-ботов](#менеджер-экранов-для-телеграм-ботов)
  - [Ссылки](#ссылки)
    - [GitHub](#github)
    - [PyPI (pip)](#pypi-pip)
  - [Table of Contents](#table-of-contents)
  - [Основные возможности](#основные-возможности)
    - [Экраны](#экраны)
    - [Пользовательский ввод](#пользовательский-ввод)
    - [Строгие типы](#строгие-типы)
    - [Динамичность](#динамичность)
    - [Структура](#структура)
  - [Установка и использование](#установка-и-использование)
    - [Инициализация проекта](#инициализация-проекта)
    - [Минимально рабочий пример](#минимально-рабочий-пример)

## Основные возможности
### Экраны 
Позволяют легко переключаться между заранее известными меню
> Например. В вашем боте есть главное меню, из которого кнопки ведут в 3 других меню.
> Для этого вы можете заранее создать всевозможные меню, и организовать систему переходов между ними.  
> **Не придётся переписывать и дублировать меню несколько раз**

### Пользовательский ввод
Режим пользовательского ввода позволяет принимать от пользователя 
сообщение в нужный момент, и выходить из этого режима, когда будет нужно.
> Это может пригодиться в очень многих ситуациях, когда после нажатия на кнопку или после ввода сообщения нужно принять от пользователя ввод.
> Для этого бот переключается в режим ожидания ввода, и после того, как пользователь ввёл что-то, вызвалась пользовательская callback-функция

### Строгие типы
Снижают количество ошибок, которые могут быть допущены.
> В телеграмме клавиатура представляется как двойной массив кнопок. Когда клавиатуры приходится динамически создавать, добавлять к ним строки,
> кнопки, многократно увеличивается возможность ошибиться. И только после Runtime Error разработчик узнаёт, что допустил ошибку, но даже в этот момент он может не понять, чем она была вызвана.
TBS исключает такую возможность: Клавиатура, строка кнопок, кнопка, меню, 
экран в нём - это отдельные классы, в некоторых из которых прописаны 
выкидывание ошибок из-за несоответствия типов.

### Динамичность
Экраны, меню, текст, клавиатуры в TBS имеют возможность 
быть динамическими, и генерироваться в моменте.
> Это может пригодиться в любых не самых простых ботах, в которых экраны хоть как-то могут меняться. Экран будет создаваться в моменте под определённую ситуацию.
> Так же это можно использовать для ботов, переведённых на несколько языков

### Структура
Архитектура проекта построена вокруг класса BotManager, в котором собраны 
прочие менеджеры


## Установка и использование
**Есть 2 варианта как начать разработку с tg_bot_screen:**
1) Инициализировать проект с помощью встроенного генератора
2) Начать с минимально рабочего примера

Скачайте зависимости: `pip install tg_bot_screen python-telegram-bot`

### Инициализация проекта
1. Создайте директорию с вашим проектом  
2. Инициализируйте проект: `python -m tg_bot_screen --ptb`
3. Добавьте переменную окружения `BOT_TOKEN` с вашим токеном бота из BotFather
4. Запустите бота с помощью `python run.py`


### Минимально рабочий пример

```python
from telegram import Update
from telegram.ext import Application, CommandHandler

from tg_bot_screen.callback_data import GoToScreen, StepBack
from tg_bot_screen.ptb import BotManager
from tg_bot_screen.ptb.button_rows import ButtonRows, ButtonRow, Button
from tg_bot_screen.ptb.messages.simple_message import SimpleMessage


token = "YOUR_TOKEN"

app = Application.builder().token(token).build()

botm = BotManager(app).build()

async def start_callback(update: Update, _):
    user_id = update.message.from_user.id 
    print(f"{user_id} has typed /start")
    await botm.screen.set_by_name(user_id, "welcome")

app.add_handler(CommandHandler("start", start_callback))
botm.add_handlers()

@botm.dynamic_screen()
async def welcome(user_id: int, **kwargs):
    text = "Welcome screen"
    button_rows = ButtonRows(
        ButtonRow(Button("Second screen", GoToScreen("screen2")))
    )
    return [SimpleMessage(text, button_rows)]

@botm.dynamic_screen()
async def screen2(user_id: int, **kwargs):
    text = "Second screen"
    button_rows = ButtonRows(
        ButtonRow(Button("Back", StepBack()))
    )
    return [SimpleMessage(text, button_rows)]


print("Polling...")
app.run_polling(0.1)
```














