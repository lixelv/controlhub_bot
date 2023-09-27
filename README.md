bot.py:
```python
import asyncio
from db import SQLite
from aiogram import types
from bot_cnf import *

sql = SQLite('db.db')

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if sql.user_exists(message.from_user.id):
        sql.new_user(message.from_user.id, message.from_user.username)
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
        sql.add_command(message.from_user.id, args[0], args[1])
        await message.answer(f"Была записана команда: \n`{args[0]}`\nПод названием: `{args[1]}`")

    else:
        await message.answer('Введите аргументы для функции типа: \n`/program C:/Program Files/Google/Chrome/Application/chrome.exe, --new-window, https://www.google.com @.@ Google`\n'
                             '*Не забывайте про разделение команд и аргументов *`(, )`* и названия *`( @.@ )`')


@dp.message_handler(commands=['a', 'act', 'activate'])
async def activate(message: types.Message):
    resp = sql.read_for_bot(message.from_user.id)
    kb = inline(resp, prefix='a')

    await message.answer('Выберете задачу, которую хотите запустить:', reply_markup=kb)

@dp.message_handler(commands=['d', 'del', 'delete'])
async def delete(message: types.Message):
    kb = inline(sql.read_for_bot(message.from_user.id), prefix='d')
    await message.answer('Выберете задачу, которую хотите удалить:', reply_markup=kb)

@dp.callback_query_handler(lambda callback: callback.data[0] == 'a')
async def callback(callback: types.CallbackQuery):
    command_id = int(callback.data.split('_')[1])
    command_name = sql.command_name_from_id(command_id)

    await callback.message.edit_text(f'Задача `{command_name}` запущена\.')
    sql.activate_command(command_id)
    await asyncio.sleep(timing())
    sql.deactivate_command()

    await callback.message.edit_text(f'Задача `{command_name}` выполнена\.')


@dp.callback_query_handler(lambda callback: callback.data[0] == 'd')
async def callback(callback: types.CallbackQuery):
    command_id = int(callback.data.split('_')[1])
    command_name = sql.command_name_from_id(command_id)

    sql.delete_command(command_id)
    await callback.message.edit_text(f'Команда `{command_name}` была удалена \.')

if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True)

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
    for id_, name_ in lst:
        kb.add(InlineKeyboardButton(name_, callback_data=f'{prefix}_{id_}'))

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
import sqlite3
from aiogram.types import Message

class SQLite:
    # region stuff
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

        self.do("""CREATE TABLE IF NOT EXISTS user (
    id       INTEGER PRIMARY KEY
                     UNIQUE
                     NOT NULL,
    name     TEXT,
    is_admin INTEGER DEFAULT (0) 
);""")

        self.do("""CREATE TABLE IF NOT EXISTS command (
    id      INTEGER PRIMARY KEY AUTOINCREMENT
                    UNIQUE
                    NOT NULL,
    user_id INTEGER REFERENCES user (id),
    name    TEXT,
    args    TEXT,
    active  INTEGER DEFAULT (0) 
);""")

    def do(self, query: str, values=()) -> None:
        self.cursor.execute(query, values)
        self.connection.commit()

    def read(self, query: str, values=(), one=False) -> tuple:
        self.cursor.execute(query, values)
        return self.cursor.fetchone() if one else self.cursor.fetchall()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    # endregion
    # region user

    def user_exists(self, user_id: str) -> bool:
        result = self.read('SELECT id FROM user WHERE id = ?', (user_id,), one=True)
        return bool(result is None)

    def new_user(self, user_id: int, username: str) -> None:
        self.do('INSERT INTO user (id, name) VALUES (?, ?)', (user_id, username))

    def is_admin(self, message: Message) -> bool:
        return not bool(self.read('SELECT is_admin FROM user WHERE id = ?', (message.from_user.id,), one=True)[0])
    # endregion
    # region command_bot

    def add_command(self, user_id: int, command: str, command_name: str) -> None:
        self.do('INSERT INTO command (user_id, name, args) VALUES (?, ?, ?)', (user_id, command_name, command))

    def delete_command(self, command_id: int) -> None:
        self.do('DELETE FROM command WHERE id = ?', (command_id,))

    def activate_command(self, command_id: int) -> None:
        self.do('UPDATE command SET active = 1 WHERE id = ?', (command_id,))

    def deactivate_command(self) -> None:
        self.do('UPDATE command SET active = 0 WHERE active = 1')

    def read_for_bot(self, user_id: int) -> tuple:
        return self.read('SELECT id, name FROM command WHERE user_id IS NULL OR user_id = ?', (user_id,))

    def command_name_from_id(self, command_id: int) -> str:
        return self.read('SELECT name FROM command WHERE id = ?', (command_id,), one=True)[0]
    # endregion
    # region command_api

    def api_read(self):
        result = self.read('SELECT args FROM command WHERE active = 1', one=True)

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
from fastapi import FastAPI
from db import SQLite
import json

sql = SQLite('db.db')
app = FastAPI()


with open('main.json', 'r') as file:
    default = json.load(file)

@app.get("/")
async def read_root():
    content = sql.api_read()
    if content is None:
        return default

    else:
        result = {"args": content}
        result.update(default)
        result["run"] = True
        return result

```
run.py:
```python
import subprocess
import os
from time import sleep
from cnf import *

prev_value = requests.get(link).json()

while True:

    value = requests.get(link).json()

    if value != prev_value and value["run"]:
        try:
            value["args"][0] = value["args"][0].replace('/user/', f'/{os.getlogin()}/')

            subprocess.run(value["args"])

        except Exception as e:
            print(f"Error {e}")

    prev_value = value

    sleep(value["sleep"])


```
test.py:
```python
import db
import json

sql = db.SQLite('db.db')

print(sql.api_read())
with open('main.json', 'r') as file:
    default = json.load(file)

print({"args": [1, 2, 3]}.update(default))

```
