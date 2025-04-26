from dotenv import load_dotenv
import os
import asyncio
import hashlib
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes
import logging
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
    DIY_HRT_GUIDE_LINK,
    DIY_HRT_GUIDE_NAME,
    SURGERY_PLANNING_PROMPT,
    FAREWELL_MESSAGE,
    ANONYMOUS_CONFIRMATION
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
)
from channels import CHANNELS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    DONE,
) = range(17)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
HASH_SALT = os.getenv("HASH_SALT", "default_salt")

def generate_message_id(user_id: int) -> str:
    """Генерирует хеш для анонимной идентификации сообщений"""
    return hashlib.sha256(f"{HASH_SALT}_{user_id}_{os.urandom(16)}".encode()).hexdigest()[:8]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        START_MESSAGE,
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = update.message.text
    if user_choice == "🆘 Попросить о помощи":
        await update.message.reply_text(
            HELP_MENU_MESSAGE,
            reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [["✅ Готово"]], resize_keyboard=True),
            parse_mode="Markdown",
        )
        return HELP_MENU
    elif user_choice == "➕ Предложить ресурс":
        context.user_data["request_type"] = "Ресурс"
        await update.message.reply_text(RESOURCE_PROMPT_MESSAGE, reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True))
        return TYPING
    elif user_choice == "🤝 Стать волонтером":
        await update.message.reply_text(VOLUNTEER_MESSAGE, reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True))
        return VOLUNTEER_START_STATE
    elif user_choice == "💸 Поддержать проект":
        context.user_data["request_type"] = "Донат"
        await update.message.reply_text(
            DONATE_MESSAGE, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True)
        )
        return MAIN_MENU
    elif user_choice == "✉️ Анонимное сообщение":
        await update.message.reply_text(
            "Пожалуйста, напишите ваше анонимное сообщение:",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        context.user_data["request_type"] = "Анонимное сообщение"
        return ANONYMOUS_MESSAGE
    elif user_choice == "✅ Готово":
        await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text(CHOOSE_FROM_MENU)
        return MAIN_MENU

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = update.message.text
    if user_choice == BACK_BUTTON:
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
        )
        return MAIN_MENU
    elif user_choice == "🚨 Срочная помощь":
        context.user_data["request_type"] = "Срочная помощь"
        await update.message.reply_text(EMERGENCY_MESSAGE, reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True))
        return TYPING
    elif user_choice == "🏠 Жилье/финансы":
        context.user_data["request_type"] = "Жилье/финансы"
        await update.message.reply_text(HOUSING_FINANCE_PROMPT, reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True))
        return TYPING
    elif user_choice == "🧠 Психологическая помощь":
        context.user_data["request_type"] = "Психологическая помощь"
        await update.message.reply_text(PSYCHOLOGICAL_HELP_PROMPT, reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True))
        return TYPING
    elif user_choice == "🩺 Медицинская помощь":
        await update.message.reply_text(
            "Выберите категорию медицинской помощи:",
            reply_markup=ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [["✅ Готово"]], resize_keyboard=True),
        )
        return MEDICAL_MENU
    elif user_choice == "⚖️ Юридическая помощь":
        await update.message.reply_text(
            "Выберите категорию юридической помощи:",
            reply_markup=ReplyKeyboardMarkup(LEGAL_MENU_BUTTONS + [["✅ Готово"]], resize_keyboard=True),
        )
        return FAQ_LEGAL
    elif user_choice == "✅ Готово":
        await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text(CHOOSE_HELP_CATEGORY)
        return HELP_MENU

async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text
    request_type = context.user_data.get("request_type", "Сообщение")

    # Для анонимных сообщений используем отдельную обработку
    if request_type == "Анонимное сообщение":
        return await anonymous_message(update, context)

    user_id = update.effective_user.id
    channel_mapping = {
        "Ресурс": "t64_misc",
        "Срочная помощь": "t64_gen",
        "Помощь - Сообщение о нарушении (юридическое)": "t64_legal",
        "Помощь - Юридическая консультация": "t64_legal",
        "Помощь - Медицинская консультация": "t64_gen",
        "Помощь - Консультация по мужской ГТ": "t64_gen",
        "Помощь - Консультация по женской ГТ": "t64_gen",
        "Помощь - Планирование операции": "t64_gen",
        "Помощь - Планирование ФТМ операции": "t64_gen",
        "Помощь - Планирование МТФ операции": "t64_gen",
        "Психологическая помощь": "t64_psych",
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
                reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True),
            )
            return MAIN_MENU
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                MESSAGE_SEND_ERROR,
                reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True),
            )
            return MAIN_MENU
    else:
        await update.message.reply_text(
            "Произошла ошибка при обработке вашего запроса.",
            reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True),
        )
        return MAIN_MENU

async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message.text
    message_id = generate_message_id(update.effective_user.id)

    try:
        await context.bot.send_message(
            chat_id=CHANNELS.get("t64_misc"),
            text=f"🔒 Анонимное сообщение [{message_id}]:\n\n{message}"
        )
        await update.message.reply_text(
            ANONYMOUS_CONFIRMATION,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        # Очищаем временные данные
        if "request_type" in context.user_data:
            del context.user_data["request_type"]
        return MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка при отправке анонимного сообщения: {e}", exc_info=True)
        await update.message.reply_text(
            "Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        return MAIN_MENU

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
        )
        return MAIN_MENU
    elif choice == "🏳️‍🌈 ЛГБТ+ семьи":
        await update.message.reply_text(
            LGBT_FAMILIES_INFO,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        return FAQ_LEGAL
    elif choice == "📝 Как сменить документы":
        response = DOCUMENTS_MESSAGE
        keyboard = ReplyKeyboardMarkup(
            [["Запросить консультацию по смене документов"], [BACK_BUTTON], ["✅ Готово"]],
            resize_keyboard=True,
        )
        await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)
        context.user_data["request_type"] = "Помощь - Юридическая консультация (смена документов)"
        return TYPING
    elif choice == "📢 Что такое пропаганда ЛГБТ?":
        response = PROPAGANDA_MESSAGE
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True)
        await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)
        return FAQ_LEGAL
    elif choice == "🗣️ Юридическая консультация":
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        context.user_data["request_type"] = "Помощь - Юридическая консультация"
        return TYPING
    elif choice == "🚨 Сообщить о нарушении":
        await update.message.reply_text(
            REPORT_ABUSE_MESSAGE,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        context.user_data["request_type"] = "Помощь - Сообщение о нарушении (юридическое)"
        return TYPING
    elif choice == "✅ Готово":
        await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return FAQ_LEGAL

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        await update.message.reply_text(
            HELP_MENU_MESSAGE,
            reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [["✅ Готово"]], resize_keyboard=True),
        )
        return HELP_MENU
    elif choice == "🗣️ Медицинская консультация":
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        context.user_data["request_type"] = "Помощь - Медицинская консультация"
        return TYPING
    elif choice == "💉HRT":
        await update.message.reply_text(
            GENDER_THERAPY_MESSAGE,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                GENDER_THERAPY_CHOICE_BUTTONS + [["✅ Готово"]], resize_keyboard=True
            ),
        )
        return MEDICAL_GENDER_THERAPY_MENU
    elif choice == "❓ F64":
        await update.message.reply_text(
            F64_MESSAGE,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        return MEDICAL_MENU
    elif choice == "⚕️ Операции":
        await update.message.reply_text(
            SURGERY_INFO_MESSAGE,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(SURGERY_INFO_KEYBOARD.keyboard + [["✅ Готово"]], resize_keyboard=True),
        )
        return MEDICAL_SURGERY_PLANNING
    elif choice == "✅ Готово":
        await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_MENU

async def medical_gender_therapy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_menu(update, context)
    elif choice == "T":
        await update.message.reply_text(
            MASCULINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["DIY"],
                    ["Запросить консультацию по мужской ГТ"],
                    [BACK_BUTTON],
                    ["✅ Готово"],
                ],
                resize_keyboard=True,
            ),
        )
        return MEDICAL_FTM_HRT
    elif choice == "E":
        await update.message.reply_text(
            FEMINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["DIY"],
                    ["Запросить консультацию по женской ГТ"],
                    [BACK_BUTTON],
                    ["✅ Готово"],
                ],
                resize_keyboard=True,
            ),
        )
        return MEDICAL_MTF_HRT
    elif choice == "✅ Готово":
        await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_GENDER_THERAPY_MENU

async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_gender_therapy_menu(update, context)
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True
        )
        await update.message.reply_text(
            DIY_HRT_WARNING, parse_mode="Markdown", reply_markup=keyboard
        )
        return MEDICAL_FTM_HRT
    elif choice == "Запросить консультацию по мужской ГТ":
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        context.user_data["request_type"] = "Помощь - Консультация по мужской ГТ"
        return TYPING
    elif choice == "Я понимаю риски, скачать гайд":
        link = DIY_HRT_GUIDE_LINK
        file_name = DIY_HRT_GUIDE_NAME
        await update.message.reply_text(
            f"Вы можете скачать гайд по DIY ГТ: [{file_name}]({link})",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON], ["✅ Готово"]],
                resize_keyboard=True,
            ),
            disable_web_page_preview=True,
        )
        return MEDICAL_FTM_HRT
    elif choice == "✅ Готово":
        return await medical_gender_therapy_menu(update, context)
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_FTM_HRT

async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_gender_therapy_menu(update, context)
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True
        )
        await update.message.reply_text(
            DIY_HRT_WARNING, parse_mode="Markdown", reply_markup=keyboard
        )
        return MEDICAL_MTF_HRT
    elif choice == "Запросить консультацию по женской ГТ":
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        context.user_data["request_type"] = "Помощь - Консультация по женской ГТ"
        return TYPING
    elif choice == "Я понимаю риски, скачать гайд":
        link = DIY_HRT_GUIDE_LINK
        file_name = DIY_HRT_GUIDE_NAME
        await update.message.reply_text(
            f"Вы можете скачать гайд по DIY ГТ: [{file_name}]({link})",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [["Запросить консультацию по женской ГТ"], [BACK_BUTTON], ["✅ Готово"]],
                resize_keyboard=True,
            ),
            disable_web_page_preview=True,
        )
        return MEDICAL_MTF_HRT
    elif choice == "✅ Готово":
        return await medical_gender_therapy_menu(update, context)
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_MTF_HRT

async def medical_surgery_planning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_menu(update, context)
    elif choice == "ФТМ Операции":
        await update.message.reply_text(
            FTM_SURGERY_INFO,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        return MEDICAL_SURGERY_PLANNING
    elif choice == "МТФ Операции":
        await update.message.reply_text(
            MTF_SURGERY_INFO,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        return MEDICAL_SURGERY_PLANNING
    elif choice == "🗓️ Спланировать операцию":
        await update.message.reply_text(
            SURGERY_PLANNING_PROMPT,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        context.user_data["request_type"] = "Помощь - Планирование операции"
        return TYPING
    elif choice == "✅ Готово":
        return await medical_menu(update, context)
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_SURGERY_PLANNING

async def volunteer_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Как к вам обращаться?", reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True))
    return VOLUNTEER_NAME

async def volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.effective_user.id} entered volunteer_name: {update.message.text}")
    context.user_data["volunteer_data"] = {"name": update.message.text}
    await update.message.reply_text("Из какого вы региона?", reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True))
    return VOLUNTEER_REGION

async def volunteer_region_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.effective_user.id} entered volunteer_region: {update.message.text}, current user_data: {context.user_data}")
    context.user_data["volunteer_data"]["region"] = update.message.text
    await update.message.reply_text(
        "Чем вы готовы помочь?",
        reply_markup=VOLUNTEER_HELP_TYPE_KEYBOARD,
    )
    return VOLUNTEER_HELP_TYPE

async def volunteer_help_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["volunteer_data"]["help_type"] = update.message.text
    user_contact = update.effective_user.username
    context.user_data["volunteer_data"]["contact"] = f"@{user_contact}" if user_contact else "не указан"
    await update.message.reply_text("Как с вами можно связаться (Telegram, email)?", reply_markup=ReplyKeyboardMarkup([["✅ Готово"]], resize_keyboard=True))
    return VOLUNTEER_CONTACT

async def volunteer_contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"CHANNELS['t64_admin']: {CHANNELS.get('t64_admin')}")
    context.user_data["volunteer_data"]["contact_other"] = update.message.text
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
    except Exception as e:
        logger.error(f"Ошибка при отправке в t64_admin: {e}")

    help_type = context.user_data["volunteer_data"].get("help_type", "").lower()
    if "юридическ" in help_type:
        try:
            await context.bot.send_message(chat_id=CHANNELS.get("t64_legal"), text=volunteer_info)
        except Exception as e:
            logger.error(f"Ошибка при отправке в t64_legal: {e}")
    elif "психологическ" in help_type:
        try:
            await context.bot.send_message(chat_id=CHANNELS.get("t64_psych"), text=volunteer_info)
        except Exception as e:
            logger.error(f"Ошибка при отправке в t64_psych: {e}")
    elif "медицинск" in help_type or "финансов" in help_type or "друг" in help_type:
        try:
            await context.bot.send_message(chat_id=CHANNELS.get("t64_gen"), text=volunteer_info)
        except Exception as e:
            logger.error(f"Ошибка при отправке в t64_gen: {e}")
    elif "информацион" in help_type or "текст" in help_type or "модерац" in help_type:
        try:
            await context.bot.send_message(chat_id=CHANNELS.get("t64_misc"), text=volunteer_info)
        except Exception as e:
            logger.error(f"Ошибка при отправке в t64_misc: {e}")

    await update.message.reply_text(
        "Спасибо за вашу готовность помочь! Ваша заявка принята и будет рассмотрена.",
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
    )
    context.user_data.clear()
    return MAIN_MENU

async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message.text
    message_id = generate_message_id(update.effective_user.id)

    try:
        await context.bot.send_message(
            chat_id=CHANNELS.get("t64_misc"),
            text=f"🔒 Анонимное сообщение [{message_id}]:\n\n{message}"
        )
        await update.message.reply_text(
            ANONYMOUS_CONFIRMATION,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        # Очищаем временные данные
        if "request_type" in context.user_data:
            del context.user_data["request_type"]
        return MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка при отправке анонимного сообщения: {e}", exc_info=True)
        await update.message.reply_text(
            "Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON], ["✅ Готово"]], resize_keyboard=True),
        )
        return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Действие отменено.", reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(TOKEN).build()

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
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()

