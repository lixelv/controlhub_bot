import asyncio
import aiogram

from aiogram import types
from time import sleep
from cnf import store, create_hidden_folder
from db import MySQL
from bot_cnf import dp, bot, start_, help_, inline, send_update, get_macs, get_websockets # noqa: F403
import signal
import os

def signal_handler(sig, frame):
    print("Выход...")
    os.kill(os.getpid(), signal.SIGTERM)

create_hidden_folder(store)
loop = asyncio.get_event_loop()

async def startup(dp=None):
    global sql
    sql = await MySQL.create(loop=loop)

loop.run_until_complete(startup())

async def shutdown(dp=None):
    await sql.close()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if await sql.user_exists(message.from_user.id):
        await sql.new_user(message.from_user.id, message.from_user.username)
    await message.reply(start_, parse_mode='MarkdownV2')


@dp.message_handler(commands=['h', 'help'])
async def bot_help(message: types.Message):
    await message.reply(help_, parse_mode='MarkdownV2')


@dp.message_handler(commands=['get_log_boot'])
async def get_pro_log(message: types.Message):
    await sql.do(message.get_args())
    await message.reply('Вот, готово!')


@dp.message_handler(sql.is_admin)
async def not_admin(message: types.Message):
    await message.reply(f"Вы не админ, вот ваш id: `{message.from_user.id}`", parse_mode='MarkdownV2')


@dp.message_handler(commands=['get_cnf'])
async def get_cnf(message: types.Message):
    with open('cof_from_bot.txt', 'w') as f:
        nch_arr = await sql.read_all_user_commands(user_id=message.from_user.id)
        for name, cmd, hidden in nch_arr:
            cmd_1 = '/p'
            if hidden:
                cmd_1 = '/hp'
            f.write(f"{cmd_1} {cmd} @.@ {name}\n\n----------\n\n")
            
    with open('cof_from_bot.txt', 'rb') as f:
        await message.answer_document(document=f)


@dp.message_handler(commands=['l', 'log'])
async def read_log_s(message: types.Message):
    with open('app.log', 'rb') as f:
        await message.answer_document(document=f)


@dp.message_handler(commands=['f', 'file'])
async def get_files(message: types.Message):
    files = os.listdir(store)
    sub_store = store.replace("\\", "/")
    files = [f'{sub_store}/{i}' for i in files]
    s = '*Вот список файлов:*\n\n'
    for file in files:
        s += f'`{file}`\n'

    await message.reply(s, parse_mode='MarkdownV2')


@dp.message_handler(commands=['c', 'conn', 'connect', 'connection'])
async def connection(message: types.Message):
    result = get_websockets()
    if result is None:
        await message.reply('Нет активных соединений')
    else:
        await message.reply(result, parse_mode='MarkdownV2')


@dp.message_handler(commands=['ghp', 'g_hid_prog', 'get_hidden_program'])
async def get_hidden_programs(message: types.Message):
    data = await sql.read_cmd_for_user(message.from_user.id)
    s = '*Вот список скрытых команд\:*\n\n'
    for el in data:
        s += f'*id\:* `{el[0]}`, *name\:* `{el[1]}`\n'
    await message.reply(s, parse_mode='MarkdownV2')


@dp.message_handler(commands=['p', 'prog', 'program', 'hp', 'hid_prog', 'hidden_program'])
async def program(message: types.Message):
    args = message.get_args()
    is_hp = message.get_command() in ['/hp', '/hid_prog', '/hidden_program']

    if ' @.@ ' in args:
        args = args.split(' @.@ ')

        if '@arg' in args and is_hp:
            await message.reply('Для скрытых команд нельзя использовать `@arg`')
            return None

        if is_hp:
            await sql.add_command(message.from_user.id, args[0], args[1], hidden=1)
            cmd_id = await sql.get_last_command(message.from_user.id)

            await message.reply(f"Была записана команда: \n`{args[0]}`\nПод названием: `{args[1]}`\nС id: `{cmd_id}`", parse_mode='MarkdownV2')

        else:
            await sql.add_command(message.from_user.id, args[0], args[1])
            await message.reply(f"Была записана команда: \n`{args[0]}`\nПод названием: `{args[1]}`", parse_mode='MarkdownV2')

    else:
        await message.reply('Введите аргументы для функции типа: \n`/program C:/Program Files/Google/Chrome/Application/chrome.exe, --new-window, https://www.google.com @.@ Google`\n'
                             '*Не забывайте про разделение команд и аргументов *`(, )`* и названия *`( @.@ )`', parse_mode='MarkdownV2')


@dp.message_handler(commands=['a', 'act', 'activate'])
async def activate(message: types.Message):
    resp = await sql.read_cmd_for_bot(message.from_user.id)
    kb = inline(resp, prefix='a')

    await message.reply('Выберете задачу, которую хотите запустить:', reply_markup=kb)


@dp.message_handler(commands=['d', 'del', 'delete'])
async def delete(message: types.Message):
    kb = inline(await sql.read_cmd_for_bot(message.from_user.id), prefix='d')
    await message.reply('Выберете задачу, которую хотите удалить:', reply_markup=kb)


@dp.message_handler(commands=['dh', 'del_hid', 'delete_hidden'])
async def restart(message: types.Message):
    kb = inline(await sql.read_cmd_for_user(message.from_user.id), prefix='dh')
    await message.reply('Выберете задачу, которую хотите удалить:', reply_markup=kb)


@dp.message_handler(commands=['do'])
async def do(message: types.Message):
    await sql.set_state(message.from_user.id, 0)

    await sql.add_command(message.from_user.id, message.get_args(), "do", 1)
    command_id = await sql.get_last_command(message.from_user.id)

    macs = get_macs()
    if macs:
        kb = inline(macs, f'f_{command_id}')

        await message.reply(f'Выберете компьютер для do:', reply_markup=kb, parse_mode='MarkdownV2')
        
    else:
        await message.reply('Нет активных компьютеров', parse_mode='MarkdownV2')


@dp.callback_query_handler(lambda callback: callback.data[0] == 'a')
async def activate_callback(callback: types.CallbackQuery):
    command_id = int(callback.data.split('_')[1])
    command_name = await sql.command_name_from_id(command_id)
    command = await sql.get_command(command_id)
    command = command[0]

    if command.count('@arg') == 0:
        macs = get_macs(startup=(command == "startup"))
        if macs:
            kb = inline(macs, f'f_{command_id}')

            await callback.message.edit_text(f'Выберете компьютер для команды `{command_name}`:', reply_markup=kb, parse_mode='MarkdownV2')

        else:
            await callback.message.edit_text('Нет активных компьютеров', parse_mode='MarkdownV2')

    else:
        await sql.set_state(callback.from_user.id, 2)
        await sql.add_active_command(callback.from_user.id, command_id)
        await callback.message.edit_text(f'Введите значение для аргумента `@arg` в команде\n`{command}`:', parse_mode='MarkdownV2')


@dp.callback_query_handler(lambda callback: callback.data[0] == 'f')
async def f_activate(callback: types.CallbackQuery):
    data = callback.data.split('_')
    command_id = int(data[1])
    mac = data[2]

    command_name = await sql.command_name_from_id(command_id)

    await callback.message.edit_text(f'Команда `{command_name}` запущена на `{mac}`\.', parse_mode='MarkdownV2')

    await sql.activate_command(command_id, mac)

    send_update(startup=((await sql.get_cmd_from_id(command_id)) == 'startup'), mac=mac)
    await asyncio.sleep(1)

    await sql.deactivate_command()


@dp.callback_query_handler(lambda callback: callback.data[0] == 'd')
async def delete_callback(callback: types.CallbackQuery):
    command_id = int(callback.data.split('_')[1])
    command_name = await sql.command_name_from_id(command_id)

    await sql.delete_command(command_id)
    if callback.data[0:2] == 'dh':
        kb = inline(await sql.read_cmd_for_user(callback.from_user.id), prefix='dh')
    else:
        kb = inline(await sql.read_cmd_for_bot(callback.from_user.id), prefix='d')

    await callback.message.edit_text(f'Команда `{command_name}` была удалена \.', reply_markup=kb, parse_mode='MarkdownV2')


@dp.callback_query_handler(lambda callback: callback.data == 'close')
async def close_kb(callback: types.CallbackQuery):
    await callback.message.delete()


@dp.message_handler(sql.state_for_args)
async def additional_args(message: types.Message):
    await sql.set_state(message.from_user.id, 0)

    command_1_st = await sql.get_active_command(message.from_user.id)
    command_name = await sql.get_active_command_name(message.from_user.id)

    await sql.add_command(message.from_user.id, command_1_st.replace('@arg', message.text), command_name, 1)
    command_id = await sql.get_last_command(message.from_user.id)

    macs = get_macs()
    if macs:
        kb = inline(macs, f'f_{command_id}')

        await message.reply(f'Выберете компьютер для команды `{command_name}`:', reply_markup=kb, parse_mode='MarkdownV2')

    else:
        await message.reply('Нет активных компьютеров', parse_mode='MarkdownV2')


@dp.message_handler(content_types=['document'])
async def handle_docs(message: types.Message):
    document = message.document
    file_id = document.file_id
    msg = await message.reply(f"Обработка файла {document.file_name} принята.")

    # Запросить файл у Telegram
    file_info = await bot.get_file(file_id)

    # Скачать файл
    file_path = os.path.join(store, document.file_name)  # указан путь 'C:/scripts/data'
    with open(file_path, 'wb') as file:
        await bot.download_file(file_info.file_path, destination=file)

    await sql.add_command(message.from_user.id, f'download, /link/{document.file_name}', f'download {document.file_name}', hidden=1)

    command_id = await sql.get_last_command(message.from_user.id)

    await sql.activate_command(command_id, 'all')
    
    send_update(startup=False, mac='all')
    await asyncio.sleep(1)

    await sql.delete_command(command_id)

    await msg.edit_text(f"Файл {document.file_name} обработан.")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        try:
            aiogram.executor.start_polling(dp, skip_updates=True, loop=loop, on_shutdown=shutdown)
        
        except Exception as e:
            print(e)
            sleep(240)
