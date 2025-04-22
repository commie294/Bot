from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=types.ContentTypes.ANY)
async def forward_message(message: Message):
    try:
        text = f"Новое сообщение от пользователя:\n\n{message.text}"
        await bot.send_message(chat_id=ADMIN_ID, text=text)
        await message.reply("Спасибо! Ваше сообщение отправлено модератору.")
    except Exception as e:
        await message.reply("Произошла ошибка. Попробуйте позже.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
