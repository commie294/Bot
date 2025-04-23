import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

CHOOSING, TYPING = range(2)

main_keyboard = [
    ["Запрос о помощи", "Предложить ресурс"],
    ["Анонимное сообщение", "Сообщить о нарушении"],
    ["Стать волонтёром", "Пожертвовать"],
    ["Назад"]
]
main_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

help_keyboard = [
    ["Срочная", "Юридическая"],
    ["Психологическая", "Медицинская"],
    ["Жильё и финансы", "Назад"]
]
help_markup = ReplyKeyboardMarkup(help_keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Здравствуйте! Это @t64helper_bot. Пожалуйста, выберите, чем вы хотите поделиться:",
        reply_markup=main_markup
    )
    return CHOOSING


async def help_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Выберите тип помощи:", reply_markup=help_markup)
    return TYPING


async def help_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = update.message.text
    context.user_data["type"] = f"Запрос о помощи ({category})"

    responses = {
        "Срочная": "Опишите вашу ситуацию. Мы постараемся помочь как можно скорее.",
        "Юридическая": (
            "Опишите ваш вопрос. Мы постараемся связать вас с ЛГБТ-френдли юристом.\n"
            "Юридическая помощь может касаться документов, дел, семейных споров и т.д.\n"
            "Учтите: такие обращения не анонимны — будет сохранён ваш ID."
        ),
        "Психологическая": "Опишите вашу ситуацию. Мы постараемся направить вас к т-френдли специалисту.",
        "Медицинская": "Вы можете задать вопрос о гормональной терапии, переходе или других аспектах.",
        "Жильё и финансы": "Опишите свою ситуацию. Мы постараемся найти помощь или ресурсы.",
        "Назад": "Вы вернулись в главное меню."
    }

    if category == "Назад":
        return await start(update, context)

    await update.message.reply_text(responses.get(category, "Опишите ваш запрос:"), reply_markup=main_markup)
    return TYPING


async def anon_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["type"] = "Анонимное сообщение"
    await update.message.reply_text("Напишите сообщение. Оно будет передано без указания отправителя.")
    return TYPING


async def resource(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["type"] = "Предложение ресурса"
    await update.message.reply_text("Опишите ресурс, который вы хотите предложить.")
    return TYPING


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["type"] = "Сообщение о нарушении"
    await update.message.reply_text("Опишите проблему. Мы постараемся отреагировать.")
    return TYPING


async def volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Если вы хотите присоединиться к нашей команде, пожалуйста, заполните анкету волонтёра:\n"
        "https://forms.gle/n2mZdRA2fYBeeCUY7",
        reply_markup=main_markup
    )
    return CHOOSING


async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Вы можете поддержать нас по ссылке: https://boosty.to/t64helper\n"
        "или уточнить криптовалютные способы у админа.",
        reply_markup=main_markup
    )
    return CHOOSING


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    user = update.effective_user
    msg_type = context.user_data.get("type", "Не указано")

    message = f"Новое сообщение:\nТип: {msg_type}\n"
    if msg_type != "Анонимное сообщение":
        message += f"От: @{user.username or 'без username'} (ID: {user.id})\n"
    message += f"\n{text}"

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    await update.message.reply_text("Спасибо! Ваше сообщение отправлено.", reply_markup=main_markup)

    context.user_data.clear()
    return CHOOSING


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Действие отменено.", reply_markup=main_markup)
    return CHOOSING


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^Запрос о помощи$"), help_request),
                MessageHandler(filters.Regex("^Анонимное сообщение$"), anon_message),
                MessageHandler(filters.Regex("^Предложить ресурс$"), resource),
                MessageHandler(filters.Regex("^Сообщить о нарушении$"), report),
                MessageHandler(filters.Regex("^Стать волонтёром$"), volunteer),
                MessageHandler(filters.Regex("^Пожертвовать$"), donate),
            ],
            TYPING: [
                MessageHandler(filters.Regex("^(Срочная|Юридическая|Психологическая|Медицинская|Жильё и финансы|Назад)$"), help_category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()
