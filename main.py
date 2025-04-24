import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import sys
sys.path.append('/data/data/com.termux/files/usr/lib/python3.12/site-packages')
import gspread

from google.oauth2.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import sys

# Добавляем путь к директории, где установлены библиотеки
sys.path.append('/data/data/com.termux/files/usr/lib/python3.12/site-packages')

# Теперь можно импортировать библиотеку
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue

# Остальной код
# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
# --- НОВЫЙ БЛОК: Интеграция с Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '/storage/emulated/0/Download/rapid-goal-457809-n6-9e1bda1dc23c.json',
    scope
)

# <--- ВСТАВЬ СВОЙ ПУТЬ
SPREADSHEET_ID = '1w21-rrE7j5QATYtq8IixK79rQxN-LOC8tic827TT8ts'
WORKSHEET_NAME = 'Ответы на форму (1)'
# --- НОВЫЙ БЛОК: Отслеживание обработанных ID ---
LAST_PROCESSED_ROW = 1  # Инициализируем с первой строкой данных

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
) = range(6)

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
    "Срочная": -1002507059500,  # t64_gen (остальное)
    "Анонимные": -1002507059500, # t64_gen (остальное) - пока используем этот же
    "Юридические": -1002523489451, # t64_legal
    "Медицинские": -1002507059500, # t64_gen (остальное) - пока используем этот же
    "Психологическая помощь": -1002677526813, # t64_psych
    "Предложение ресурса": -1002645097441 # t4_misc
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
    "• 🆘 **Попросить о помощи** в различных ситуациях.\n"
    "• 📚 **Предложить ресурс**, который может быть полезен сообществу.\n"
    "• 💖 **Стать волонтером** и помочь проекту.\n"
    "• 💸 **Поддержать проект**, чтобы мы могли продолжать нашу работу.\n\n"
    "Пожалуйста, выберите нужную опцию:"
)
HELP_MENU_MESSAGE = "Выберите категорию помощи:"
RESOURCE_PROMPT_MESSAGE = "Опишите, какой ресурс вы хотите предложить:"
VOLUNTEER_MESSAGE = (
    "Мы очень рады твоему желанию присоединиться к нашей команде волонтеров! "
    "Твоя помощь может стать неоценимым вкладом в поддержку нашего сообщества.\n\n"
    "Пожалуйста, заполни эту форму, чтобы мы могли узнать тебя лучше и предложить подходящие задачи:\n"
    "[Форма для волонтеров](https://docs.google.com/forms/d/1kFHSQ05lQyL6s7WDdqTqqY-Il6La3Sehhj_1iVTNgus/edit)\n\n"
    "Мы свяжемся с тобой в ближайшее время после получения твоей заявки. "
    "Спасибо за твою готовность помогать!"
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
    "⚠️ **ВНИМАНИЕ! В экстренной ситуации, угрожающей вашей жизни или здоровью, действуйте немедленно:**\n\n"
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

def get_gsheet_data():
    """Получает все записи из Google Sheets."""
    try:
        from oauth2client.service_account import ServiceAccountCredentials
        import gspread

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        CREDENTIALS_FILE = '/storage/emulated/0/Download/rapid-goal-457809-n6-9e1bda1dc23c.json'
        SPREADSHEET_ID = '1w21-rrE7j5QATYtq8IixK79rQxN-LOC8tic827TT8ts'
        WORKSHEET_NAME = 'Ответы на форму (1)'

        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        data = worksheet.get_all_records()
        return data
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при получении данных из Google Sheets (oauth2client): {e}", exc_info=True)
        print(f"Ошибка Google Sheets (oauth2client): {e}")
        return None

async def process_new_volunteers(context: ContextTypes.DEFAULT_TYPE):
    """Периодически проверяет новые ответы в Google Sheets и отправляет уведомления."""
    global LAST_PROCESSED_ROW
    new_volunteers_data = get_gsheet_data()
    if new_volunteers_data:
        for i, volunteer_data in enumerate(new_volunteers_data):
            row_number = i + 2
            if row_number > LAST_PROCESSED_ROW:
                help_direction = volunteer_data.get("d")
                target_chat_id = CHANNELS.get("Волонтеры Остальные")
                if help_direction == "Психологическая помощь":
                    target_chat_id = CHANNELS.get("Волонтеры Психология")
                elif help_direction == "Юридическая помощь":
                    target_chat_id = CHANNELS.get("Волонтеры Юристы")
                elif help_direction == "Информационная поддержка":
                    target_chat_id = CHANNELS.get("Волонтеры Инфо")
                                volunteer_info = f"Новый волон""


                try:
                                        await context.bot.send_message(chat_id=target_chat_id, text=volunteer_info)
                except Exception as e:
                    logger.error(f"Ошибка при отправке уведомления о волонтере: {e}", exc_info=True)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(START_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    return MAIN_MENU

# Обработчик главного меню
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
        if choice == "Попросить о помощи":

        await update.message.reply_text(HELP_MENU_MESSAGE, reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True))
        return HELP_MENU
    elif choice == "Предложить ресурс":
        context.user_data["type"] = "💡 Предложение ресурса"
        await update.message.reply_text(RESOURCE_PROMPT_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
        return TYPING
    elif choice == "Стать волонтером":
        await update.message.reply_text(VOLUNTEER_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="Markdown", disable_web_page_preview=True)
        return TYPING
    elif choice == "Поддержать проект":
        await update.message.reply_text(DONATE_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode="Markdown", disable_web_page_preview=True)
        return TYPING
    else:
        await update.message.reply_text(CHOOSE_FROM_MENU)
        return MAIN_MENU

# Обработчик меню помощи
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "🆘 Срочная помощь":
        await update.message.reply_text(EMERGENCY_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), disable_web_page_preview=True)
        context.user_data["type"] = "Срочная"
        return TYPING
    elif choice == "💼 Юридическая помощь":
        await update.message.reply_text("Выберите вопрос:", reply_markup=ReplyKeyboardMarkup(LEGAL_FAQ_BUTTONS, resize_keyboard=True))
        return FAQ_LEGAL
    elif choice == "🏥 Медицинская помощь":
        context.user_data["type"] = "Медицинская"
        await update.message.reply_text("Выберите вопрос:", reply_markup=ReplyKeyboardMarkup(MEDICAL_FAQ_BUTTONS, resize_keyboard=True))
        return FAQ_MED
    elif choice == "🧠 Психологическая помощь":
        context.user_data["type"] = "Психологическая помощь"
        await update.message.reply_text(PSYCHOLOGICAL_HELP_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
        return TYPING
    elif choice == "🏠 Жилье/финансы":
        context.user_data["type"] = "Срочная"  # Или "Остальное"
        await update.message.reply_text(HOUSING_FINANCE_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
        return TYPING
    elif choice == BACK_BUTTON:
        return await start(update, context)
    else:
        await update.message.reply_text(CHOOSE_HELP_CATEGORY)
        return HELP_MENU

# Функция handle_message должна быть определена здесь, на том же уровне
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message_text = update.message.text
    if message_text == BACK_BUTTON:
        await update.message.reply_text(BACK_TO_MAIN_MENU, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
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
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification)
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
        await context.bot.send_message(chat_id=target_channel_id, text=forward_text)
        await update.message.reply_text(MESSAGE_SENT_SUCCESS, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}", exc_info=True)
        await update.message.reply_text(MESSAGE_SEND_ERROR.format(e), reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))

    return MAIN_MENU


# Обработчик FAQ (юридические и медицинские)
async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, faq_type: str) -> int:
    question = update.message.text
    if question == BACK_BUTTON:
        await update.message.reply_text(HELP_MENU_MESSAGE, reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True))
        return HELP_MENU
    elif "Консультация" in question:
        context.user_data["type"] = f"{faq_type.capitalize()} консультация"
        await update.message.reply_text(CONSULTATION_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
        return TYPING
    else:
        response = FAQ_RESPONSES.get(question, "Ответ не найден")
        await update.message.reply_text(response, parse_mode="Markdown")
        return FAQ_LEGAL if faq_type == "юридическая" else FAQ_MED

async def handle_legal_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_faq(update, context, "юридическая")

async def handle_medical_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_faq(update, context, "медицинская")
# Обработчик ввода текста пользователя
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message_text = update.message.text
    if message_text == BACK_BUTTON:
        await update.message.reply_text(BACK_TO_MAIN_MENU, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
        return MAIN_MENU

    request_type = context.user_data.get("type", "Запрос")
    username = update.message.from_user.username or "нет"
    forward_text = f"📩 {request_type}\nОт @{username}\n\n{message_text}"

    target_channel_id = ADMIN_CHAT_ID  # По умолчанию отправляем админу

    if "Срочная" in request_type:
        target_channel_id = CHANNELS["Срочная"]
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
        await context.bot.send_message(chat_id=target_channel_id, text=forward_text)
        await update.message.reply_text(MESSAGE_SENT_SUCCESS, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}", exc_info=True)
        await update.message.reply_text(MESSAGE_SEND_ERROR.format(e), reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))

    return MAIN_MENU

# Обработчик команды /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    return START

# Запуск бота
def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [CommandHandler("start", start)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_menu)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_legal_faq)],
            FAQ_MED: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_medical_faq)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    # --- НОВЫЙ БЛОК: Периодическая проверка новых волонтеров ---
    # Запускаем задачу, которая будет выполняться каждые N секунд (например, 60 секунд)
    app.job_queue.run_repeating(process_new_volunteers, interval=60, first=10)

    # Запуск бота в режиме ожидания
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
