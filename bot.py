import aiofiles
import asyncio
import json
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
