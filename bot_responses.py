import os
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
import logging
from telegram.error import TelegramError
import hashlib
from bot_responses import (
    START_MESSAGE,
    HELP_MENU_MESSAGE,
    RESOURCE_PROMPT_MESSAGE,
    VOLUNTEER_MESSAGE,
    DONATE_MESSAGE,
    EMERGENCY_MESSAGE,
    HOUSING_FINANCE_PROMPT,
    PSYCHOLOGICAL_HELP_PROMPT,
    CONSULTATION_PROMPT,
    MESSAGE_SENT_SUCCESS,
    MESSAGE_SEND_ERROR,
    CANCEL_MESSAGE,
    BACK_TO_MAIN_MENU,
    CHOOSE_FROM_MENU,
    CHOOSE_HELP_CATEGORY,
    GENDER_THERAPY_MESSAGE,
    FEMINIZING_HRT_INFO,
    MASCULINIZING_HRT_INFO,
    DIY_HRT_WARNING,
    LGBT_FAMILIES_INFO,
    REPORT_ABUSE_MESSAGE,
    FTM_SURGERY_INFO,
    MTF_SURGERY_INFO,
    GENDER_THERAPY_CHOICE_MESSAGE,
    SURGERY_INFO_MESSAGE,
    DOCUMENTS_MESSAGE,
    PROPAGANDA_MESSAGE,
    F64_MESSAGE,
    SURGERY_PLANNING_PROMPT,
    FAREWELL_MESSAGE,
    DIY_HRT_GUIDE_NAME,
    ANONYMOUS_CONFIRMATION,
    LEGAL_CONSULTATION_INTRO,
    MEDICAL_CONSULTATION_INTRO,
    PSYCH_CONSULTATION_INTRO,
    LEGAL_SITUATION_PROMPT,
    LEGAL_ASSISTANCE_PROMPT,
    LEGAL_CONTACT_PROMPT,
    MEDICAL_SITUATION_PROMPT,
    MEDICAL_REGION_ASSISTANCE_PROMPT,
    MEDICAL_CONTACT_PROMPT,
    PSYCH_CHOICE_PROMPT,
    PSYCH_SITUATION_PROMPT,
    PSYCH_REGION_ASSISTANCE_PROMPT,
    PSYCH_CONTACT_PROMPT,
    PSYCH_ANONYMOUS_PROMPT,
    CONSULTATION_REQUEST_RECEIVED, # Возможно, стоит переименовать это сообщение
    ANONYMOUS_REQUEST_SENT,
)
from keyboards import (
    MAIN_MENU_BUTTONS,
    HELP_MENU_BUTTONS,
    LEGAL_MENU_BUTTONS,
    MEDICAL_MENU_BUTTONS,
    GENDER_THERAPY_CHOICE_BUTTONS,
    BACK_BUTTON,
    SURGERY_INFO_KEYBOARD,
    VOLUNTEER_HELP_TYPE_KEYBOARD,
    DONE_BUTTON,
    FINISH_MENU_KEYBOARD,
    YES_NO_BUTTONS,
    YES_NO_MAYBE_BUTTONS,
)
from channels import CHANNELS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
HASH_SALT = os.getenv("HASH_SALT")
DIY_HRT_GUIDE_PATH = os.getenv("DIY_HRT_GUIDE_PATH")

if BOT_TOKEN:
    print(f"Токен бота: {BOT_TOKEN}")
else:
    print("Ошибка: Переменная BOT_TOKEN не найдена.")

(
    START,
    MAIN_MENU,
    HELP_MENU,
    TYPING,
    FAQ_LEGAL,
    MEDICAL_MENU,
    VOLUNTEER_START_STATE,
    VOLUNTEER_NAME,
    VOLUNTEER_REGION,
    VOLUNTEER_HELP_TYPE,
    VOLUNTEER_CONTACT,
    ANONYMOUS_MESSAGE,
    MEDICAL_GENDER_THERAPY_MENU,
    MEDICAL_FTM_HRT,
    MEDICAL_MTF_HRT,
    MEDICAL_SURGERY_PLANNING,
    DONE_STATE,
    CONSULTATION_START,
    CONSULTATION_LEGAL_SITUATION,
    CONSULTATION_LEGAL_ASSISTANCE,
    CONSULTATION_LEGAL_CONTACT,
    CONSULTATION_MEDICAL_SITUATION,
    CONSULTATION_MEDICAL_ASSISTANCE,
    CONSULTATION_MEDICAL_CONTACT,
    CONSULTATION_PSYCH_CHOICE,
    CONSULTATION_PSYCH_SITUATION,
    CONSULTATION_PSYCH_ASSISTANCE,
    CONSULTATION_PSYCH_CONTACT,
    CONSULTATION_CONFIRM,
    CONSULTATION_PSYCH_ANONYMOUS_MESSAGE,
) = range(29)

def generate_message_id(user_id: int) -> str:
    """Генерирует хеш для анонимной идентификации сообщений"""
    return hashlib.sha256(f"{HASH_SALT}_{user_id}_{os.urandom(16)}".encode()).hexdigest()[:8]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(START_MESSAGE, reply_markup=keyboard, parse_mode="Markdown")
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = update.message.text
    if user_choice == "🆘 Попросить о помощи":
        keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(HELP_MENU_MESSAGE, reply_markup=keyboard, parse_mode="Markdown")
        return HELP_MENU
    elif user_choice == "➕ Предложить ресурс":
        context.user_data["request_type"] = "Ресурс"
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(RESOURCE_PROMPT_MESSAGE, reply_markup=keyboard)
        return TYPING
    elif user_choice == "🤝 Стать волонтером":
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text(VOLUNTEER_MESSAGE, reply_markup=keyboard)
        return VOLUNTEER_START_STATE
    elif user_choice == "💸 Поддержать проект":
        await update.message.reply_text(DONATE_MESSAGE, parse_mode="Markdown")
        return MAIN_MENU
    elif user_choice == "✉️ Анонимное сообщение":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Пожалуйста, напишите ваше анонимное сообщение:",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = "Анонимное сообщение"
        return ANONYMOUS_MESSAGE
    elif user_choice == BACK_BUTTON or user_choice == DONE_BUTTON:
        await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text(CHOOSE_FROM_MENU)
        return MAIN_MENU

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = update.message.text
    if user_choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=keyboard,
        )
        return MAIN_MENU
    elif user_choice == "🚨 Срочная помощь":
        context.user_data["request_type"] = "Срочная помощь"
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(EMERGENCY_MESSAGE, reply_markup=keyboard)
        return TYPING
    elif user_choice == "🏠 Жилье/финансы":
        context.user_data["request_type"] = "Жилье/финансы"
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(HOUSING_FINANCE_PROMPT, reply_markup=keyboard)
        return TYPING
    elif user_choice == "🧠 Психологическая помощь":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(PSYCHOLOGICAL_HELP_PROMPT, reply_markup=keyboard)
        context.user_data["consultation_type"] = "Психологическая"
        return CONSULTATION_START
    elif user_choice == "🩺 Медицинская помощь":
        keyboard = ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Выберите категорию медицинской помощи:",
            reply_markup=keyboard,
        )
        return MEDICAL_MENU
    elif user_choice == "⚖️ Юридическая помощь":
        keyboard = ReplyKeyboardMarkup(LEGAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Выберите категорию юридической помощи:",
            reply_markup=keyboard,
        )
        return FAQ_LEGAL
    else:
        await update.message.reply_text(CHOOSE_HELP_CATEGORY)
        return HELP_MENU

async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text
    request_type = context.user_data.get("request_type", "Сообщение")

    if user_text and user_text != BACK_BUTTON:
        channel_mapping = {
            "Ресурс": "t64_misc",
            "Срочная помощь": "t64_gen",
            "Помощь - Сообщение о нарушении (юридическое)": "t64_legal",
            "Помощь - Юридическая консультация (смена документов)": "t64_legal",
            "Помощь - Планирование операции": "t64_gen",
            "Жилье/финансы": "t64_gen",
        }
        channel_name = channel_mapping.get(request_type)
        if channel_name:
            try:
                await context.bot.send_message(
                    chat_id=CHANNELS.get(channel_name),
                    text=f"Запрос от пользователя:\n\n{user_text}"
                )
                await update.message.reply_text(
                    MESSAGE_SENT_SUCCESS,
                    reply_markup=FINISH_MENU_KEYBOARD,
                )
                return MAIN_MENU
            except TelegramError as e:
                logger.error(f"Ошибка Telegram API при отправке сообщения: {e}", exc_info=True)
                await update.message.reply_text(
                    MESSAGE_SEND_ERROR.format(e),
                    reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
                )
                return MAIN_MENU
            except Exception as e:
                logger.error(f"Непредвиденная ошибка при отправке сообщения: {e}", exc_info=True)
                await update.message.reply_text(
                    MESSAGE_SEND_ERROR.format(e),
                    reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
                )
                return MAIN_MENU
        elif request_type == "Психологическая помощь":
            context.user_data["consultation_type"] = "Психологическая"
            await update.message.reply_text(PSYCH_CONSULTATION_INTRO)
            return CONSULTATION_START
        elif request_type == "Помощь - Юридическая консультация (смена документов)":
            context.user_data["consultation_type"] = "Юридическая"
            await update.message.reply_text(LEGAL_CONSULTATION_INTRO)
            return CONSULTATION_START
        elif request_type == "Помощь - Планирование операции":
            await context.bot.send_message(
                chat_id=CHANNELS.get("t64_gen"),
                text=f"Запрос от пользователя (планирование операции):\n\n{user_text}"
            )
            await update.message.reply_text(
                MESSAGE_SENT_SUCCESS,
                reply_markup=FINISH_MENU_KEYBOARD,
            )
            return MAIN_MENU
        else:
            await update.message.reply_text(
                "Произошла ошибка при обработке вашего запроса.",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return MAIN_MENU
    elif user_text == BACK_BUTTON:
        return await help_menu(update, context)
    return TYPING

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            HELP_MENU_MESSAGE,
            reply_markup=keyboard,
        )
        return HELP_MENU
    elif choice == "🏳️‍🌈 ЛГБТ+ семьи":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            LGBT_FAMILIES_INFO,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return FAQ_LEGAL
    elif choice == "📝 Как сменить документы":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Запросить консультацию", callback_data='request_legal_docs')]
        ])
        await update.message.reply_text(DOCUMENTS_MESSAGE, parse_mode="Markdown", reply_markup=keyboard)
        return FAQ_LEGAL
    elif choice == "📢 Что такое пропаганда ЛГБТ?":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(PROPAGANDA_MESSAGE, parse_mode="Markdown", reply_markup=keyboard)
        return FAQ_LEGAL
    elif choice == "🗣️ Юридическая консультация":
        context.user_data["consultation_type"] = "Юридическая"
        await update.message.reply_text(LEGAL_CONSULTATION_INTRO)
        return CONSULTATION_START
    elif choice == "🚨 Сообщить о нарушении":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            REPORT_ABUSE_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = "Помощь - Сообщение о нарушении (юридическое)"
        return TYPING
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return FAQ_LEGAL

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            HELP_MENU_MESSAGE,
            reply_markup=keyboard,
        )
        return HELP_MENU
    elif choice == "🗣️ Медицинская консультация":
        context.user_data["consultation_type"] = "Медицинская"
        await update.message.reply_text(MEDICAL_CONSULTATION_INTRO)
        return CONSULTATION_START
    elif choice == "💉HRT":
        keyboard = ReplyKeyboardMarkup(
            GENDER_THERAPY_CHOICE_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            GENDER_THERAPY_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return MEDICAL_GENDER_THERAPY_MENU
    elif choice == "❓ F64":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            F64_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return MEDICAL_MENU
    elif choice == "⚕️ Операции":
        await update.message.reply_text(
            SURGERY_INFO_MESSAGE,
            parse_mode="Markdown",
            reply_markup=SURGERY_INFO_KEYBOARD,
        )
        return MEDICAL_SURGERY_PLANNING
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_MENU

async def medical_gender_therapy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_menu(update, context)
    elif choice == "T":
        keyboard = ReplyKeyboardMarkup(
            [
                ["DIY"],
                ["Запросить консультацию по мужской ГТ"],
                [BACK_BUTTON],
            ],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            MASCULINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return MEDICAL_FTM_HRT
    elif choice == "E":
        keyboard = ReplyKeyboardMarkup(
            [
                ["DIY"],
                ["Запросить консультацию по женской ГТ"],
                [BACK_BUTTON],
            ],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            FEMINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return MEDICAL_MTF_HRT
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_GENDER_THERAPY_MENU

async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_gender_therapy_menu(update, context)
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            DIY_HRT_WARNING, parse_mode="Markdown", reply_markup=keyboard
        )
        return MEDICAL_FTM_HRT
    elif choice == "Запросить консультацию по мужской ГТ":
        context.user_data["consultation_type"] = "Медицинская"
        await update.message.reply_text(MEDICAL_CONSULTATION_INTRO)
        return CONSULTATION_START
    elif choice == "Я понимаю риски, скачать гайд":
        if DIY_HRT_GUIDE_PATH:
            try:
                with open(DIY_HRT_GUIDE_PATH, 'rb') as pdf_file:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=pdf_file,
                        filename=DIY_HRT_GUIDE_NAME,
                    )
                    keyboard = ReplyKeyboardMarkup(
                        [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
                        resize_keyboard=True,
                    )
                    await update.message.reply_text(
                        "Желаем вам удачи на вашем пути!",
                        reply_markup=keyboard
                    )
                    return MEDICAL_FTM_HRT
            except FileNotFoundError:
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text("Файл гайда не найден.", reply_markup=keyboard)
                return MEDICAL_FTM_HRT
            except TelegramError as e:
                logger.error(f"Ошибка Telegram API при отправке файла: {e}", exc_info=True)
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text(f"Произошла ошибка при отправке файла: {e}", reply_markup=keyboard)
                return MEDICAL_FTM_HRT
        else:
            keyboard = ReplyKeyboardMarkup(
                [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
                resize_keyboard=True,
            )
            await update.message.reply_text("Путь к файлу гайда не настроен.", reply_markup=keyboard)
            return MEDICAL_FTM_HRT
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_FTM_HRT

async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_gender_therapy_menu(update, context)
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            DIY_HRT_WARNING, parse_mode="Markdown", reply_markup=keyboard
        )
        return MEDICAL_MTF_HRT
    elif choice == "Запросить консультацию по женской ГТ":
        context.user_data["consultation_type"] = "Медицинская"
        await update.message.reply_text(MEDICAL_CONSULTATION_INTRO)
        return CONSULTATION_START
    elif choice == "Я понимаю риски, скачать гайд":
        if DIY_HRT_GUIDE_PATH:
            try:
                with open(DIY_HRT_GUIDE_PATH, 'rb') as pdf_file:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=pdf_file,
                        filename=DIY_HRT_GUIDE_NAME,
                    )
                    keyboard = ReplyKeyboardMarkup(
                        [["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
                        resize_keyboard=True,
                    )
                    await update.message.reply_text(
                        "Желаем вам удачи на вашем пути!",
                        reply_markup=keyboard
                    )
                    return MEDICAL_MTF_HRT
            except FileNotFoundError:
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text("Файл гайда не найден.", reply_markup=keyboard)
                return MEDICAL_MTF_HRT
            except TelegramError as e:
                logger.error(f"Ошибка Telegram API при отправке файла: {e}", exc_info=True)
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text(f"Произошла ошибка при отправке файла: {e}", reply_markup=keyboard)
                return MEDICAL_MTF_HRT
        else:
            keyboard = ReplyKeyboardMarkup(
                [["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
                resize_keyboard=True,
            )
            await update.message.reply_text("Путь к файлу гайда не настроен.", reply_markup=keyboard)
            return MEDICAL_MTF_HRT
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_MTF_HRT

async def medical_surgery_planning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_menu(update, context)
    elif choice == "ФТМ Операции":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            FTM_SURGERY_INFO,
            reply_markup=keyboard,
        )
        return MEDICAL_SURGERY_PLANNING
    elif choice == "МТФ Операции":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            MTF_SURGERY_INFO,
            reply_markup=keyboard,
        )
        return MEDICAL_SURGERY_PLANNING
    elif update.callback_query and update.callback_query.data == 'plan_surgery':
        await update.callback_query.answer()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=SURGERY_PLANNING_PROMPT,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        context.user_data["request_type"] = "Помощь - Планирование операции"
        return TYPING
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_SURGERY_PLANNING

async def volunteer_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = ReplyKeyboardMarkup([["Продолжить", "Отмена"]], resize_keyboard=True)
    await update.message.reply_text(VOLUNTEER_MESSAGE, reply_markup=keyboard)
    return VOLUNTEER_NAME # Исправлено: теперь переходит к запросу имени

async def volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text
    if name == "Отмена":
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    elif not name:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text("Пожалуйста, введите ваше имя.", reply_markup=keyboard)
        return VOLUNTEER_NAME
    context.user_data["volunteer_data"] = {"name": name}
    keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
    await update.message.reply_text("Из какого вы региона?", reply_markup=keyboard)
    return VOLUNTEER_REGION

async def volunteer_region_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    region = update.message.text
    if region == "Отмена":
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    elif not region:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text("Пожалуйста, введите ваш регион.", reply_markup=keyboard)
        return VOLUNTEER_REGION
    context.user_data["volunteer_data"]["region"] = region
    await update.message.reply_text(
        "Чем вы готовы помочь?",
        reply_markup=VOLUNTEER_HELP_TYPE_KEYBOARD,
    )
    return VOLUNTEER_HELP_TYPE

async def volunteer_help_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    help_type = update.message.text
    if help_type == "Отмена":
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    context.user_data["volunteer_data"]["help_type"] = help_type
    user_contact = update.effective_user.username
    context.user_data["volunteer_data"]["contact"] = f"@{user_contact}" if user_contact else "не указан"
    keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
    await update.message.reply_text("Как с вами можно связаться (Telegram, email)?", reply_markup=keyboard)
    return VOLUNTEER_CONTACT

async def volunteer_contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact_other = update.message.text
    if contact_other == "Отмена":
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    elif not contact_other:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text("Пожалуйста, введите ваши контактные данные.", reply_markup=keyboard)
        return VOLUNTEER_CONTACT
    context.user_data["volunteer_data"]["contact_other"] = contact_other
    user_id = update.effective_user.id
    volunteer_info = f"""Новый волонтер!
ID: {user_id}
Имя: {context.user_data["volunteer_data"].get("name", "не указано")}
Регион: {context.user_data["volunteer_data"].get("region", "не указано")}
Тип помощи: {context.user_data["volunteer_data"].get("help_type", "не указано")}
Контакт (Telegram): {context.user_data["volunteer_data"].get("contact", "не указано")}
Контакт (Другое): {context.user_data["volunteer_data"].get("contact_other", "не указано")}"""

    try:
        await context.bot.send_message(chat_id=CHANNELS.get("t64_admin"), text=volunteer_info)
        logger.info(f"Сообщение отправлено в t64_admin: {volunteer_info}")
    except TelegramError as e:
        logger.error(f"Ошибка Telegram API при отправке сообщения в t64_admin: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при отправке сообщения в t64_admin: {e}", exc_info=True)

    help_type = context.user_data["volunteer_data"].get("help_type", "").lower()
    channel_map = {
        "юридическ": "t64_legal",
        "психологическ": "t64_psych",
        "медицинск": "t64_gen",
        "финансов": "t64_gen",
        "друг": "t64_gen",
        "информацион": "t64_misc",
        "текст": "t64_misc",
        "модерац": "t64_misc",
    }
    for keyword, channel_name in channel_map.items():
        if keyword in help_type:
            try:
                await context.bot.send_message(chat_id=CHANNELS.get(channel_name), text=volunteer_info)
                logger.info(f"Сообщение отправлено в {channel_name}: {volunteer_info}")
            except TelegramError as e:
                logger.error(f"Ошибка Telegram API при отправке сообщения в {channel_name}: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"Непредвиденная ошибка при отправке сообщения в {channel_name}: {e}", exc_info=True)

    await update.message.reply_text(
        "Спасибо за вашу готовность помочь! Ваша заявка принята и будет рассмотрена.",
        reply_markup=FINISH_MENU_KEYBOARD,
    )
    context.user_data.clear()
    return MAIN_MENU

async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message.text
    if message == BACK_BUTTON:
        keyboard = Reply KeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=keyboard,
        )
        return MAIN_MENU
    elif message:
        message_id = generate_message_id(update.effective_user.id)
        try:
            await context.bot.send_message(
                chat_id=CHANNELS.get("t64_misc"),
                text=f"🔒 Анонимное сообщение [{message_id}]:\n\n{message}"
            )
            await update.message.reply_text(
                ANONYMOUS_CONFIRMATION,
                reply_markup=FINISH_MENU_KEYBOARD,
            )
            if "request_type" in context.user_data:
                del context.user_data["request_type"]
            return MAIN_MENU
        except TelegramError as e:
            logger.error(f"Ошибка Telegram API при отправке анонимного сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                "Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return MAIN_MENU
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при отправке анонимного сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                "Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return MAIN_MENU
    else:
        await update.message.reply_text("Пожалуйста, введите ваше сообщение или нажмите '⬅️ Назад'.")
        return ANONYMOUS_MESSAGE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Действие отменено.", reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a telegram message to notify the developer."""
    logger.error(f"Exception while handling an update {update}:", exc_info=context.error)
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"⚠️ Произошла ошибка при обработке обновления `{update}`:\n\n`{context.error}`",
                parse_mode="MarkdownV2",            )
        except TelegramError as e:
            logger.error(f"Ошибка Telegram API при отправке сообщения об ошибке администратору: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при отправке сообщения об ошибке администратору: {e}", exc_info=True)

async def request_legal_docs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик для inline-кнопки запроса консультации по документам."""
    query = update.callback_query
    await query.answer()  # Уведомляет пользователя о получении запроса
    context.user_data["consultation_type"] = "Юридическая"
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=LEGAL_CONSULTATION_INTRO,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
    )
    return CONSULTATION_START

async def plan_surgery_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик для inline-кнопки запроса планирования операции."""
    query = update.callback_query
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=SURGERY_PLANNING_PROMPT,
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
    )
    context.user_data["request_type"] = "Помощь - Планирование операции"
    return TYPING

async def consultation_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text
    if name == "Отмена":
        await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    elif not name:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text("Пожалуйста, введите ваше имя.", reply_markup=keyboard)
        return CONSULTATION_START
    context.user_data["consultation_name"] = name
    consultation_type = context.user_data.get("consultation_type")
    if consultation_type == "Юридическая":
        await update.message.reply_text(LEGAL_SITUATION_PROMPT)
        return CONSULTATION_LEGAL_SITUATION
    elif consultation_type == "Медицинская":
        await update.message.reply_text(MEDICAL_SITUATION_PROMPT)
        return CONSULTATION_MEDICAL_SITUATION
    elif consultation_type == "Психологическая":
        keyboard = ReplyKeyboardMarkup([["Консультация", "Анонимный запрос", BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(PSYCH_CHOICE_PROMPT, reply_markup=keyboard)
        return CONSULTATION_PSYCH_CHOICE
    else:
        await update.message.reply_text("Произошла ошибка при определении типа консультации.")
        return MAIN_MENU

async def consultation_legal_situation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["legal_situation"] = update.message.text
    keyboard = ReplyKeyboardMarkup(YES_NO_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(LEGAL_ASSISTANCE_PROMPT, reply_markup=keyboard)
    return CONSULTATION_LEGAL_CONTACT

async def consultation_legal_assistance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["legal_assistance"] = update.message.text
    await update.message.reply_text(LEGAL_CONTACT_PROMPT)
    return CONSULTATION_LEGAL_CONTACT

async def consultation_legal_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["legal_contact"] = update.message.text
    await update.message.reply_text(CONSULTATION_REQUEST_RECEIVED)
    await send_consultation_request_to_admin(update, context, "Юридическая")
    return ConversationHandler.END

async def consultation_medical_situation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["medical_situation"] = update.message.text
    keyboard = ReplyKeyboardMarkup(YES_NO_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(MEDICAL_REGION_ASSISTANCE_PROMPT, reply_markup=keyboard)
    return CONSULTATION_MEDICAL_ASSISTANCE

async def consultation_medical_assistance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["medical_assistance"] = update.message.text
    await update.message.reply_text(MEDICAL_CONTACT_PROMPT)
    return CONSULTATION_MEDICAL_CONTACT

async def consultation_medical_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["medical_contact"] = update.message.text
    await update.message.reply_text(CONSULTATION_REQUEST_RECEIVED)
    await send_consultation_request_to_admin(update, context, "Медицинская")
    return ConversationHandler.END

async def consultation_psych_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "Консультация":
        await update.message.reply_text(PSYCH_SITUATION_PROMPT)
        return CONSULTATION_PSYCH_SITUATION
    elif choice == "Анонимный запрос":
        await update.message.reply_text(PSYCH_ANONYMOUS_PROMPT)
        return CONSULTATION_PSYCH_ANONYMOUS_MESSAGE
    elif choice == BACK_BUTTON:
        await update.message.reply_text("Вы вернулись в меню психологической помощи.")
        return HELP_MENU
    else:
        await update.message.reply_text(CHOOSE_FROM_MENU)
        return CONSULTATION_PSYCH_CHOICE

async def consultation_psych_situation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["psych_situation"] = update.message.text
    keyboard = ReplyKeyboardMarkup(YES_NO_MAYBE_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(PSYCH_REGION_ASSISTANCE_PROMPT, reply_markup=keyboard)
    return CONSULTATION_PSYCH_ASSISTANCE

async def consultation_psych_assistance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["psych_assistance"] = update.message.text
    await update.message.reply_text(PSYCH_CONTACT_PROMPT)
    return CONSULTATION_PSYCH_CONTACT

async def consultation_psych_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["psych_contact"] = update.message.text
    await update.message.reply_text(CONSULTATION_REQUEST_RECEIVED)
    await send_consultation_request_to_admin(update, context, "Психологическая")
    return ConversationHandler.END

async def consultation_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Подтверждает отправку запроса на консультацию."""
    await update.message.reply_text(
        "Ваш запрос на консультацию отправлен администратору. Пожалуйста, ожидайте ответа.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def consultation_psych_anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text
    if user_text and user_text != BACK_BUTTON:
        try:
            await context.bot.send_message(
                chat_id=CHANNELS.get("t64_psych"),
                text=f"🔒 Анонимный запрос (психология):\n\n{user_text}"
            )
            await update.message.reply_text(
                ANONYMOUS_REQUEST_SENT,
                reply_markup=FINISH_MENU_KEYBOARD,
            )
            return MAIN_MENU
        except TelegramError as e:
            logger.error(f"Ошибка Telegram API при отправке анонимного сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                MESSAGE_SEND_ERROR.format(e),
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return MAIN_MENU
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при отправке анонимного сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                MESSAGE_SEND_ERROR.format(e),
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return MAIN_MENU
    elif user_text == BACK_BUTTON:
        await update.message.reply_text("Вы вернулись к выбору формата консультации.")
        return CONSULTATION_PSYCH_CHOICE
    return CONSULTATION_PSYCH_ANONYMOUS_MESSAGE

async def send_consultation_request_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, consultation_type: str):
    """Отправляет запрос на консультацию администратору."""
    user_data = context.user_data
    message = f"Новый запрос на {consultation_type} консультацию:\n"
    message += f"Имя: {user_data.get('consultation_name', 'не указано')}\n"
    if consultation_type == "Юридическая":
        message += f"Ситуация: {user_data.get('legal_situation', 'не указано')}\n"
        message += f"Поиск адвоката: {user_data.get('legal_assistance', 'не указано')}\n"
        message += f"Контакт: {user_data.get('legal_contact', 'не указано')}\n"
    elif consultation_type == "Медицинская":
        message += f"Ситуация: {user_data.get('medical_situation', 'не указано')}\n"
        message += f"Поиск специалиста в регионе: {user_data.get('medical_assistance', 'не указано')}\n"
        message += f"Контакт: {user_data.get('medical_contact', 'не указано')}\n"
    elif consultation_type == "Психологическая":
        message += f"Ситуация: {user_data.get('psych_situation', 'не указано')}\n"
        message += f"Помощь в регионе: {user_data.get('psych_assistance', 'не указано')}\n"
        message += f"Контакт: {user_data.get('psych_contact', 'не указано')}\n"

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message
        )
    except TelegramError as e:
        logger.error(f"Ошибка Telegram API при отправке запроса на консультацию администратору: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при отправке запроса на консультацию администратору: {e}", exc_info=True)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_menu)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, faq_legal)],
            MEDICAL_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_menu)],
            MEDICAL_GENDER_THERAPY_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_gender_therapy_menu)
            ],
            MEDICAL_FTM_HRT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_ftm_hrt)
            ],
            MEDICAL_MTF_HRT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_mtf_hrt)
            ],
            MEDICAL_SURGERY_PLANNING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_surgery_planning)
            ],
            VOLUNTEER_START_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_start)],
            VOLUNTEER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_name)],
            VOLUNTEER_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_region_handler)],
            VOLUNTEER_HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_help_type_handler)],
            VOLUNTEER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_contact_handler)],
            ANONYMOUS_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, anonymous_message)
            ],
            CONSULTATION_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_start)],
            CONSULTATION_LEGAL_SITUATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_legal_situation)],
            CONSULTATION_LEGAL_ASSISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_legal_assistance)],
            CONSULTATION_LEGAL_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_legal_contact)],
            CONSULTATION_MEDICAL_SITUATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_medical_situation)],
            CONSULTATION_MEDICAL_ASSISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_medical_assistance)],
            CONSULTATION_MEDICAL_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_medical_contact)],
            CONSULTATION_PSYCH_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_psych_choice)],
            CONSULTATION_PSYCH_SITUATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_psych_situation)],
            CONSULTATION_PSYCH_ASSISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_psych_assistance)],
            CONSULTATION_PSYCH_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_psych_contact)],
            CONSULTATION_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_confirm)],
            CONSULTATION_PSYCH_ANONYMOUS_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, consultation_psych_anonymous_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(request_legal_docs_callback, pattern='^request_legal_docs$'))
    application.add_handler(CallbackQueryHandler(plan_surgery_callback, pattern='^plan_surgery$'))
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
