import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Состояния бота
CHOOSING, TYPING = range(2)

# Главное меню
reply_keyboard = [
    ["Запрос о помощи", "Предложить ресурс"],
    ["Сообщить о нарушении", "Стать волонтёром"],
    ["Оставить анонимное сообщение", "Поддержать проект"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Это бот поддержки. Чем вы хотите поделиться?",
        reply_markup=markup
    )
    return CHOOSING

# Выбор категории помощи
async def help_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["type"] = update.message.text
    await update.message.reply_text(
        """Пожалуйста, опишите ситуацию. Если это запрос о помощи, уточните категорию:
1. Срочная
2. Юридическая
3. Психологическая
4. Медицинская
5. Жильё или финансы"""
    )
    return TYPING

# Обработка сообщения
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_type = context.user_data.get("type", "Не указано")
    message = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "без username"

    if user_type == "Оставить анонимное сообщение":
        text = f"Анонимное сообщение:\n\n{message}"
    else:
        text = (
            f"Новое сообщение ({user_type}):\n"
            f"От: @{username} (ID {user_id})\n\n{message}"
        )

    await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    await update.message.reply_text("Спасибо! Ваше сообщение получено.")
    context.user_data.clear()
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

# Основной запуск
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_request)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
