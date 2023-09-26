import aiogram
import requests
import aiofiles
import asyncio
import json
from aiogram import types
from envparse import env

start_ = 'Привет, я бот созданный чтобы управлять \nкомпьютерами в *40 кабинете школы №358*\. \n\nЧтобы ознакомится с моим функционалом введите */help*'

help_ = """Этот бот создан для управления компьютерами в *40 кабинете 358 школы\.*

Для записи в бота команды используйте */program \(args\)*
Очень важно, что если у вашей команды есть аргументы типа ссылки при запуске браузера, то перечисляйте их через запятую с пробелом `(, )`

Для запуска программы на компьютерах введите */a*"""

env.read_envfile('.env')

def timing():
    return requests.get(link).json()['sleep']

link = env('LINK')

token = env('TELEGRAM')
admin_list = env('ADMIN_LIST').split(',')
bot = aiogram.Bot(token, parse_mode='MarkdownV2')
dp = aiogram.Dispatcher(bot)
