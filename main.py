import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Загружаем токен из .env (если есть)
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1835516062"))

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это @t64helper_bot — бот для приёма сообщений и ресурсов для трансгендерного сообщества СНГ.\n"
        "Просто напиши сюда сообщение, и оно будет передано модерации анонимно.\n"
        "Команды: /start /help"
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ты можешь отправить:\n"
        "- предложения и идеи\n"
        "- полезные ресурсы\n"
        "- срочные сигналы или просьбы о помощи\n\n"
        "Бот пересылает их модератору, всё анонимно."
    )

# Обработка текстов
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    log_text = f"Сообщение от @{user.username or user.id}:\n{text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=log_text)
    await update.message.reply_text("Спасибо! Твоё сообщение получено.")

# Удаление вебхука перед запуском polling
async def clear_webhook(application):
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        logging.info("Webhook удалён")
    except Exception as e:
        logging.warning(f"Ошибка при удалении вебхука: {e}")

# Главный запуск
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    asyncio.run(clear_webhook(application))
    application.run_polling()

if __name__ == "__main__":
    main()
