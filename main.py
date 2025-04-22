import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# ID админа
ADMIN_ID = 1835516062

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это @t64helper_bot — бот для приёма анонимных сообщений и ресурсов для трансгендерного сообщества СНГ.\n\n"
        "Ты можешь:\n"
        "- просто отправить сообщение или ссылку\n"
        "- использовать /help чтобы узнать больше"
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Этот бот собирает сообщения, предложения и ресурсы для трансгендерного сообщества СНГ. "
        "Все сообщения пересылаются админу анонимно.\n\n"
        "Доступные команды:\n"
        "/start — начать\n"
        "/help — помощь\n"
        "/info — о проекте"
    )

# Команда /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Проект создан для сбора и распространения информации, поддержки и ресурсов для трансгендерных персон "
        "в условиях ограничений и давления в странах СНГ. Ты можешь отправить нам полезный ресурс, новость или предложение."
    )

# Обработка обычных сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    sender = update.message.from_user

    # Пересылаем админу
    admin_message = f"Новое сообщение от @{sender.username or sender.id}:\n{message}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)

    await update.message.reply_text("Спасибо! Твое сообщение получено.")

# Запуск бота
def main():
    token = os.getenv("BOT_TOKEN") or "8038993649:AAGXZMo5nMMJA3A00ZRyg_jpQVXMmdRUyxY"
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
