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
    ANONYMOUS_MESSAGE,
) = range(12)

# Константы
BACK_BUTTON = "🔙 Назад"
MAIN_MENU_BUTTONS = [
    ["Попросить о помощи"],
    ["Предложить ресурс", "Стать волонтером"],
    ["Поддержать проект", "Анонимное сообщение"],
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
    "Анонимные сообщения": -1002645097441, # Канал для анонимных сообщений
}

# Ответы на часто задаваемые вопросы
FAQ_RESPONSES = {
    "Как сменить документы?": """В России смена гендерного маркера сейчас возможна только через суд. Это сложный процесс, который редко проходит без хирургических вмешательств — многое зависит от конкретного судьи и региона.\n\nИмя в ЗАГСе могут не позволить сменить, если оно «не соответствует» гендерному маркеру. В редких случаях удаётся выбрать нейтральное имя. Убрать отчество также можно не во всех отделениях — зависит от практики на месте.\n\nМы можем связать вас с юристами, которые помогут оценить риски и шаги в вашем случае.""",
    "Что такое пропаганда ЛГБТ?": """Закон о «ЛГБТ-пропаганде» формулируется крайне расплывчато. На практике под него могут подвести:\n• Публикации о своём опыте перехода\n• Трансфрендли контент\n• Упоминание смены пола в СМИ\n\n*Что не запрещено:*\n1. Личная переписка\n2. Взрослые обсуждения\n3. Медицинские материалы""",
    "Брак после смены пола": """После смены юридического пола:\n1. Действующий брак автоматически расторгается\n2. Новый брак возможен только с партнёром противоположного пола (по документам)\n3. В РФ запрещены однополые браки""",
    "Женская гормональная терапия": """**Женская гормональная терапия**\n\nФеминизирующая терапия включает приём эстрогенов и антиандрогенов. Врачи в РФ обычно не выдают рецепты на эти препараты без официальной смены гендерного маркера в документах. Анализы для контроля терапии рекомендуется проводить самостоятельно в частных клиниках.\n\n*Эстрогены:*\n• Эстрадиол валерат (инъекции)\n• Эстрадиол гель: «Дивигель», «Эстрожель» (иногда без рецепта, продаются за рубежом онлайн)\n• Таблетки: «Прогинова» (меньше используется из-за риска тромбозов)\n\n*Антиандрогены:*\n• Ципротерон ацетат (Андрокур), Спиронолактон, Бикалутамид (25–50 мг/день)\n\n*Схема:*\n- Гель — 1–2 мг/день (в аптеке без рецепта)\n- Инъекции — 5–10 мг каждые 7–10 дней (продаются за рубежом онлайн)\n\n**Важно:**\n• Официальное назначение возможно только после смены документов\n• Препараты приобретаются в интернете\n• Анализы сдавайте в частных клиниках""",
    "Мужская гормональная терапия": """**Мужская гормональная терапия**\n\nМаскулинизирующая терапия — приём тестостерона. Врачи в РФ обычно не выдают рецепты на эти препараты без официальной смены гендерного маркера в документах. Анализы для контроля терапии рекомендуется проводить самостоятельно в частных клиниках.\n• Андрогель: 5 г/день (в аптеке без рецепта)\n• Инъекции: 50–100 мг/нед (можно найти в даркнет форумах среди анаболических стероидов)\n\n**Важно:**\n• Официальное назначение возможно только после смены документов\n• Контролируйте гематокрит и печеночные пробы\n• Анализы: тестостерон 15-30 нмоль/л""",
    "Где делают операции?": """В РФ официально такие операции не проводят. Доступны в:\n• Таиланде (лучшие хирурги)\n• Турции (оптимально по цене)\n• Армении, Сербии (бюджетные варианты)\n\n**Требования:**\n1. Справка F64\n2. 12+ месяцев ГТ (для мастэктомии — 6 мес)\n3. Консультация хирурга""",
    "Диагноз F64": """F64 — это код в Международной классификации болезней 10-го пересмотра (МКБ-10), обозначающий транссексуализм или гендерную дисфорию. В Российской Федерации сам по себе диагноз F64 **не дает никаких юридических прав**, кроме того, что он может быть основанием для обращения в суд с целью смены гендерного маркера в документах. Также наличие диагноза F64 является одним из обязательных требований для проведения хирургических операций по коррекции пола за рубежом."""
}

# Сообщения бота
START_MESSAGE = (
    "Привет! Мы — проект «Переход в неположенном месте». Этот бот создан для поддержки трансгендерных людей и их близких в России.\n\n"
    "Здесь вы можете:\n"
    "* 🆘 **Попросить о помощи** в различных ситуациях.\n"
    "* 📚 **Предложить ресурс**, который может быть полезен сообществу.\n"
    "* 💖 **Стать волонтером** и помочь проекту.\n"
    "* 💸 **Поддержать проект**, чтобы мы могли продолжать нашу работу.\n"
    "* 🤫 **Написать анонимное сообщение**.\n\n"
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
    "💖 **Через Boosty:** [Поддержать на Boosty](https://boosty.to/t64/donate)\n\n"
    "💰 **USDT (TRC-20):** `TLTBoXCSifWGBeuiRkxkPtH9M9mfwSf1sf`\n\n"
    "Мы благодарны за любую вашу поддержку!"
)
EMERGENCY_MESSAGE = (
    "⚠️ **ВНИМАНИЕ! В экстренной ситуации, угрожающей вашей жизни или здоровью, действуйте немедленно:**\n\n"
    "📞 **Позвоните по номеру 112** (единый номер вызова экстренных оперативных служб на территории РФ).\n\n"
    "**Памятка при звонке в экстренные службы:**\n"
    "1. Сохраняйте спокойствие и говорите четко.\n"
    "2. Сообщите, что случилось (кратко и ясно).\n"
    "3. Укажите точный адрес места происшествия (город, улица, номер дома, этаж, ориентиры).\n"
    "4. Назовите свою фамилию, имя (если можете).\n"
    "5. Отвечайте на вопросы диспетчера.\n"
    "6. Не вешайте трубку первым, пока диспетчер не скажет, что вызов принят.\n\n"
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
    try:
        await update.message.reply_text("Давайте начнем небольшое интервью. Как вас зовут?")
        return VOLUNTEER_NAME
    except Exception as e:
        logger.error(f"Ошибка в volunteer_start: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
        return MAIN_MENU

async def volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["volunteer_name"] = update.message.text
        await update.message.reply_text("Из какого вы региона?")
        return VOLUNTEER_REGION
    except Exception as e:
        logger.error(f"Ошибка в volunteer_name: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
        return MAIN_MENU

async def volunteer_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
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
    except Exception as e:
        logger.error(f"Ошибка в volunteer_region: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
        return MAIN_MENU

async def volunteer_help_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["volunteer_help_type"] = update.message.text
        await update.message.reply_text("Пожалуйста, укажите ваш Telegram-ник для связи.")
        return VOLUNTEER_CONTACT
    except Exception as e:
        logger.error(f"Ошибка в volunteer_help_type: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
        return MAIN_MENU

async def volunteer_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["volunteer_contact"] = update.message.text
        volunteer_name = context.user_data.get('volunteer_name', 'не указано')
        volunteer_region = context.user_data.get('volunteer_region', 'не указано')
        volunteer_help_type = context.user_data.get('volunteer_help_type', 'не указано')
        volunteer_contact_info = context.user_data.get('volunteer_contact', 'не указано')
        user_id = update.message.from_user.id

        volunteer_info = (
            f"Новый потенциальный волонтер:\n"
            f"Имя: {volunteer_name}\n"
            f"Регион: {volunteer_region}\n"
            f"Направление: {volunteer_help_type}\n"
            f"Контакт: {volunteer_contact_info}\n"
            f"ID пользователя: {user_id}"
        )

        target_admin_channel_id = -4691654032 # ID канала для волонтеров

        await context.bot.send_message(chat_id=target_admin_channel_id, text=volunteer_info)

        # Определяем ссылки на группы
        group_link = None
        if volunteer_help_type == "Психологическая помощь":
            group_link = "https://t.me/+_0BKLwTgVX85ZTZi"
        elif volunteer_help_type == "Юридические услуги":
            group_link = "https://t.me/+aoZhc-rYfAkyMGY6"
        elif volunteer_help_type == "Информационные услуги (тексты, модерация)":
            group_link = "https://t.me/+nz2iA2Rzq740MDZi"
        elif volunteer_help_type in ["Медицинские услуги", "Финансовая поддержка", "Другое..."]:
            group_link = "https://t.me/+hXllFVRn0hc0MTcy" # Ссылка на "Остальное"

        general_admin_link = "https://t.me/+kUJeFUF3088wZDZi" # Ссылка на общий админ-чат

        if group_link:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"Спасибо за вашу заявку! Мы получили вашу информацию и свяжемся с вами в ближайшее время.\n\n"
                         f"Присоединяйтесь к нашей волонтерской группе по направлению '{volunteer_help_type}': {group_link}\n\n"
                         f"Также рекомендуем присоединиться к общему чату администраторов и волонтеров: {general_admin_link}",
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение волонтеру {user_id}: {e}", exc_info=True)
                await update.message.reply_text("Спасибо! Ваша информация передана. Мы свяжемся с вами при необходимости. (Не удалось отправить ссылки на группы в личные сообщения)", reply_markup=ReplyKeyboardMarkup([["🔙 Назад в главное меню"]], resize_keyboard=True), parse_mode="Markdown")
                context.user_data.clear()
                return MAIN_MENU
        else:
            await update.message.reply_text("Спасибо! Ваша информация передана. Мы свяжемся с вами при необходимости.", reply_markup=ReplyKeyboardMarkup([["🔙 Назад в главное меню"]], resize_keyboard=True), parse_mode="Markdown")

        context.user_data.clear() # Очищаем данные интервью
        return MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в volunteer_contact: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
        return MAIN_MENU

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data.clear()
        await update.message.reply_text(START_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
        return MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в start: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
        return START

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "Попросить о помощи":
            await update.message.reply_text(HELP_MENU_MESSAGE, reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
            return HELP_MENU
        elif choice == "Предложить ресурс":
            await update.message.reply_text(RESOURCE_PROMPT_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="Markdown")
            return TYPING
        elif choice == "Стать волонтером":
            return await volunteer_start(update, context) # Запускаем интервью
        elif choice == "Поддержать проект":
            await update.message.reply_text(DONATE_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="Markdown", disable_web_page_preview=True)
            return TYPING
        elif choice == "Анонимное сообщение":
            await update.message.reply_text("Пожалуйста, напишите ваше анонимное сообщение:", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="Markdown")
            context.user_data["type"] = "Анонимное сообщение"
            return TYPING
        else:
            await update.message.reply_text(CHOOSE_FROM_MENU, parse_mode="Markdown")
            return MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в main_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
        return MAIN_MENU

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "🆘 Срочная помощь":
            await update.message.reply_text(EMERGENCY_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), disable_web_page_preview=True, parse_mode="Markdown")
            context.user_data["type"] = "Срочная"
            return TYPING
        elif choice == "💼 Юридическая помощь":
            await update.message.reply_text("Выберите вопрос:", reply_markup=ReplyKeyboardMarkup(LEGAL_FAQ_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
            return FAQ_LEGAL
        elif choice == "🏥 Медицинская помощь":
            context.user_data["type"] = "Медицинская"
            await update.message.reply_text("Выберите вопрос:", reply_markup=ReplyKeyboardMarkup(MEDICAL_FAQ_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
            return FAQ_MED
        elif choice == "🧠 Психологическая помощь":
            context.user_data["type"] = "Психологическая помощь"
            await update.message.reply_text(PSYCHOLOGICAL_HELP_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="Markdown")
            return TYPING
        elif choice == "🏠 Жилье/финансы":
            context.user_data["type"] = "Срочная"  # Или "Остальное"
            await update.message.reply_text(HOUSING_FINANCE_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="Markdown")
            return TYPING
        elif choice == BACK_BUTTON:
            return await start(update, context)
        else:
            await update.message.reply_text(CHOOSE_HELP_CATEGORY, parse_mode="Markdown")
            return HELP_MENU
    except Exception as e:
        logger.error(f"Ошибка в help_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
        return HELP_MENU

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        message_text = update.message.text
        if message_text == BACK_BUTTON:
            await update.message.reply_text(BACK_TO_MAIN_MENU, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
            return MAIN_MENU

        request_type = context.user_data.get("type", "Запрос")
        username = update.message.from_user.username or "нет"
        forward_text = f"📩 {request_type}\nОт @{username}\n\n{message_text}"
        anonymous_text = f"🤫 Анонимное сообщение:\n\n{message_text}"

        target_channel_id = ADMIN_CHAT_ID  # По умолчанию отправляем админу

        if "Срочная" in request_type:
            target_channel_id = CHANNELS["Срочная"]
            admin_notification = f"🚨 НОВЫЙ СРОЧНЫЙ ЗАПРОС!\nОт пользователя: @{username}\nСообщение: {message_text}"
            try:
                await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления администратору о срочном запросе: {e}", exc_info=True)
        elif "Анонимное сообщение" in request_type:
            target_channel_id = CHANNELS["Анонимные сообщения"]
            await context.bot.send_message(chat_id=target_channel_id, text=anonymous_text, parse_mode="Markdown")
            await update.message.reply_text("✅ Ваше анонимное сообщение отправлено!", reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
            return MAIN_MENU
        elif "Анонимное" in request_type: # Обработка старого "Анонимные"
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

        if "Анонимное сообщение" not in request_type:
            await context.bot.send_message(chat_id=target_channel_id, text=forward_text, parse_mode="Markdown")
            await update.message.reply_text(MESSAGE_SENT_SUCCESS, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")

        return MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}", exc_info=True)
        await update.message.reply_text(MESSAGE_SEND_ERROR.format(e), reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
        return MAIN_MENU

async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, faq_type: str) -> int:
    try:
        question = update.message.text
        if question == BACK_BUTTON:
            await update.message.reply_text(HELP_MENU_MESSAGE, reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
            return HELP_MENU
        elif "Консультация" in question:
            context.user_data["type"] = f"{faq_type.capitalize()} консультация"
            await update.message.reply_text(CONSULTATION_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="Markdown")
            return TYPING
        else:
            response = FAQ_RESPONSES.get(question, "Ответ не найден")
            await update.message.reply_text(response, parse_mode="Markdown")
            return FAQ_LEGAL if faq_type == "юридическая" else FAQ_MED
    except Exception as e:
        logger.error(f"Ошибка в handle_faq ({faq_type}): {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
        return HELP_MENU

async def handle_legal_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_faq(update, context, "юридическая")

async def handle_medical_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_faq(update, context, "медицинская")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
        return START
    except Exception as e:
        logger.error(f"Ошибка в cancel: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="Markdown")
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
            ANONYMOUS_MESSAGE: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    # Запуск бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

