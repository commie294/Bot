import os
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Получаем токен и ID админа из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1835516062"))  # можно хардкодить при локальном запуске

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это бот для приёма предложений и ресурсов для трансгендерного сообщества. "
        "Просто напиши, что хочешь отправить — это анонимно. Спасибо за участие!"
    )

# Приём любых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # Ответ пользователю
    await update.message.reply_text("Спасибо! Твоё сообщение получено и передано модерации.")

    # Пересылка админу
    admin_text = f"Новое сообщение от @{user.username or 'без_ника'} (ID: {user.id}):\n\n{text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

def main():
    app = Application.builder().token(TOKEN).build()

    # Удалим старый вебхук (если был)
    bot: Bot = app.bot
    app.run_coroutine(bot.delete_webhook())

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
