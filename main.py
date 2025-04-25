# -*- coding: utf-8 -*-
import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters as Filters,
    ContextTypes,
    ConversationHandler,
)
import sys
sys.path.append('/data/data/com.termux/files/usr/lib/python3.12/site-packages')

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Настройка логирования
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Состояния диалога
(
    START,
    MAIN_MENU,
    HELP_MENU,
    TYPING,
    FAQ_LEGAL,
    FAQ_MED,
    VOLUNTEER_START,
    VOLUNTEER_NAME,
    VOLUNTEER_REGION,
    VOLUNTEER_HELP_TYPE,
    VOLUNTEER_CONTACT,
) = range(11)

# Константы
BACK_BUTTON = "🔙 Назад"
MAIN_MENU_BUTTONS = [
    ["Попросить о помощи"],
    ["Предложить ресурс", "Стать волонтером"],
    ["Поддержать проект"],
]
HELP_MENU_BUTTONS = [
    ["🆘 Срочная помощь", "💼 Юридическая помощь"],
    ["🏥 Медицинская помощь", "🏠 Жилье/финансы"],
    ["🧠 Психологическая помощь", BACK_BUTTON],
]
LEGAL_FAQ_BUTTONS = [
    ["Как сменить документы?", "Брак после смены пола"],
    ["Что такое пропаганда ЛГБТ?", "Консультация юриста"],
    [BACK_BUTTON],
]
MEDICAL_FAQ_BUTTONS = [
    ["Женская гормональная терапия", "Мужская гормональная терапия"],
    ["Диагноз F64", "Где делают операции?"],
    ["Консультация врача", BACK_BUTTON],
]

# Каналы для пересылки сообщений
CHANNELS = {
    "Срочная": -1002507059500,
    "Анонимные": -1002507059500,
    "Юридические": -1002523489451,
    "Медицинские": -1002507059500,
    "Психологическая помощь": -1002677526813,
    "Предложение ресурса": -1002645097441,
    "Волонтеры Остальные": -1002507059500,
    "Волонтеры Психология": -1002677526813,
    "Волонтеры Юристы": -1002523489451,
    "Волонтеры Инфо": -1002645097441,
}

# Ответы на часто задаваемые вопросы
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

# Сообщения бота
START_MESSAGE = (
    "Привет! Мы — проект «Переход в неположенном месте». Этот бот создан для поддержки трансгендерных людей и их близких в России.\n\n"
    "Здесь вы можете:\n"
    "• 🆘 \\!**Попросить о помощи** в различных ситуациях.\n"
    "• 📚 \\!**Предложить ресурс**, который может быть полезен сообществу.\n"
    "• 💖 \\!**Стать волонтером** и помочь проекту.\n"
    "• 💸 \\!**Поддержать проект**, чтобы мы могли продолжать нашу работу.\n\n"
    "Пожалуйста, выберите нужную опцию:"
)

HELP_MENU_MESSAGE = "Выберите категорию помощи:"
RESOURCE_PROMPT_MESSAGE = "Опишите, какой ресурс вы хотите предложить:"
VOLUNTEER_MESSAGE = (
    "Мы очень рады твоему желанию присоединиться к нашей команде волонтеров! "
    "Твоя помощь может стать неоценимым вкладом в поддержку нашего сообщества.\n\n"
    "Пожалуйста, ответьте на несколько вопросов:"
)
DONATE_MESSAGE = (
    "Ваша поддержка помогает нам продолжать нашу работу и оказывать помощь тем, кто в ней нуждается. "
    "Даже небольшой вклад может сделать большую разницу!\n\n"
    "Вы можете поддержать наш проект следующими способами:\n\n"
    "💖 **Через Boosty:** [Поддержать на Boosty](https://boosty.to/t64/donate)\n\n"
    "💰 **USDT (TRC-20):** `TLTBoXCSifWGBeuiRkxkPtH9M9mfwSf1sf`\n\n"
    "Мы благодарны за любую вашу поддержку!"
)
EMERGENCY_MESSAGE = (
    "⚠️ \\!**ВНИМАНИЕ\\! В экстренной ситуации, угрожающей вашей жизни или здоровью, действуйте немедленно:**\n\n"
    "📞 **Позвоните по номеру 112** (единый номер вызова экстренных оперативных служб на территории РФ).\n\n"
    "**Памятка при звонке в экстренные службы:**\n"
    "1. **Сохраняйте спокойствие** и говорите четко.\n"
    "2. **Сообщите, что случилось** (кратко и ясно).\n"
    "3. **Укажите точный адрес** места происшествия (город, улица, номер дома, этаж, ориентиры).\n"
    "4. **Назовите свою фамилию, имя** (если можете).\n"
    "5. **Отвечайте на вопросы диспетчера**.\n"
    "6. **Не вешайте трубку первым**, пока диспетчер не скажет, что вызов принят.\n\n"
    "Опишите вашу ситуацию кратко, и мы постараемся передать информацию волонтерам для поддержки, но помните, что ответ может быть не мгновенным. **В критической ситуации ваш первый шаг - звонок 112.**"
)

HOUSING_FINANCE_PROMPT = (
    "Пожалуйста, опишите вашу ситуацию подробно, укажите информацию о себе (например, регион, возраст, краткую историю вопроса) и ваши потребности. Обратите внимание, что супер-экстренные случаи (например, угроза безопасности) рассматриваются в приоритетном порядке. Мы постараемся помочь вам в рамках наших возможностей и ресурсов."
)
PSYCHOLOGICAL_HELP_PROMPT = (
    "Опишите ваш запрос и, если у вас есть особые пожелания к специалисту (например, опыт работы с определенными темами), пожалуйста, укажите их."
)
CONSULTATION_PROMPT = "Опишите ваш вопрос. Мы постараемся связать вас со специалистом в ближайшее время."
MESSAGE_SENT_SUCCESS = "✅ Ваше сообщение отправлено!"
MESSAGE_SEND_ERROR = "⚠️ Ошибка отправки: {}. Попробуйте позже."
CANCEL_MESSAGE = "Операция отменена."
BACK_TO_MAIN_MENU = "Вы вернулись в главное меню."
CHOOSE_FROM_MENU = "Пожалуйста, выберите опцию из меню."
CHOOSE_HELP_CATEGORY = "Пожалуйста, выберите опцию из меню помощи."

async def volunteer_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Давайте начнем небольшое интервью. Как вас зовут?")
    return VOLUNTEER_NAME

async def volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["volunteer_name"] = update.message.text
    await update.message.reply_text("Из какого вы региона?")
    return VOLUNTEER_REGION

async def volunteer_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["volunteer_region"] = update.message.text
    keyboard = [
        ["Психологическая помощь"],
        ["Юридические услуги"],
        ["Медицинские услуги"],
        ["Информационные услуги (тексты, модерация)"],
        ["Финансовая поддержка"],
        ["Другое..."],
    ]
    await update.message.reply_text("Какую помощь вы готовы предоставить?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return VOLUNTEER_HELP_TYPE

async def volunteer_help_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["volunteer_help_type"] = update.message.text
    await update.message.reply_text("Пожалуйста, укажите ваш Telegram-ник для связи.")
    return VOLUNTEER_CONTACT

async def volunteer_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["volunteer_contact"] = update.message.text
    volunteer_info = (
        f"Новый потенциальный волонтер:\n"
        f"Имя: {context.user_data.get('volunteer_name', 'не указано')}\n"
        f"Регион: {context.user_data.get('volunteer_region', 'не указано')}\n"
        f"Направление: {context.user_data.get('volunteer_help_type', 'не указано')}\n"
        f"Контакт: @{context.user_data.get('volunteer_contact', 'не указано')}"
    )

    help_type = context.user_data.get("volunteer_help_type")
    target_channel_id = None
    if help_type == "Психологическая помощь":
        target_channel_id = CHANNELS["Волонтеры Психология"]
    elif help_type == "Юридические услуги":
        target_channel_id = CHANNELS["Волонтеры Юристы"]
    elif help_type == "Информационные услуги (тексты, модерация)":
        target_channel_id = CHANNELS["Волонтеры Инфо"]
    elif help_type in ["Медицинские услуги", "Финансовая поддержка", "Другое..."]:
        target_channel_id = CHANNELS["Волонтеры Остальные"]

    if target_channel_id:
        try:
            await context.bot.send_message(chat_id=target_channel_id, text=volunteer_info)
            await update.message.reply_text("Ваша заявка отправлена администраторам соответствующего направления. С вами свяжутся в ближайшее время.", reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
        except Exception as e:
            logger.error(f"Ошибка при отправке информации о волонтере в канал: {e}", exc_info=True)
            await update.message.reply_text("Произошла ошибка при отправке вашей заявки. Пожалуйста, попробуйте позже.", reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    else:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Новый волонтер (неопределенное направление):\n{volunteer_info}") # Отправка админам для обработки (на всякий случай)
        await update.message.reply_text("Ваша заявка отправлена администраторам. С вами свяжутся в ближайшее время.", reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))

    context.user_data.clear() # Очищаем данные интервью
    return MAIN_MENU

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(START_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="MarkdownV2")
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "Попросить о помощи":
        await update.message.reply_text(HELP_MENU_MESSAGE, reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True), parse_mode="MarkdownV2")
        return HELP_MENU
    elif choice == "Предложить ресурс":
        context.user_data["type"] = "💡 Предложение ресурса"
        await update.message.reply_text(RESOURCE_PROMPT_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="MarkdownV2")
        return TYPING
    elif choice == "Стать волонтером":
        return await volunteer_start(update, context) # Запускаем интервью
    elif choice == "Поддержать проект":
        await update.message.reply_text(DONATE_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="MarkdownV2", disable_web_page_preview=True)
        return TYPING
    else:
        await update.message.reply_text(CHOOSE_FROM_MENU, parse_mode="MarkdownV2")
        return MAIN_MENU

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "🆘 Срочная помощь":
        await update.message.reply_text(EMERGENCY_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), disable_web_page_preview=True, parse_mode="MarkdownV2")
        context.user_data["type"] = "Срочная"
        return TYPING
    elif choice == "💼 Юридическая помощь":
        await update.message.reply_text("Выберите вопрос:", reply_markup=ReplyKeyboardMarkup(LEGAL_FAQ_BUTTONS, resize_keyboard=True), parse_mode="MarkdownV2")
        return FAQ_LEGAL
    elif choice == "🏥 Медицинская помощь":
        context.user_data["type"] = "Медицинская"
        await update.message.reply_text("Выберите вопрос:", reply_markup=ReplyKeyboardMarkup(MEDICAL_FAQ_BUTTONS, resize_keyboard=True), parse_mode="MarkdownV2")
        return FAQ_MED
    elif choice == "🧠 Психологическая помощь":
        context.user_data["type"] = "Психологическая помощь"
        await update.message.reply_text(PSYCHOLOGICAL_HELP_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="MarkdownV2")
        return TYPING
    elif choice == "🏠 Жилье/финансы":
        context.user_data["type"] = "Срочная"  # Или "Остальное"
        await update.message.reply_text(HOUSING_FINANCE_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="MarkdownV2")
        return TYPING
    elif choice == BACK_BUTTON:
        return await start(update, context)
    else:
        await update.message.reply_text(CHOOSE_HELP_CATEGORY, parse_mode="MarkdownV2")
        return HELP_MENU

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message_text = update.message.text
    if message_text == BACK_BUTTON:
        await update.message.reply_text(BACK_TO_MAIN_MENU, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="MarkdownV2")
        return MAIN_MENU

    request_type = context.user_data.get("type", "Запрос")
    username = update.message.from_user.username or "нет"
    forward_text = f"📩 {request_type}\nОт @{username}\n\n{message_text}"

    target_channel_id = ADMIN_CHAT_ID  # По умолчанию отправляем админу

    if "Срочная" in request_type:
        target_channel_id = CHANNELS["Срочная"]
        # Отправляем уведомление администраторам
        admin_notification = f"🚨 НОВЫЙ СРОЧНЫЙ ЗАПРОС!\nОт пользователя: @{username}\nСообщение: {message_text}"
        try:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification, parse_mode="MarkdownV2")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления администратору о срочном запросе: {e}", exc_info=True)
    elif "Анонимное" in request_type:
        target_channel_id = CHANNELS["Анонимные"]
    elif "Юридическая" in request_type:
        target_channel_id = CHANNELS["Юридические"]
    elif "Медицинская" in request_type:
        target_channel_id = CHANNELS["Медицинские"]
    elif "Психологическая помощь" in request_type:
        target_channel_id = CHANNELS["Психологическая помощь"]
    elif "Предложение ресурса" in request_type:
        target_channel_id = CHANNELS["Предложение ресурса"]
    elif "Юридическая консультация" in request_type:
        target_channel_id = CHANNELS["Юридические"]
    elif "Медицинская консультация" in request_type:
        target_channel_id = CHANNELS["Медицинские"]

    try:
        await context.bot.send_message(chat_id=target_channel_id, text=forward_text, parse_mode="MarkdownV2")
        await update.message.reply_text(MESSAGE_SENT_SUCCESS, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}", exc_info=True)
        await update.message.reply_text(MESSAGE_SEND_ERROR.format(e), reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="MarkdownV2")

    return MAIN_MENU

async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, faq_type: str) -> int:
    question = update.message.text
    if question == BACK_BUTTON:
        await update.message.reply_text(HELP_MENU_MESSAGE, reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True), parse_mode="MarkdownV2")
        return HELP_MENU
    elif "Консультация" in question:
        context.user_data["type"] = f"{faq_type.capitalize()} консультация"
        await update.message.reply_text(CONSULTATION_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="MarkdownV2")
        return TYPING
    else:
        response = FAQ_RESPONSES.get(question, "Ответ не найден")
        await update.message.reply_text(response, parse_mode="MarkdownV2")
        return FAQ_LEGAL if faq_type == "юридическая" else FAQ_MED

async def handle_legal_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_faq(update, context, "юридическая")

async def handle_medical_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_faq(update, context, "медицинская")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="MarkdownV2")
    return START

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [CommandHandler("start", start)],
            MAIN_MENU: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, main_menu)],
            HELP_MENU: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, help_menu)],
            FAQ_LEGAL: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, handle_legal_faq)],
            FAQ_MED: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, handle_medical_faq)],
            TYPING: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, handle_message)],
            VOLUNTEER_START: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_start)],
            VOLUNTEER_NAME: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_name)],
            VOLUNTEER_REGION: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_region)],
            VOLUNTEER_HELP_TYPE: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_help_type)],
            VOLUNTEER_CONTACT: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    # Запуск бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
