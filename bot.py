from cnf import *


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
