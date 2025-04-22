import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1835516062

async def start(update, context):
    await update.message.reply_text("Привет! Это бот для приёма предложений и ресурсов для трансгендерного сообщества. Напиши сюда, что ты хочешь предложить.")

async def echo(update, context):
    user = update.message.from_user
    text = update.message.text
    print(f"Сообщение от {user.username or user.id}: {text}")
    await update.message.reply_text("Спасибо! Твое сообщение получено.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()

if __name__ == "__main__":
    main()
