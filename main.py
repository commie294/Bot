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
START, MAIN_MENU, HELP_MENU, TYPING, FAQ_LEGAL, FAQ_MED = range(6)

# Каналы
CHANNELS = {
    "Срочная": -1002507059500,  # t64_gen (остальное)
    "Анонимные": -1002507059500, # t64_gen (остальное) - пока используем этот же, если нет отдельного
    "Юридические": -1002523489451, # t64_legal
    "Медицинские": -1002507059500, # t64_gen (остальное) - пока используем этот же, если нет отдельного
    "Психологическая помощь": -1002677526813, # t64_psych
    "Предложение ресурса": -1002645097441 # t4_misc
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

Феминизирующая терапия включает приём эстрогенов и антиандрогенов. Врачи в РФ обычно не выдают рецепты на эти препараты без официальной смены гендерного маркера в документах. Анализы для контроля терапии рекомендуется проводить самостоятельно в частных клиниках.

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
• Официальное назначение возможно только после смены документов
• Препараты приобретаются в интернете
• Анализы сдавайте в частных клиниках""",

    "Мужская гормональная терапия": """
**Мужская гормональная терапия**

Маскулинизирующая терапия — приём тестостерона. Врачи в РФ обычно не выдают рецепты на эти препараты без официальной смены гендерного маркера в документах. Анализы для контроля терапии рекомендуется проводить самостоятельно в частных клиниках.
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
F64 — это код в Международной классификации болезней 10-го пересмотра (МКБ-10), обозначающий транссексуализм или гендерную дисфорию. В Российской Федерации сам по себе диагноз F64 **не дает никаких юридических прав**, кроме того, что он может быть основанием для обращения в суд с целью смены гендерного маркера в документах. Также наличие диагноза F64 является одним из обязательных требований для проведения хирургических операций по коррекции пола за рубежом."""
}

# Клавиатуры
main_kb = ReplyKeyboardMarkup([
    ["Попросить о помощи"],
    ["Предложить ресурс", "Стать волонтером"],
    ["Поддержать проект"]
], resize_keyboard=True)

help_kb = ReplyKeyboardMarkup([
    ["🆘 Срочная помощь", "💼 Юридическая помощь"],
    ["🏥 Медицинская помощь", "🏠 Жилье/финансы"],
    ["🧠 Психологическая помощь", "🔙 Назад"]
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
        "Привет! Мы — проект «Переход в неположенном месте». Этот бот создан для поддержки трансгендерных людей и их близких в России.\n\n"
        "Здесь вы можете:\n"
        "• 🆘 **Попросить о помощи** в различных ситуациях.\n"
        "• 📚 **Предложить ресурс**, который может быть полезен сообществу.\n"
        "• 💖 **Стать волонтером** и помочь проекту.\n"
        "• 💸 **Поддержать проект**, чтобы мы могли продолжать нашу работу.\n\n"
        "Пожалуйста, выберите нужную опцию:",
        reply_markup=main_kb
    )
    return MAIN_MENU

# Главное меню
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "Попросить о помощи":
        await update.message.reply_text("Выберите категорию помощи:", reply_markup=help_kb)
        return HELP_MENU
    elif choice == "Предложить ресурс":
        context.user_data["type"] = "💡 Предложение ресурса"
        await update.message.reply_text("Опишите, какой ресурс вы хотите предложить:", reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True))
        return TYPING
    elif choice == "Стать волонтером":
        volunteer_text = (
            "Мы очень рады твоему желанию присоединиться к нашей команде волонтеров! "
            "Твоя помощь может стать неоценимым вкладом в поддержку нашего сообщества.\n\n"
            "Пожалуйста, заполни эту форму, чтобы мы могли узнать тебя лучше и предложить подходящие задачи:\n"
            "[Форма для волонтеров](https://docs.google.com/forms/d/1kFHSQ05lQyL6s7WDdqTqqY-Il6La3Sehhj_1iVTNgus/edit)\n\n"
            "Мы свяжемся с тобой в ближайшее время после получения твоей заявки. "
            "Спасибо за твою готовность помогать!"
        )
        await update.message.reply_text(
            volunteer_text,
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return TYPING
    elif choice == "Поддержать проект":
        donate_text = (
            "Ваша поддержка помогает нам продолжать нашу работу и оказывать помощь тем, кто в ней нуждается. "
            "Даже небольшой вклад может сделать большую разницу!\n\n"
            "Вы можете поддержать наш проект следующими способами:\n\n"
            "💖 **Через Boosty:** [Поддержать на Boosty](https://boosty.to/t64/donate)\n\n"
            "💰 **USDT (TRC-20):** `TLTBoXCSifWGBeuiRkxkPtH9M9mfwSf1sf`\n\n"
            "Мы благодарны за любую вашу поддержку!"
        )
        await update.message.reply_text(
            donate_text,
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return TYPING
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MAIN_MENU

# Меню помощи
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "🆘 Срочная помощь":
        await update.message.reply_text(
            "Опишите срочную ситуацию (мы постараемся ответить в течение 15 минут). Пожалуйста, помните, что мы не являемся экстренной службой. В критических ситуациях, угрожающих жизни или здоровью, немедленно обратитесь в соответствующие службы экстренного реагирования или на телефон доверия.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
        )
        return TYPING
    elif choice == "💼 Юридическая помощь":
        await update.message.reply_text("Выберите вопрос:", reply_markup=legal_faq_kb)
        return FAQ_LEGAL
    elif choice == "🏥 Медицинская помощь":
        await update.message.reply_text("Выберите вопрос:", reply_markup=medical_faq_kb)
        return FAQ_MED
    elif choice == "🧠 Психологическая помощь":
        await update.message.reply_text(
            "Опишите ваш запрос и, если у вас есть особые пожелания к специалисту (например, опыт работы с определенными темами), пожалуйста, укажите их.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
        )
        return TYPING
    elif choice == "🏠 Жилье/финансы":
        await update.message.reply_text(
            "Пожалуйста, опишите вашу ситуацию подробно, укажите информацию о себе (например, регион, возраст, краткую историю вопроса) и ваши потребности. Обратите внимание, что супер-экстренные случаи (например, угроза безопасности) рассматриваются в приоритетном порядке. Мы постараемся помочь вам в рамках наших возможностей и ресурсов.",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
        )
        return TYPING
    elif choice == "🔙 Назад":
        return await start(update, context)
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню помощи.")
        return HELP_MENU

# Ответы FAQ
async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str) -> int:
    question = update.message.text
    if question == "🔙 Назад":
        await update.message.reply_text("Выберите категорию помощи:", reply_markup=help_kb)
        return HELP_MENU
    elif "Консультация" in question:
        channel_type = "Юридическая" if mode == "Юридическая" else "Медицинская"
        context.user_data["type"] = f"{channel_type} консультация"
        await update.message.reply_text("Опишите ваш вопрос. Мы постараемся связать вас со специалистом в ближайшее время.", reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True))
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
        return MAIN_MENU

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
    elif "Психологическая помощь" in request_type:
        chat_id = CHANNELS["Психологическая помощь"]
    elif "Предложение ресурса" in request_type:
        chat_id = CHANNELS["Предложение ресурса"]
    else:
        chat_id = ADMIN_CHAT_ID

    text = f"📩 *{request_type}*\nОт @{username}\n\n{msg}"

    try:
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        await update.message.reply_text("✅ Ваше сообщение отправлено!", reply_markup=main_kb)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка отправки: {e}. Попробуйте позже.", reply_markup=main_kb)
        # Желательно здесь добавить логирование ошибки для отладки

    return MAIN_MENU

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Операция отменена.", reply_markup=main_kb)
    return MAIN_MENU

# Запуск
def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_menu)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_legal_faq)],
            FAQ_MED: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_medical_faq)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(conv_handler)
