import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

CHOOSING, TYPING = range(2)

reply_keyboard = [
    ["Запрос о помощи", "Сообщить о нарушении"],
    ["Предложить ресурс", "Анонимное сообщение"],
    ["Хочу помочь"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

help_types = [
    "Срочная", "Юридическая", "Психологическая", "Медицинская", "Финансовая и жильё", "Другое"
]

help_markup = ReplyKeyboardMarkup(
    [[t] for t in help_types], one_time_keyboard=True, resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Это @t64helper_bot. Пожалуйста, выберите, что вы хотите отправить:",
        reply_markup=markup
    )
    return CHOOSING

async def choose_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["choice"] = text

    if text == "Запрос о помощи":
        await update.message.reply_text("Выберите категорию помощи:", reply_markup=help_markup)
        return TYPING
    elif text == "Сообщить о нарушении":
        await update.message.reply_text("Опишите ситуацию с нарушением.")
        return TYPING
    elif text == "Предложить ресурс":
        await update.message.reply_text("Опишите ресурс, который вы хотите предложить.")
        return TYPING
    elif text == "Анонимное сообщение":
        await update.message.reply_text("Напишите ваше сообщение. Оно будет передано модерации.")
        return TYPING
    elif text == "Хочу помочь":
        await update.message.reply_text(
            "Чтобы стать волонтёром, ответьте на несколько вопросов.\n"
            "1. Как вы хотите помогать?\n"
            "2. Есть ли у вас опыт?\n"
            "3. Уточните ваши контакты, по желанию."
        )
        return TYPING

async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = context.user_data.get("choice", "Сообщение")
    user_id = update.effective_user.id
    username = update.effective_user.username or "Без username"
    message = update.message.text

    # В случае юридической помощи — не анонимно
    if choice == "Запрос о помощи" and context.user_data.get("subcategory") == "Юридическая":
        send_text = f"Юридический запрос от @{username} (ID {user_id}):\n\n{message}"
    else:
        send_text = f"{choice}:\n\n{message}"

    if choice == "Запрос о помощи" and not context.user_data.get("subcategory"):
        context.user_data["subcategory"] = message
        await update.message.reply_text("Теперь опишите вашу ситуацию.")
        return TYPING

    await context.bot.send_message(chat_id=ADMIN_ID, text=send_text)
    await update.message.reply_text("Спасибо! Ваше сообщение отправлено.")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено. Напишите /start, чтобы начать заново.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_option)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
