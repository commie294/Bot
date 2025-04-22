import os
import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Команда /start
async def start(update, context):
    await update.message.reply_text(
        "Привет! Это бот приёма сообщений и ресурсов. Просто напиши сюда, что хочешь отправить."
    )

# Обработка обычных сообщений
async def handle_message(update, context):
    user = update.message.from_user
    text = update.message.text

    # Пересылаем админу
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"Сообщение от @{user.username or user.id}:\n{text}")
    await update.message.reply_text("Спасибо! Твое сообщение отправлено модераторам.")

# Запуск бота
async def main():
    application = Application.builder().token(TOKEN).build()

    # Удаляем вебхук на всякий случай
    bot = Bot(TOKEN)
    await bot.delete_webhook()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
