# -*- coding: utf-8 -*-
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters, CallbackContext, JobQueue
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from telegram.constants import ParseMode
from google.oauth2 import service_account
from google.auth.transport.requests import Request

load_dotenv()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена и ID чатов из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
GSHEET_URL = os.getenv("GSHEET_URL")
VOLUNTEER_NOTIFICATION_CHAT_ID = os.getenv("VOLUNTEER_NOTIFICATION_CHAT_ID")

# Состояния разговора
START, MAIN_MENU, HELP_MENU, TYPING, FAQ_LEGAL, FAQ_MED = range(6)

# Клавиатуры
MAIN_MENU_BUTTONS = [['Попросить о помощи'], ['Предложить ресурс'], ['Стать волонтером'], ['Поддержать проект']]
HELP_MENU_BUTTONS = [['🆘 Срочная помощь'], ['💼 Юридическая помощь'], ['🏥 Медицинская помощь'], ['🧠 Психологическая помощь'], ['🏠 Жилье/финансы'], ['⬅️ Назад']]
LEGAL_FAQ_BUTTONS = [['Какие документы нужны для получения статуса беженца?'], ['Как получить временное убежище?'], ['Нужна юридическая консультация'], ['⬅️ Назад']]
MEDICAL_FAQ_BUTTONS = [['Где получить первую медицинскую помощь?'], ['Как получить доступ к медицинскому обслуживанию?'], ['Нужна медицинская консультация'], ['⬅️ Назад']]
BACK_BUTTON = '⬅️ Назад'

# Сообщения
START_MESSAGE = "Добро пожаловать! Чем я могу вам помочь?"
HELP_MENU_MESSAGE = "Выберите категорию помощи:"
RESOURCE_PROMPT_MESSAGE = "Опишите, какой ресурс вы можете предложить:"
VOLUNTEER_MESSAGE = "Если вы хотите стать волонтером, пожалуйста, опишите ваши навыки и как вы можете помочь."
DONATE_MESSAGE = "Вы можете поддержать наш проект, перейдя по [ссылке](https://example.com/donate)." # Замените на реальную ссылку
EMERGENCY_MESSAGE = "Опишите вашу срочную ситуацию:"
PSYCHOLOGICAL_HELP_PROMPT = "Опишите, какая психологическая помощь вам нужна:"
HOUSING_FINANCE_PROMPT = "Опишите вашу потребность в жилье или финансовой помощи:"
CHOOSE_FROM_MENU = "Пожалуйста, выберите пункт из меню."
CHOOSE_HELP_CATEGORY = "Пожалуйста, выберите категорию помощи."
MESSAGE_SENT_SUCCESS = "Ваше сообщение отправлено!"
MESSAGE_SEND_ERROR = "Произошла ошибка при отправке сообщения: {}"
CANCEL_MESSAGE = "Действие отменено."
BACK_TO_MAIN_MENU = "Вы вернулись в главное меню."
CONSULTATION_PROMPT = "Опишите ваш вопрос для консультации:"

# ID каналов
CHANNELS = {
    "Срочная": os.getenv("URGENT_CHANNEL_ID"),
    "Анонимные": os.getenv("ANONYMOUS_CHANNEL_ID"),
    "Юридические": os.getenv("LEGAL_CHANNEL_ID"),
    "Медицинские": os.getenv("MEDICAL_CHANNEL_ID"),
    "Психологическая помощь": os.getenv("PSYCHOLOGICAL_CHANNEL_ID"),
    "Предложение ресурса": os.getenv("RESOURCE_OFFER_CHANNEL_ID"),
    "Волонтеры Остальные": os.getenv("VOLUNTEERS_OTHER_CHANNEL_ID"),
    "Волонтеры Психология": os.getenv("VOLUNTEERS_PSYCHOLOGY_CHANNEL_ID"),
    "Волонтеры Юристы": os.getenv("VOLUNTEERS_LAWYERS_CHANNEL_ID"),
    "Волонтеры Инфо": os.getenv("VOLUNTEERS_INFO_CHANNEL_ID"),
}

# FAQ ответы
FAQ_RESPONSES = {
    "Какие документы нужны для получения статуса беженца?": "Для получения статуса беженца обычно требуются [список документов](https://example.com/refugee_docs).", # Замените на реальную ссылку
    "Как получить временное убежище?": "Информация о получении временного убежище доступна по [ссылке](https://example.com/temporary_shelter).", # Замените на реальную ссылку
    "Где получить первую медицинскую помощь?": "Ближайшие пункты оказания первой медицинской помощи можно найти [здесь](https://example.com/medical_help).", # Замените на реальную ссылку
    "Как получить доступ к медицинскому обслуживанию?": "Информация о доступе к медицинскому обслуживанию доступна [по ссылке](https://example.com/medical_access).", # Замените на реальную ссылку
}

# Глобальная переменная для отслеживания последней обработанной строки в Google Sheets
LAST_PROCESSED_ROW = 1

# Функция для подключения к Google Sheets
def get_gsheet_client():
    creds = None
    if os.path.exists('token.json'):
        creds = service_account.Credentials.from_service_account_file('token.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = service_account.Credentials.from_service_account_file(
                'rapid-goal-457809-n6-9e1bda1dc23c.json',
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
    gc = gspread.authorize(creds)
    return gc

# Функция для получения данных из Google Sheets
def get_gsheet_data():
    try:
        gc = get_gsheet_client()
        spreadsheet = gc.open_by_url(GSHEET_URL)
        worksheet = spreadsheet.sheet1
        data = worksheet.get_all_records()
        return data
    except Exception as e:
        logger.error(f"Ошибка при получении данных из Google Sheets: {e}", exc_info=True)
        return None

# Асинхронная функция для периодической проверки новых волонтеров
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
                volunteer_info = f"Новый волонтер (ID: {row_number})!\n\n"
                for key, value in volunteer_data.items():
                    volunteer_info += f"{key}: {value}\n"

                try:
                    await context.bot.send_message(chat_id=target_chat_id, text=volunteer_info)
                    LAST_PROCESSED_ROW = row_number
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
        context.user_data["type"] = "Стать волонтером"
        await update.message.reply_text("Если вы хотите стать волонтером, пожалуйста, заполните эту [анкету](https://docs.google.com/forms/d/e/1FAIpQLSdj4lm6Z_nsvZh6zAWnk0ob8p6hvG6fxVQV5kYrcdXTVjpbaA/viewform?usp=dialog), чтобы стать волонтером.",
                                        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
                                        parse_mode=ParseMode.MARKDOWN,
                                        disable_web_page_preview=True)
        return TYPING
    elif choice == "Поддержать проект":
        await update.message.reply_text(DONATE_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
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
        context.user_data["type"] = "Жилье/финансы"
        await update.message.reply_text(HOUSING_FINANCE_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
        return TYPING
    elif choice == BACK_BUTTON:
        return await start(update, context)
    else:
        await update.message.reply_text(CHOOSE_HELP_CATEGORY)
        return HELP_MENU

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
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
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

    if "Стать волонтером" in request_type:
        await update.message.reply_text("Пожалуйста, заполните эту [анкету](https://docs.google.com/forms/d/e/1FAIpQLSdj4lm6Z_nsvZh6zAWnk0ob8p6hvG6fxVQV5kYrcdXTVjpbaA/viewform?usp=dialog), чтобы стать волонтером.",
                                        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
                                        parse_mode=ParseMode.MARKDOWN,
                                        disable_web_page_preview=True)
        return MAIN_MENU
    elif "Срочная" in request_type:
        target_channel_id = CHANNELS.get("Срочная")
        # Отправляем уведомление администраторам
        admin_notification = f"🚨 НОВЫЙ СРОЧНЫЙ ЗАПРОС!\nОт пользователя: @{username}\nСообщение: {message_text}"
        try:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification)
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления администратору о срочном запросе: {e}", exc_info=True)
    elif "Анонимное" in request_type:
        target_channel_id = CHANNELS.get("Анонимные")
    elif "Юридическая" in request_type:
        target_channel_id = CHANNELS.get("Юридические")
    elif "Медицинская" in request_type:
        target_channel_id = CHANNELS.get("Медицинские")
    elif "Психологическая помощь" in request_type:
        target_channel_id = CHANNELS.get("Психологическая помощь")
    elif "Предложение ресурса" in request_type:
        target_channel_id = CHANNELS.get("Предложение ресурса")
    elif "Юридическая консультация" in request_type:
        target_channel_id = CHANNELS.get("Юридические")
    elif "Медицинская консультация" in request_type:
        target_channel_id = CHANNELS.get("Медицинские")
    elif "Жилье/финансы" in request_type:
        target_channel_id = CHANNELS.get("Срочная") # Решил отправлять пока в "Срочная", логику можно уточнить

    if target_channel_id:
        try:
            await context.bot.send_message(chat_id=target_channel_id, text=forward_text)
            await update.message.reply_text(MESSAGE_SENT_SUCCESS, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}", exc_info=True)
            await update.message.reply_text(MESSAGE_SEND_ERROR.format(e), reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    else:
        await update.message.reply_text("Не удалось определить целевой канал для вашего запроса.", reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    return MAIN_MENU

async def unknown(update: Update, context: ContextTypes.
DEFAULT_TYPE)) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.")

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Set up conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_menu)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_legal_faq)],
            FAQ_MED: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_medical_faq)],
        },
        fallbacks=[CommandHandler('cancel', lambda update, context: update.message.reply_text(CANCEL_MESSAGE))]
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Запуск периодической задачи проверки волонтеров
    async def job_callback(context: CallbackContext):
        await process_new_volunteers(context)

    job_queue = application.job_queue
    job_queue.run_repeating(job_callback, interval=300, first=5) # Проверять каждые 5 минут (300 секунд)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
