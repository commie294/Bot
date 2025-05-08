import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот запущен.")

async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN не найден в файле .env")
        return

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))

    logger.info("Starting bot with polling...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())
