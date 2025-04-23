import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Состояния диалога
START, MENU, HELP_TYPE, TYPING, FAQ_LEGAL, FAQ_MED = range(6)

# Ответы на FAQ
FAQ_RESPONSES = {
    # Юридические вопросы
    "Как сменить документы?": """Полный текст ответа...""",
    "Что такое пропаганда ЛГБТ?": """Полный текст ответа...""",
    
    # Медицинские вопросы
    "Женская ГТ": """Полный текст ответа...""",
    "Мужская ГТ": """Полный текст ответа...""",
    "Диагноз F64": """Полный текст ответа...""",
    "Где делают операции?": """Полный текст ответа..."""
}

# Клавиатуры
main_kb = ReplyKeyboardMarkup([
    ["Запрос о помощи"],
    ["Предложить ресурс", "Пожертвовать"],
    ["Анонимное сообщение", "Стать волонтёром"],
    ["Назад"]
], resize_keyboard=True)

help_kb = ReplyKeyboardMarkup([
    ["Юридическая", "Медицинская"],
    ["Психологическая", "Жильё и финансы"],
    ["Назад"]
], resize_keyboard=True)

legal_faq_kb = ReplyKeyboardMarkup([
    ["Как сменить документы?", "Что такое пропаганда ЛГБТ?"],
    ["Консультация юриста", "Назад"]
], resize_keyboard=True)

medical_faq_kb = ReplyKeyboardMarkup([
    ["Женская ГТ", "Мужская ГТ"],
    ["Диагноз F64", "Где делают операции?"],
    ["Консультация врача", "Назад"]
], resize_keyboard=True)

# ID каналов
CHANNELS = {
    "Юридическая": -100123456,
    "Психологическая": -100789012,
    "Медицинская": -100345678,
    "Жильё и финансы": -100901234,
    "Анонимное сообщение": -100567890,
    "Ресурсы": -100567890
}

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=main_kb
    )
    return MENU

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Это бот поддержки проекта 'Переход в неположенном месте'.\n\n"
        "Вы можете:\n"
        "- Запросить помощь\n"
        "- Предложить полезный ресурс\n"
        "- Поддержать проект финансово\n"
        "- Стать волонтёром\n"
        "- Отправить анонимное сообщение",
        reply_markup=main_kb
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "Запрос о помощи":
        await update.message.reply_text("Выберите категорию помощи:", reply_markup=help_kb)
        return HELP_TYPE
    elif choice == "Предложить ресурс":
        context.user_data["type"] = "Предложение ресурса"
        await update.message.reply_text("Опишите ресурс, который хотите предложить:", reply_markup=ReplyKeyboardRemove())
        return TYPING
    elif choice == "Пожертвовать":
        await update.message.reply_text(
            "Вы можете поддержать проект:\n\n"
            "• Boosty: https://boosty.to/t64/donate\n"
            "• USDT (TRC-20): TLTBoXCSifWGBeuiRkxkPtH9M9mfwSf1sf",
            reply_markup=main_kb
        )
        return MENU
    elif choice == "Стать волонтёром":
        await update.message.reply_text(
            "Заполните анкету волонтёра:\n"
            "https://forms.gle/n2mZdRA2fYBeeCUY7",
            reply_markup=main_kb
        )
        return MENU
    elif choice == "Анонимное сообщение":
        context.user_data["type"] = "Анонимное сообщение"
        await update.message.reply_text("Напишите ваше сообщение:", reply_markup=ReplyKeyboardRemove())
        return TYPING
    elif choice == "Назад":
        return await start(update, context)
    return MENU

async def help_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = update.message.text
    if category == "Юридическая":
        await update.message.reply_text("Выберите вопрос:", reply_markup=legal_faq_kb)
        return FAQ_LEGAL
    elif category == "Медицинская":
        await update.message.reply_text("Выберите вопрос:", reply_markup=medical_faq_kb)
        return FAQ_MED
    elif category == "Назад":
        return await start(update, context)
    else:
        context.user_data["type"] = f"Запрос - {category}"
        await update.message.reply_text("Опишите вашу ситуацию:", reply_markup=ReplyKeyboardRemove())
        return TYPING

async def handle_legal_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = update.message.text
    if question == "Назад":
        await update.message.reply_text("Выберите категорию:", reply_markup=help_kb)
        return HELP_TYPE
    elif question == "Консультация юриста":
        context.user_data["type"] = "Юридическая - Консультация"
        await update.message.reply_text("Опишите ваш вопрос юристу:", reply_markup=ReplyKeyboardRemove())
        return TYPING
    else:
        await update.message.reply_text(FAQ_RESPONSES.get(question, "Ответ не найден"), reply_markup=legal_faq_kb)
        return FAQ_LEGAL

async def handle_medical_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = update.message.text
    if question == "Назад":
        await update.message.reply_text("Выберите категорию:", reply_markup=help_kb)
        return HELP_TYPE
    elif question == "Консультация врача":
        context.user_data["type"] = "Медицинская - Консультация"
        await update.message.reply_text("Опишите ваш медицинский вопрос:", reply_markup=ReplyKeyboardRemove())
        return TYPING
    else:
        await update.message.reply_text(FAQ_RESPONSES.get(question, "Ответ не найден"), reply_markup=medical_faq_kb)
        return FAQ_MED

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message.text
    request_type = context.user_data.get("type", "Неизвестно")
    
    channel_key = request_type.split()[0]
    chat_id = CHANNELS.get(channel_key, ADMIN_CHAT_ID)
    
    text = f"📩 *{request_type}*\n"
    if "Анонимное" not in request_type:
        text += f"От: @{update.message.from_user.username or 'нет'} (ID: {update.message.from_user.id})\n\n"
    text += msg
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown"
    )
    await update.message.reply_text("✅ Ваше сообщение отправлено!", reply_markup=main_kb)
    return MENU

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_category)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_legal_faq)],
            FAQ_MED: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_medical_faq)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
