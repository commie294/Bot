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

# Состояния
START, MENU, HELP_TYPE, TYPING, FAQ_LEGAL, FAQ_MED = range(6)

# Каналы
CHANNELS = {
    "Срочная": -100123456789,
    "Анонимные": -100987654321,
    "Юридические": -100111222333,
    "Медицинские": -100444555666
}

# Ответы FAQ
FAQ_RESPONSES = {
    # Юридические вопросы
    "Как сменить документы?": """
В России смена гендерного маркера сейчас возможна только через суд. Это сложный процесс, который редко проходит без хирургических вмешательств — многое зависит от конкретного судьи и региона.

Имя в ЗАГСе могут не позволить сменить, если оно «не соответствует» гендерному маркеру. В редких случаях удаётся выбрать нейтральное имя. Убрать отчество также можно не во всех отделениях — зависит от практики на месте.

Мы можем связать вас с юристами, которые помогут оценить риски и шаги в вашем случае.""",

    "Что такое пропаганда ЛГБТ?": """
Закон о «ЛГБТ-пропаганде» формулируется крайне расплывчато. На практике под него могут подвести:
• Публикации о своём опыте перехода
• Трансфрендли контент
• Упоминание смены пола в СМИ

*Что не запрещено:*
1. Личная переписка
2. Взрослые обсуждения
3. Медицинские материалы""",

    "Брак после смены пола": """
После смены юридического пола:
1. Действующий брак автоматически расторгается
2. Новый брак возможен только с партнёром противоположного пола (по документам)
3. В РФ запрещены однополые браки""",

    # Медицинские вопросы
    "Женская гормональная терапия": """
**Женская гормональная терапия**

Феминизирующая терапия включает приём эстрогенов и антиандрогенов.

*Эстрогены:*
• Эстрадиол валерат (инъекции)
• Эстрадиол гель: «Дивигель», «Эстрожель» (иногда без рецепта, продаются за рубежом онлайн)
• Таблетки: «Прогинова» (меньше используется из-за риска тромбозов)

*Антиандрогены:*
• Ципротерон ацетат (Андрокур), Спиронолактон, Бикалутамид (25–50 мг/день)

*Схема:*
- Гель — 1–2 мг/день (в аптеке без рецепта)
- Инъекции — 5–10 мг каждые 7–10 дней (продаются за рубежом онлайн)

**Важно:**
• Эндокринологи часто отказываются выдавать рецепты без смены гендерного маркера
• Препараты приобретаются в интернете
• Анализы сдавайте в частных клиниках""",

    "Мужская гормональная терапия": """
**Мужская гормональная терапия**

Маскулинизирующая терапия — приём тестостерона.
• Андрогель: 5 г/день (в аптеке без рецепта)
• Инъекции: 50–100 мг/нед (можно найти в даркнет форумах среди анаболических стероидов)

**Важно:**
• Официальное назначение возможно только после смены документов
• Контролируйте гематокрит и печеночные пробы
• Анализы: тестостерон 15-30 нмоль/л""",

    "Где делают операции?": """
В РФ официально такие операции не проводят. Доступны в:
• Таиланде (лучшие хирурги)
• Турции (оптимально по цене)
• Армении, Сербии (бюджетные варианты)

**Требования:**
1. Справка F64
2. 12+ месяцев ГТ (для мастэктомии — 6 мес)
3. Консультация хирурга""",

    "Диагноз F64": """
F64 — код в МКБ-10 для гендерной дисфории. В РФ:
• Дает право на смену документов через суд
• Не дает доступа к гормонам
• Требуется для операций за рубежом

*Как получить:*
1. Консультация психиатра
2. Обследование (2+ визита)
3. Заключение"""
}

# Клавиатуры
main_kb = ReplyKeyboardMarkup([
    ["🆘 Срочная помощь", "💼 Юридическая помощь"],
    ["🏥 Медицинская помощь", "💬 Анонимное сообщение"],
    ["📚 Ресурсы", "💖 Стать волонтером"],
    ["💸 Поддержать проект"]
], resize_keyboard=True)

help_kb = ReplyKeyboardMarkup([
    ["🆘 Срочная помощь", "💼 Юридическая"],
    ["🏥 Медицинская", "🏠 Жилье/финансы"],
    ["🧠 Психологическая", "🔙 Назад"]
], resize_keyboard=True)

legal_faq_kb = ReplyKeyboardMarkup([
    ["Как сменить документы?", "Брак после смены пола"],
    ["Что такое пропаганда ЛГБТ?", "Консультация юриста"],
    ["🔙 Назад"]
], resize_keyboard=True)

medical_faq_kb = ReplyKeyboardMarkup([
    ["Женская гормональная терапия", "Мужская гормональная терапия"],
    ["Диагноз F64", "Где делают операции?"],
    ["Консультация врача", "🔙 Назад"]
], resize_keyboard=True)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Привет! Это бот поддержки. Выберите нужную опцию:",
        reply_markup=main_kb
    )
    return MENU

# Меню
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if "🆘 Срочная помощь" in choice:
        context.user_data["type"] = "🚨 СРОЧНО - Запрос"
        await update.message.reply_text(
            "Опишите срочную ситуацию (мы ответим в течение 15 минут):",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
        )
        return TYPING
    elif "💬 Анонимное сообщение" in choice:
        context.user_data["type"] = "👤 Анонимное сообщение"
        await update.message.reply_text(
            "Напишите сообщение (ваши данные не сохранятся):",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
        )
        return TYPING
    elif choice == "💼 Юридическая помощь":
        await update.message.reply_text("Выберите вопрос:", reply_markup=legal_faq_kb)
        return FAQ_LEGAL
    elif choice == "🏥 Медицинская помощь":
        await update.message.reply_text("Выберите вопрос:", reply_markup=medical_faq_kb)
        return FAQ_MED
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MENU

# Категории помощи
async def help_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = update.message.text

    if category == "💼 Юридическая":
        await update.message.reply_text(
            "Выберите вопрос или нажмите «Консультация юриста»:",
            reply_markup=legal_faq_kb
        )
        return FAQ_LEGAL

    elif category == "🏥 Медицинская":
        await update.message.reply_text(
            "Выберите вопрос или нажмите «Консультация врача»:",
            reply_markup=medical_faq_kb
        )
        return FAQ_MED

    elif category in ["🏠 Жилье/финансы", "🧠 Психологическая"]:
        context.user_data["type"] = category
        await update.message.reply_text(
            "Опишите ваш запрос:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
        )
        return TYPING

    elif category == "🔙 Назад":
        return await start(update, context)

    else:
        await update.message.reply_text("Выберите корректную категорию.")
        return HELP_TYPE

# Ответы FAQ
async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str) -> int:
    question = update.message.text
    if question == "🔙 Назад":
        await update.message.reply_text("Выберите категорию:", reply_markup=help_kb)
        return HELP_TYPE
    elif "Консультация" in question:
        context.user_data["type"] = f"{mode} - Консультация"
        await update.message.reply_text("Опишите ваш вопрос:", reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True))
        return TYPING
    else:
        await update.message.reply_text(FAQ_RESPONSES.get(question, "Ответ не найден"), parse_mode="Markdown")
        return FAQ_LEGAL if mode == "Юридическая" else FAQ_MED

async def handle_legal_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_faq(update, context, "Юридическая")

async def handle_medical_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_faq(update, context, "Медицинская")

# Приём сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message.text
    if msg == "🔙 Назад":
        await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_kb)
        return MENU

    request_type = context.user_data.get("type", "Запрос")
    username = update.message.from_user.username or "нет"

    if "СРОЧНО" in request_type:
        chat_id = CHANNELS["Срочная"]
    elif "Анонимное" in request_type:
        chat_id = CHANNELS["Анонимные"]
    elif "Юридическая" in request_type:
        chat_id = CHANNELS["Юридические"]
    elif "Медицинская" in request_type:
        chat_id = CHANNELS["Медицинские"]
    else:
        chat_id = ADMIN_CHAT_ID

    text = f"📩 *{request_type}*\nОт @{username}\n\n{msg}"

    try:
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        await update.message.reply_text("✅ Ваше сообщение отправлено!", reply_markup=main_kb)
    except:
        await update.message.reply_text("⚠️ Ошибка отправки. Попробуйте позже.", reply_markup=main_kb)

    return MENU

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Операция отменена.", reply_markup=main_kb)
    return MENU

# Запуск
def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_category)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_legal_faq)],
            FAQ_MED: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_medical_faq)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
