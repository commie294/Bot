import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

(
    CHOOSING,
    TYPING_MESSAGE,
    HELP_REQUEST,
    VOLUNTEER,
) = range(4)

main_keyboard = [
    ["Запрос о помощи", "Предложить ресурс"],
    ["Сообщить о нарушении", "Стать волонтёром"],
    ["Оставить анонимное сообщение", "Поддержать проект"],
]
main_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

help_keyboard = [
    ["Срочная", "Юридическая"],
    ["Психологическая", "Медицинская"],
    ["Финансовая/Жильё", "Назад"],
]
help_markup = ReplyKeyboardMarkup(help_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Здравствуйте! Это @t64helper_bot.\n"
        "Пожалуйста, выберите, что вы хотите сделать:",
        reply_markup=main_markup
    )
    return CHOOSING

async def main_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["choice"] = text

    if text == "Оставить анонимное сообщение":
        await update.message.reply_text("Пожалуйста, введите сообщение. Оно будет передано анонимно.")
        return TYPING_MESSAGE
    elif text == "Поддержать проект":
        await update.message.reply_text(
            "Спасибо за желание помочь!\n"
            "Вы можете поддержать нас по ссылке:\n"
            "https://boosty.to/t64helper"
        )
        return CHOOSING
    elif text == "Стать волонтёром":
        await update.message.reply_text(
            "Пожалуйста, расскажите немного о себе и чем вы можете помочь. Мы свяжемся с вами при необходимости."
        )
        return VOLUNTEER
    elif text == "Запрос о помощи":
        await update.message.reply_text("Выберите вид помощи:", reply_markup=help_markup)
        return HELP_REQUEST
    else:
        await update.message.reply_text("Опишите, пожалуйста, ваш запрос или сообщение.")
        return TYPING_MESSAGE

async def help_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Назад":
        await update.message.reply_text("Возврат в главное меню:", reply_markup=main_markup)
        return CHOOSING

    context.user_data["help_type"] = text
    await update.message.reply_text(
        f"Вы выбрали: {text} помощь.\nОпишите ситуацию, и мы постараемся вам помочь."
    )
    return TYPING_MESSAGE

async def received_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_id = update.message.from_user.id
    choice = context.user_data.get("choice", "Сообщение")
    help_type = context.user_data.get("help_type")

    if choice == "Запрос о помощи":
        header = f"Запрос помощи: {help_type}"
    else:
        header = f"{choice}"

    message = f"{header}\n\n{user_input}"
    if choice != "Оставить анонимное сообщение":
        message += f"\n\nUser ID: {user_id}"

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    await update.message.reply_text("Спасибо, ваше сообщение получено!", reply_markup=main_markup)
    return CHOOSING

async def volunteer_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_id = update.message.from_user.id
    message = f"Заявка волонтёра:\n\n{user_input}\n\nUser ID: {user_id}"

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    await update.message.reply_text("Спасибо! Мы свяжемся с вами при необходимости.", reply_markup=main_markup)
    return CHOOSING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Действие отменено.", reply_markup=main_markup)
    return CHOOSING

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_choice)],
            HELP_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_type)],
            TYPING_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_message)],
            VOLUNTEER: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_info)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
