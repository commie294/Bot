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

# Каналы
CHANNELS = {
    "Срочная": -100123456789,
    "Анонимные": -100987654321,
    "Юридические": -100111222333,
    "Медицинские": -100444555666
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

# FAQ ответы
FAQ_RESPONSES = {
    "Как сменить документы?": """
В России смена гендерного маркера сейчас возможна только через суд. Это сложный процесс, который редко проходит без хирургических вмешательств — многое зависит от конкретного судьи и региона.

Имя в ЗАГСе могут не позволить сменить, если оно «не соответствует» гендерному маркеру. В редких случаях удаётся выбрать нейтральное имя. Убрать отчество также можно не во всех отделениях — зависит от практики на месте.

Мы можем связать вас с юристами, которые помогут оценить риски и шаги в вашем случае.""",

    "Брак после смены пола": """
После смены юридического пола:
1. Действующий брак автоматически расторгается
2. Новый брак возможен только с партнёром противоположного пола (по документам)
3. В РФ запрещены однополые браки

*В других странах правила отличаются*""",

    "Что такое пропаганда ЛГБТ?": """
Закон о «ЛГБТ-пропаганде» формулируется крайне расплывчато. На практике под него могут подвести:
• Публикации о своём опыте перехода
• Трансфрендли контент
• Упоминание смены пола в СМИ

*Что не запрещено:*
1. Личная переписка
2. Взрослые обсуждения
3. Медицинские материалы""",

    "Женская гормональная терапия": """
**Женская гормональная терапия**

Феминизирующая терапия включает приём эстрогенов и антиандрогенов. В странах СНГ распространены такие препараты:

*Эстрогены:*
• Эстрадиол валерат (инъекции) - через интернет/зарубежные аптеки
• Эстрадиол гель («Дивигель», «Эстрожель») - часто без рецепта
• Таблетки («Прогинова») - высокий риск тромбозов

*Антиандрогены:*
• Ципротерон ацетат («Андрокур») - рецептурный
• Бикалутамид - 25–50 мг/день
• Спиронолактон - 100–200 мг/день

*Важно:*
• Эндокринологи редко выписывают ГТ без смены документов
• Инъекции доступны только неофициально
• Обязательны анализы: эстрадиол, пролактин, печеночные пробы""",

    "Мужская гормональная терапия": """
**Мужская гормональная терапия**

Маскулинизирующая терапия — приём тестостерона:

*Формы:*
• Гели («Андрогель») - иногда без рецепта
• Инъекции (энантат, ципионат, сустанон, небидо) - приобретаются неофициально через форумы среди анаболических стероидов

*Схемы:*
• Гель: 5 г (1 саше) ежедневно
• Инъекции: 50–100 мг/неделю

*Контроль:*
• Тестостерон: 15-30 нмоль/л
• Гематокрит: ≤50%
• ЛГ/ФСГ: около 0""",

    "Где делают операции?": """
*Гендерно-аффирмативные операции:*

**Доступные страны:**
• Таиланд (лучшие хирурги)
• Турция (оптимально по цене)
• Армения, Сербия 

**Требования:**
1. Диагноз F64
2. 12+ месяцев ГТ (для мастэктомии - 6 мес)
3. Консультация хирурга

*Мы можем:*
- Дать контакты проверенных клиник
- Подсказать с подготовкой документов"""
}

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Это бот поддержки. Выберите нужную опцию:",
        reply_markup=main_kb
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if "🆘 Срочная помощь" in choice:
        context.user_data["type"] = "🚨 СРОЧНО - Запрос"
        await update.message.reply_text(
            "Опишите срочную ситуацию (мы ответим в течение 15 минут):",
            reply_markup=ReplyKeyboardRemove()
        )
        return TYPING
    elif "💬 Анонимное сообщение" in choice:
        context.user_data["type"] = "👤 Анонимное сообщение"
        await update.message.reply_text(
            "Напишите сообщение (ваши данные не сохранятся):",
            reply_markup=ReplyKeyboardRemove()
        )
        return TYPING
    elif choice in ["💼 Юридическая помощь", "🏥 Медицинская помощь"]:
        await update.message.reply_text("Выберите категорию:", reply_markup=help_kb)
        return HELP_TYPE
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MENU

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message.text
    request_type = context.user_data.get("type", "Запрос")

    if "СРОЧНО" in request_type:
        chat_id = CHANNELS["Срочная"]
        text = f"🚨 *СРОЧНЫЙ ЗАПРОС*\n\n{msg}"
    elif "Анонимное" in request_type:
        chat_id = CHANNELS["Анонимные"]
        text = f"👤 *АНОНИМНОЕ СООБЩЕНИЕ*\n\n{msg}"
    else:
        chat_id = ADMIN_CHAT_ID
        text = f"📩 *{request_type}*\nОт @{update.message.from_user.username}\n\n{msg}"

    try:
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        await update.message.reply_text("✅ Ваше сообщение отправлено!", reply_markup=main_kb)
    except Exception as e:
        await update.message.reply_text("⚠️ Ошибка отправки. Попробуйте позже.", reply_markup=main_kb)

    return MENU

# Заглушки для недостающих функций
async def help_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Функция в разработке.", reply_markup=main_kb)
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Операция отменена.", reply_markup=main_kb)
    return MENU

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_category)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
