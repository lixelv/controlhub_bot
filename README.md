bot.py:
```python
import asyncio
from db import SQLite
from aiogram import types
from bot_cnf import *

sql = SQLite('db.db')

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if await sql.user_exists(message.from_user.id):
        await sql.new_user(message.from_user.id, message.from_user.username)
    await message.answer(start_)


@dp.message_handler(commands=['h', 'help'])
async def bot_help(message: types.Message):
    await message.answer(help_)


@dp.message_handler(sql.is_admin)
async def not_admin(message: types.Message):
    await message.answer(f"Вы не админ, вот ваш id: `{message.from_user.id}`")


@dp.message_handler(commands=['p', 'prog', 'program'])
async def program(message: types.Message):
    args = message.get_args()
    args = args.replace('\\', '/')

    if args.count(' @.@ '):
        args = args.split(' @.@ ')
        await sql.add_command(message.from_user.id, args[0], args[1])
        await message.answer(f"Была записана команда: \n`{args[0]}`\nПод названием: `{args[1]}`")

    else:
        await message.answer('Введите аргументы для функции типа: \n`/program C:/Program Files/Google/Chrome/Application/chrome.exe, --new-window, https://www.google.com @.@ Google`\n'
                             '*Не забывайте про разделение команд и аргументов *`(, )`* и названия *`( @.@ )`')


@dp.message_handler(commands=['a', 'act', 'activate'])
async def activate(message: types.Message):
    resp = await sql.read_for_bot(message.from_user.id)
    kb = inline(resp, prefix='a')

    await message.answer('Выберете задачу, которую хотите запустить:', reply_markup=kb)

@dp.message_handler(commands=['d', 'del', 'delete'])
async def delete(message: types.Message):
    kb = inline(await sql.read_for_bot(message.from_user.id), prefix='d')
    await message.answer('Выберете задачу, которую хотите удалить:', reply_markup=kb)

@dp.callback_query_handler(lambda callback: callback.data[0] == 'a')
async def callback(callback: types.CallbackQuery):
    command_id = int(callback.data.split('_')[1])
    command_name = await sql.command_name_from_id(command_id)

    kb = inline(await sql.get_pc(), f'f_{command_id}')

    await callback.message.edit_text(f'Выберете компьютер для команды `{command_name}`:', reply_markup=kb)


@dp.callback_query_handler(lambda callback: callback.data[0] == 'd')
async def callback(callback: types.CallbackQuery):
    command_id = int(callback.data.split('_')[1])
    command_name = await sql.command_name_from_id(command_id)

    await sql.delete_command(command_id)
    await callback.message.edit_text(f'Команда `{command_name}` была удалена \.')

@dp.callback_query_handler(lambda callback: callback.data[0] == 'f')
async def f_activate(callback: types.CallbackQuery):
    data = callback.data.split('_')
    command_id = int(data[1])
    ip = data[2]

    command_name = await sql.command_name_from_id(command_id)

    await callback.message.edit_text(f'Задача `{command_name}` запущена на `{ip}`\.')
    await sql.activate_command(command_id, ip)

    await asyncio.sleep(timing())

    await sql.deactivate_command()

    await callback.message.edit_text(f'Задача `{command_name}` выполнена на  `{ip}`\.')

if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True, on_startup=lambda dp: sql.init(), on_shutdown=lambda dp: sql.close())

```
bot_cnf.py:
```python
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

```
cnf.py:
```python
from envparse import env
import requests

env.read_envfile('.env')

link = env('LINK')

def timing():
    return requests.get(link).json()['sleep'] + 1

```
db.py:
```python
import aiosqlite
from aiogram.types import Message

class SQLite:
    # region stuff
    def __init__(self, db_name):
        self.connection = None
        self.cursor = None
        self.db_name = db_name

    async def init(self):
        db_name = self.db_name
        self.connection = await aiosqlite.connect(db_name)
        self.cursor = await self.connection.cursor()

        await self.do("""CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY UNIQUE NOT NULL,
            name TEXT,
            is_admin INTEGER DEFAULT (0)
        );""")

        await self.do("""CREATE TABLE IF NOT EXISTS command (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            user_id INTEGER REFERENCES user (id),
            name TEXT,
            args TEXT
        );""")

        await self.do("""CREATE TABLE IF NOT EXISTS pc (
            ip TEXT PRIMARY KEY UNIQUE NOT NULL,
            active_command INTEGER REFERENCES command (id)
        );""")

    async def do(self, query: str, values=()) -> None:
        await self.cursor.execute(query, values)
        await self.connection.commit()

    async def read(self, query: str, values=(), one=False) -> tuple:
        await self.cursor.execute(query, values)
        if one:
            return await self.cursor.fetchone()
        else:
            return await self.cursor.fetchall()

    async def close(self):
        await self.cursor.close()
        await self.connection.close()
    # endregion
    # region user

    async def user_exists(self, user_id: str) -> bool:
        result = await self.read('SELECT id FROM user WHERE id = ?', (user_id,), one=True)
        return bool(result is None)

    async def new_user(self, user_id: int, username: str) -> None:
        await self.do('INSERT INTO user (id, name) VALUES (?, ?)', (user_id, username))

    async def is_admin(self, message: Message) -> bool:
        result = await self.read('SELECT is_admin FROM user WHERE id = ?', (message.from_user.id,))
        return not bool(result[0])
    # endregion
    # region command_bot

    async def add_command(self, user_id: int, command: str, command_name: str) -> None:
        await self.do('INSERT INTO command (user_id, name, args) VALUES (?, ?, ?)', (user_id, command_name, command))

    async def delete_command(self, command_id: int) -> None:
        await self.do('DELETE FROM command WHERE id = ?', (command_id,))

    async def activate_command(self, command_id: int, ip: str) -> None:
        if ip != 'all':
            await self.do('UPDATE pc SET active_command = ? WHERE ip = ?', (command_id, ip))
            await self.do('UPDATE pc SET active_command = ? WHERE ip = ?', (command_id, ip))
        else:
            await self.do('UPDATE pc SET active_command = ?', (command_id,))

    async def deactivate_command(self) -> None:
        await self.do('UPDATE pc SET active_command = NULL')

    async def read_for_bot(self, user_id: int) -> tuple:
        return await self.read('SELECT id, name FROM command WHERE user_id IS NULL OR user_id = ?', (user_id,))

    async def command_name_from_id(self, command_id: int) -> str:
        result = await self.read('SELECT name FROM command WHERE id = ?', (command_id,), one=True)
        return result[0]

    async def get_pc(self) -> tuple:
        result = await self.read('SELECT ip, ip FROM pc')
        return [('ALL', 'all')] + list(result)

    # endregion
    # region api
    async def pc_exists(self, ip):
        result = await self.read('SELECT ip FROM pc WHERE ip = ?', (ip,), one=True)
        return bool(result is None)

    async def add_pc(self, ip):
        await self.do('INSERT INTO pc (ip) VALUES (?)', (ip,))

    async def api_read(self, ip: str):
        result = await self.read('SELECT args FROM command WHERE id = (SELECT active_command FROM pc WHERE ip = ?)', (ip,), one=True)

        if result is not None:
            result = result[0]

            if result.count(', ') != 0:
                result = result.split(', ')
            else:
                result = [result]

        return result

    # endregion

```
main.py:
```python
from db import SQLite
import json
from fastapi import FastAPI, Request, status
import logging

logging.basicConfig(level=logging.ERROR, filename='app.log')
sql = SQLite('db.db')
app = FastAPI()
app.add_event_handler('startup', sql.init)

with open('main.json', 'r') as file:
    default = json.load(file)

@app.get("/")
async def read_root(request: Request):
    ip = request.client.host

    if await sql.pc_exists(ip):
        await sql.add_pc(ip)

    content = await sql.api_read(ip)

    if content is None:
        return default

    else:
        result = {"args": content}
        result.update(default)
        result["run"] = True
        return result

@app.get("/success", status_code=status.HTTP_204_NO_CONTENT)
async def client_success(request: Request, task: str):
    logging.info(f'SUCCESS:     {request.client.host} - {task}')


@app.post("/error", status_code=status.HTTP_204_NO_CONTENT)
async def client_error(request: Request, error: str):
    logging.error(f'ERROR:     {request.client.host} - {error}')

@app.on_event("shutdown")
async def shutdown_event():
    if sql is not None:
        await sql.close()

```
run.py:
```python
import os
import subprocess
from time import sleep
from cnf import *


def send_error(error: str) -> None:
    try:
        url = f'{link}error?error={error}'
        requests.post(url)

    except Exception as e:
        print(e)

def send_success(success: str) -> None:
    try:
        url = f'{link}success?task={success}'
        requests.post(url)

    except Exception as e:
        print(e)

while True:
    try:
        prev_value = requests.get(link).json()
        break
    except Exception as e:
        print(e)
        sleep(20)


while True:

    try:
        value = requests.get(link).json()

        if value != prev_value and value["run"]:
            try:
                value["args"][0] = value["args"][0].replace('/user/', f'/{os.getlogin()}/')
                subprocess.Popen(value["args"])
                send_success(f"Команда выполнена: {value['args']}")

            except Exception as e:
                send_error(f"Ошибка при выполнении команды: {e}")

        prev_value = value
        sleep(value["sleep"])

    except Exception as e:
        send_error(f"Общая ошибка: {e}")
        sleep(10)

```
sub_test.py:
```python
# import aiogram
# import requests
#
# try:
#     aiogram.Bot(token="dsoikfgj")
# except Exception as e:
#     url = f'http://192.168.0.8:8000/error?error={str(e)}'
#     print(url)
#     requests.post(url)
import subprocess

subprocess.Popen('C:/Program Files/WindowsApps/Microsoft.WindowsNotepad_11.2303.40.0_x64__8wekyb3d8bbwe/Notepad/Notepad.exe')
print("hi")

```
test.py:
```python
from fastapi import FastAPI, Request, HTTPException, status
import logging

logging.basicConfig(level=logging.ERROR, filename='app.log')

app = FastAPI()

@app.get("/")
async def get_client_ip(request: Request):
    client_ip = request.client.host
    return {"client_ip": client_ip}

@app.get("/success")
async def client_success(request: Request, task: str):
    logging.info(f'SUCCESS:     {request.client.host} - {task}')


@app.post("/error", status_code=status.HTTP_204_NO_CONTENT)
async def client_error(request: Request, error: str):
    logging.error(f'ERROR:     {request.client.host} - {error}')

```
