from aiogram import Bot, Dispatcher, types, executor
from wakeonlan import send_magic_packet

bot = Bot('5980468447:AAF7h-PWEQD2auAREdPx1PWYt6hXfwL_dYI')
dp = Dispatcher(bot)

@dp.message_handler(commands=['w', 'wake'])
async def wake(message: types.Message):
    mac = message.get_args()
    send_magic_packet(mac)
    await message.answer(f'Запущен `{mac}`', parse_mode='MarkdownV2')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
