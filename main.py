import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Получена команда /start от пользователя {update.effective_user.id}")
    await update.message.reply_text("Привет! Бот запущен.")

async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN не найден в файле .env")
        return

    logger.info("Создание Application...")
    application = Application.builder().token(token).build()
    logger.info("Application создан.")

    application.add_handler(CommandHandler("start", start))
    logger.info("Обработчик /start добавлен.")

    logger.info("Запуск polling в текущем event loop...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Future()  # Держим event loop запущенным

if __name__ == "__main__":
    asyncio.run(main())
