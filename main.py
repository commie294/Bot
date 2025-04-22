import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Загружаем .env переменные
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1835516062"))

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Это бот t64helper — просто напиши сюда любое сообщение, и оно будет переслано модераторам.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши сюда ресурс, идею, тревожный сигнал — и это анонимно будет передано модератору.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    log_text = f"Сообщение от @{user.username or user.id}:\n{text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=log_text)
    await update.message.reply_text("Спасибо! Твоё сообщение получено.")

# Удаление вебхука при запуске
async def remove_webhook(application: Application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    logging.info("Webhook удалён")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling(post_init=remove_webhook)

if __name__ == "__main__":
    main()
