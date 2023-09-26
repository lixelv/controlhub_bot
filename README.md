bot.py:
```python
import aiofiles
import asyncio
import json
from aiogram import types
from bot_cnf import *


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    print(message.from_user.id)
    await message.answer(start_)


@dp.message_handler(commands=['h', 'help'])
async def bot_help(message: types.Message):
    await message.answer(help_)


@dp.message_handler(lambda message: str(message.from_user.id) not in admin_list)
async def not_admin(message: types.Message):
    await message.answer(f"Вы не админ, вот ваш id: `{message.from_user.id}`")


@dp.message_handler(commands=['p', 'prog', 'program'])
async def program(message: types.Message):
    args = message.get_args()
    args = args.replace('\\', '/')

    if args:
        async with aiofiles.open('main.json', 'r', encoding='utf-8') as file:
            data = json.loads(await file.read())

        if args.count(', ') != 0:
            args = args.split(', ')
        else:
            args = [args]

        data["args"] = args

        async with aiofiles.open('main.json', 'w', encoding='utf-8') as file:
            await file.write(json.dumps(data))

        await message.answer(f"Было записано: \n`{args}`")

    else:
        await message.answer('Введите аргументы для функции типа: \n`/program C:/Program Files/Google/Chrome/Application/chrome.exe, --new-window, https://www.google.com`')


@dp.message_handler(commands=['a', 'act', 'activate'])
async def activate(message: types.Message):
    msg = await message.answer('Запрос принят\!')

    async with aiofiles.open('main.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())

    data["run"] = True

    async with aiofiles.open('main.json', 'w', encoding='utf-8') as file:
        await file.write(json.dumps(data))

    await asyncio.sleep(timing() + 1)

    async with aiofiles.open('main.json', 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())

    data["run"] = False

    async with aiofiles.open('main.json', 'w', encoding='utf-8') as file:
        await file.write(json.dumps(data))

    await msg.delete()

    await message.answer('Запрос обработан\!')


if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True)

```
bot_cnf.py:
```python
import aiogram
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

```
cnf.py:
```python
from envparse import env
import requests

env.read_envfile('.env')

link = env('LINK')

def timing():
    return requests.get(link).json()['sleep']


```
main.py:
```python
import aiofiles
import json
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    async with aiofiles.open('main.json', mode='r', encoding='utf-8') as file:
        content = await file.read()
        return json.loads(content)

```
run.py:
```python
import subprocess
from time import sleep
from cnf import *

prev_value = requests.get(link).json()

while True:

    value = requests.get(link).json()

    print(value)

    if value != prev_value and value["run"]:
        try:
            subprocess.run(value["args"])
        except Exception as e:
            print(f"Error {e}")

    prev_value = value

    sleep(value["sleep"])


```
