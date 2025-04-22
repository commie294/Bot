import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Состояния для волонтёра и анонимного сообщения
VOLUNTEER_NAME, VOLUNTEER_CONTACT, VOLUNTEER_SKILLS = range(3)
ANON_MESSAGE = range(1)

# Главное меню
main_menu = ReplyKeyboardMarkup([
    [KeyboardButton("Запрос о помощи")],
    [KeyboardButton("Оставить анонимное сообщение")],
    [KeyboardButton("Пожертвовать"), KeyboardButton("Стать волонтёром")]
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Это бот поддержки. Выберите, что хотите сделать:",
        reply_markup=main_menu
    )

# --- Пожертвования ---
async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вы можете поддержать нас здесь:\nhttps://example.com/donate\n"
        "Спасибо за вашу помощь!"
    )

# --- Волонтёр ---
async def start_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, введите ваше имя или псевдоним:")
    return VOLUNTEER_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Как с вами можно связаться? (например, Telegram @username)")
    return VOLUNTEER_CONTACT

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text
    await update.message.reply_text("В чём вы можете помочь или в чём заинтересованы?")
    return VOLUNTEER_SKILLS

async def get_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["skills"] = update.message.text
    summary = (
        "Новая анкета волонтёра:\n"
        f"Имя: {context.user_data['name']}\n"
        f"Контакт: {context.user_data['contact']}\n"
        f"Навыки: {context.user_data['skills']}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=summary)
    await update.message.reply_text("Спасибо! Мы свяжемся с вами, если понадобится помощь.")
    return ConversationHandler.END

volunteer_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Стать волонтёром$"), start_volunteer)],
    states={
        VOLUNTEER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        VOLUNTEER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
        VOLUNTEER_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_skills)],
    },
    fallbacks=[],
)

# --- Анонимное сообщение ---
async def anon_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите сообщение, которое вы хотите отправить анонимно:")
    return ANON_MESSAGE

async def forward_anon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"Анонимное сообщение:\n{update.message.text}")
    await update.message.reply_text("Спасибо! Ваше сообщение отправлено анонимно.")
    return ConversationHandler.END

anon_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Оставить анонимное сообщение$"), anon_message)],
    states={ANON_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, forward_anon)]},
    fallbacks=[],
)

# --- Запуск ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Пожертвовать$"), donate))
    app.add_handler(volunteer_conv)
    app.add_handler(anon_conv)

    print("Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()
