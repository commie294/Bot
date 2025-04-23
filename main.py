import logging
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
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

CHOOSING, TYPING_REPLY = range(2)

reply_keyboard = [
    ["Запрос о помощи", "Предложить помощь"],
    ["Анонимное сообщение", "Стать волонтёром"],
    ["Назад"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

help_keyboard = [
    ["Срочная", "Юридическая"],
    ["Психологическая", "Медицинская"],
    ["Жильё и финансы", "Назад"]
]
help_markup = ReplyKeyboardMarkup(help_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Здравствуйте! Это @t64helper_bot. Что вы хотите отправить?",
        reply_markup=markup
    )
    return CHOOSING

async def help_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Выберите вид помощи:", reply_markup=help_markup)
    return TYPING_REPLY

async def help_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = update.message.text
    replies = {
        "Срочная": "Пожалуйста, опишите вашу ситуацию. Мы постараемся помочь как можно скорее.",
        "Юридическая": (
            "Опишите ваш вопрос. Мы постараемся связать вас с ЛГБТ-френдли юристом.\n"
            "Юридическая помощь может быть предоставлена по вопросам смены документов, уголовных или административных дел, семейных споров и т.д.\n"
            "Пожалуйста, учтите, что юридическая помощь не является анонимной, будет использован ваш ID."
        ),
        "Психологическая": (
            "Опишите ситуацию, и мы постараемся направить вас к т-френдли психологу.\n"
            "Если хотите оставить анонимное сообщение — напишите «Анонимно»."
        ),
        "Медицинская": (
            "Вы можете описать ваш вопрос, и мы постараемся помочь вам найти информацию о гормональной терапии, операциях и других медицинских темах, связанных с трансгендерным переходом."
        ),
        "Жильё и финансы": (
            "Опишите вашу ситуацию, и мы постараемся найти ресурсы или людей, которые смогут помочь с жильём, финансовыми вопросами, продуктами и т.д."
        ),
        "Назад": await start(update, context)
    }

    text = replies.get(category, "Пожалуйста, выберите категорию помощи.")
    if text != None:
        await update.message.reply_text(text, reply_markup=markup)
        if category != "Назад":
            context.user_data["category"] = category
            return TYPING_REPLY
    return CHOOSING

async def volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Если вы хотите стать волонтёром, заполните, пожалуйста, анкету:\n"
        "https://docs.google.com/forms/d/e/1FAIpQLSe1... (замените на свою ссылку)",
        reply_markup=markup
    )
    return CHOOSING

async def anonymous(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Напишите своё сообщение. Мы не будем собирать информацию о вас.")
    return TYPING_REPLY

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    user = update.effective_user
    category = context.user_data.get("category", "Сообщение")
    message = f"Новое сообщение:\nКатегория: {category}\nОт: @{user.username or 'аноним'} (ID: {user.id})\n\n{text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=message)

    await update.message.reply_text(
        "Спасибо! Ваше сообщение отправлено. Вы можете выбрать другой пункт меню.",
        reply_markup=markup
    )
    return CHOOSING

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await start(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("До свидания!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(Запрос о помощи)$"), help_request),
                MessageHandler(filters.Regex("^(Стать волонтёром)$"), volunteer),
                MessageHandler(filters.Regex("^(Анонимное сообщение)$"), anonymous),
                MessageHandler(filters.Regex("^(Предложить помощь|Назад)$"), start),
            ],
            TYPING_REPLY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
