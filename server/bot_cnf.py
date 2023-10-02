import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asyncio import get_event_loop
from db import MySQL
from cnf import *

# db_url = f'mysql://{env("USER_")}:{env("PASSWORD_")}@{env("HOST_")}:{env("PORT_")}/{env("DB_")}?allowPublicKeyRetrieval=true'

sql = MySQL()

token = env('TELEGRAM')

start_ = 'Привет, я бот созданный чтобы управлять \nкомпьютерами в *40 кабинете школы №358*\. \n\nЧтобы ознакомится с моим функционалом введите */help*'

help_ = """Этот бот создан для управления компьютерами в *40 кабинете 358 школы\.*

Для записи в бота команды используйте */program \(args\)*
Очень важно, что если у вашей команды есть аргументы типа ссылки при запуске браузера, то перечисляйте их через запятую с пробелом `(, )`

Для запуска программы на компьютерах введите */a*"""

bot = aiogram.Bot(token)
dp = aiogram.Dispatcher(bot)

def inline(lst: list | tuple, prefix) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for id_, name_ in lst:
        buttons.append(InlineKeyboardButton(name_, callback_data=f'{prefix}_{id_}'))

    kb.add(*buttons)

    return kb
