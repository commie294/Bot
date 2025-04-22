import os
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

async def start(update, context):
    await update.message.reply_text(
        "Привет! Это бот приёма сообщений. Просто напиши сюда, что хочешь отправить."
    )

async def handle_message(update, context):
    user = update.message.from_user
    text = update.message.text

    await context.bot.send_message(chat_id=ADMIN_ID, text=f"Сообщение от @{user.username or user.id}:\n{text}")
    await update.message.reply_text("Спасибо! Твое сообщение отправлено.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
