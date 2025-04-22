import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Загружаем токен и ID из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1835516062"))

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это @t64helper_bot. Напиши сюда сообщение — и оно будет анонимно передано модератору."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ты можешь отправить:\n— предложения и идеи\n— ресурсы\n— просьбы о помощи\n\nВсё это анонимно пересылается модерации."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    log_text = f"Сообщение от @{user.username or user.id}:\n{text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=log_text)
    await update.message.reply_text("Спасибо! Твоё сообщение получено.")

# Удаляем старый вебхук (на случай, если был)
async def on_startup(app: Application):
    await app.bot.delete_webhook(drop_pending_updates=True)

# Запуск
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
