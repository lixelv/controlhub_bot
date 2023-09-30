import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from cnf import *

token = env('TELEGRAM')
admin_list = env('ADMIN_LIST').split(',')

start_ = 'Привет, я бот созданный чтобы управлять \nкомпьютерами в *40 кабинете школы №358*\. \n\nЧтобы ознакомится с моим функционалом введите */help*'

help_ = """Этот бот создан для управления компьютерами в *40 кабинете 358 школы\.*

Для записи в бота команды используйте */program \(args\)*
Очень важно, что если у вашей команды есть аргументы типа ссылки при запуске браузера, то перечисляйте их через запятую с пробелом `(, )`

Для запуска программы на компьютерах введите */a*"""

bot = aiogram.Bot(token, parse_mode='MarkdownV2')
dp = aiogram.Dispatcher(bot)

def inline(lst: list | tuple, prefix) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for id_, name_ in lst:
        buttons.append(InlineKeyboardButton(name_, callback_data=f'{prefix}_{id_}'))

    kb.add(*buttons)

    return kb
