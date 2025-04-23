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

# Предупреждения
WARNING_URGENT = """
🚨 *Срочная помощь* 

Важно:
1. Если есть угроза жизни - сразу звоните в экстренные службы
2. Мы отвечаем в течение 1-3 часов
3. Для анонимности не указывайте личные данные

Напишите кратко:
• Что произошло
• Где вы находитесь (город/страна)
• Какая помощь нужна
"""

WARNING_HOUSING = """
🏠 *Жильё и финансовая помощь*

Условия:
1. Помощь доступна только в некоторых регионах
2. Жильё предоставляется на 1-3 месяца
3. Приоритет - опасные ситуации (угроза жизни, насилие)

Опишите:
• Вашу ситуацию
• Город проживания
• Срок, на который нужно жильё
"""

# Ответы на FAQ
FAQ_RESPONSES = {
    # Юридические вопросы
    "Как сменить документы?": """Полный текст ответа...""",
    "Что такое пропаганда ЛГБТ?": """Полный текст ответа...""",
    
    # Медицинские вопросы
    "Женская ГТ": """Полный текст ответа...""",
    "Мужская ГТ": """Полный текст ответа...""",
    "Диагноз F64": """Полный текст ответа..."""
}

# Клавиатуры
main_kb = ReplyKeyboardMarkup([
    ["Срочная помощь", "Юридическая помощь"],
    ["Медицинская помощь", "Психологическая поддержка"],
    ["Жильё и финансы", "Анонимное сообщение"],
    ["Ресурсы"]
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
    ["Диагноз F64", "Консультация врача"],
    ["Назад"]
], resize_keyboard=True)

# ID каналов
CHANNELS = {
    "Юридическая": -100123456,
    "Психологическая": -100789012,
    "Медицинская": -100345678,
    "Жильё и финансы": -100901234,
    "Срочная": -100901234,
    "Анонимное сообщение": -100567890,
    "Ресурсы": -100567890
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Это бот поддержки. Выберите нужную категорию:",
        reply_markup=main_kb
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "Срочная помощь":
        context.user_data["type"] = "СРОЧНО - Запрос"
        await update.message.reply_text(
            WARNING_URGENT,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return TYPING
    elif choice == "Жильё и финансы":
        await update.message.reply_text(
            WARNING_HOUSING,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["type"] = "Жильё/финансы"
        return TYPING
    elif choice in ["Юридическая помощь", "Медицинская помощь"]:
        await update.message.reply_text("Выберите категорию:", reply_markup=help_kb)
        return HELP_TYPE
    # Остальные обработчики...

async def help_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = update.message.text
    if category == "Юридическая":
        await update.message.reply_text("Выберите вопрос:", reply_markup=legal_faq_kb)
        return FAQ_LEGAL
    elif category == "Медицинская":
        await update.message.reply_text("Выберите вопрос:", reply_markup=medical_faq_kb)
        return FAQ_MED
    # Остальные категории...

async def handle_legal_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = update.message.text
    if question == "Назад":
        await update.message.reply_text("Выберите категорию:", reply_markup=help_kb)
        return HELP_TYPE
    # Обработка юридических FAQ...

async def handle_medical_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = update.message.text
    if question == "Назад":
        await update.message.reply_text("Выберите категорию:", reply_markup=help_kb)
        return HELP_TYPE
    # Обработка медицинских FAQ...

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message.text
    request_type = context.user_data.get("type", "Неизвестно")
    
    # Определение канала
    channel_key = request_type.split()[0]
    if "СРОЧНО" in request_type:
        channel_key = "Срочная"
    chat_id = CHANNELS.get(channel_key, ADMIN_CHAT_ID)
    
    # Формирование сообщения
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
