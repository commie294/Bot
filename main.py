import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters,
    ConversationHandler
)
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1835516062"))

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Состояния
CHOOSE_ACTION, AWAITING_INPUT = range(2)
user_states = {}

# Основное меню
main_keyboard = [
    ["Запрос о помощи", "Предложить ресурс"],
    ["Сообщить о нарушении", "Хочу быть волонтёром"]
]
markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это @t64helper_bot. Что ты хочешь отправить?",
        reply_markup=markup
    )
    return CHOOSE_ACTION

# Обработка выбора действия
async def choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    categories = {
        "Запрос о помощи": "help_request",
        "Предложить ресурс": "resource",
        "Сообщить о нарушении": "report",
        "Хочу быть волонтёром": "volunteer"
    }

    if text not in categories:
        await update.message.reply_text("Пожалуйста, выбери один из предложенных вариантов.", reply_markup=markup)
        return CHOOSE_ACTION

    user_states[user_id] = categories[text]

    prompts = {
        "help_request": """Выбери вид помощи:
1. Срочная
2. Юридическая
3. Психологическая
4. Другая

И опиши ситуацию.""",
        "resource": "Опиши ресурс: ссылка, описание, город и т.д.",
        "report": "Опиши, что произошло. Мы передадим это модерации — анонимно.",
        "volunteer": "Расскажи, чем ты можешь помочь: юридическая, психологическая, перевод и т.д."
    }

    await update.message.reply_text(prompts[categories[text]], reply_markup=ReplyKeyboardRemove())
    return AWAITING_INPUT

# Получение сообщения от пользователя
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    user_id = user.id
    category = user_states.get(user_id, "обращение")

    labels = {
        "help_request": "[ЗАПРОС О ПОМОЩИ]",
        "resource": "[ПРЕДЛОЖЕНИЕ РЕСУРСА]",
        "report": "[СООБЩЕНИЕ О НАРУШЕНИИ]",
        "volunteer": "[ВОЛОНТЁР]"
    }

    header = labels.get(category, "[ОБРАЩЕНИЕ]")
    message = f"{header}\n{text}"

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    await update.message.reply_text("Спасибо! Твоё сообщение передано анонимно модерации.", reply_markup=markup)

    user_states.pop(user_id, None)
    return CHOOSE_ACTION

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Бот принимает анонимные сообщения, предложения, ресурсы и сигналы.\n"
        "Просто выбери нужную кнопку."
    )

# Запуск
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_action)],
            AWAITING_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
        },
        fallbacks=[CommandHandler("help", help_command)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling()

if __name__ == "__main__":
    main()
