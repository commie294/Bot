import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

CHOOSING, TYPING = range(2)

menu_keyboard = [
    ["Запрос о помощи"],
    ["Анонимное сообщение", "Предложить ресурс"],
    ["Сообщить о нарушении", "Стать волонтёром"],
    ["Пожертвовать"]
]
menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

help_keyboard = [
    ["Срочная", "Юридическая"],
    ["Психологическая", "Медицинская"],
    ["Финансовая / Жильё", "Другая"]
]
help_markup = ReplyKeyboardMarkup(help_keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Это @t64helper_bot. Чем мы можем вам помочь?",
        reply_markup=menu_markup
    )
    return CHOOSING


async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["choice"] = text

    if text == "Запрос о помощи":
        await update.message.reply_text("Выберите тип помощи:", reply_markup=help_markup)
        return CHOOSING

    elif text == "Анонимное сообщение":
        await update.message.reply_text("Пожалуйста, опишите ситуацию, мы не будем знать, кто вы.")
        return TYPING

    elif text == "Предложить ресурс":
        await update.message.reply_text("Опишите полезный ресурс, который вы хотите предложить.")
        return TYPING

    elif text == "Сообщить о нарушении":
        await update.message.reply_text("Опишите ситуацию, мы постараемся на неё отреагировать.")
        return TYPING

    elif text == "Стать волонтёром":
        await update.message.reply_text(
            "Пожалуйста, расскажите о себе. Чем вы можете помочь, сколько у вас времени и т.д."
        )
        return TYPING

    elif text == "Пожертвовать":
        await update.message.reply_text(
            "Пожертвования можно отправить по этой ссылке:\nhttps://t.me/t64helper_bot/support"
        )
        return CHOOSING

    elif text in ["Срочная", "Юридическая", "Психологическая", "Медицинская", "Финансовая / Жильё", "Другая"]:
        context.user_data["subtype"] = text
        await update.message.reply_text("Опишите, пожалуйста, вашу ситуацию.")
        return TYPING

    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")
        return CHOOSING


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    choice = context.user_data.get("choice", "Неизвестно")
    subtype = context.user_data.get("subtype", "")

    msg = f"Новое сообщение от пользователя:\n\n"
    msg += f"Категория: {choice}\n"
    if subtype:
        msg += f"Подкатегория: {subtype}\n"
    msg += f"Текст:\n{user_input}"

    # Отправка админу
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    # Ответ пользователю
    if choice == "Запрос о помощи":
        await update.message.reply_text(
            "Спасибо! Мы постараемся как можно скорее рассмотреть ваш запрос.",
            reply_markup=menu_markup
        )
    elif choice == "Стать волонтёром":
        await update.message.reply_text(
            "Спасибо! Мы свяжемся с вами, если будет подходящая возможность.",
            reply_markup=menu_markup
        )
    else:
        await update.message.reply_text(
            "Спасибо, ваше сообщение получено.",
            reply_markup=menu_markup
        )

    context.user_data.clear()
    return CHOOSING


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог завершён. Напишите /start для начала.")
    return ConversationHandler.END


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
