from dotenv import load_dotenv
import os
import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
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
)
from keyboards import (
    MAIN_MENU_BUTTONS,
    HELP_MENU_BUTTONS,
    LEGAL_MENU_BUTTONS,
    MEDICAL_MENU_BUTTONS,
    GENDER_THERAPY_CHOICE_BUTTONS,
    BACK_BUTTON,
    SURGERY_INFO_KEYBOARD,
    VOLUNTEER_HELP_TYPE_KEYBOARD,  # Import the new keyboard
)
from channels import CHANNELS

# Включите логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем состояния разговора
(
    START,
    MAIN_MENU,
    TYPING,  # Одно состояние для ввода текста
    FAQ_LEGAL,
    FAQ_MED,
    VOLUNTEER,  # Одно состояние для волонтерства
    ANONYMOUS_MESSAGE,
    MEDICAL_MENU,
    MEDICAL_GENDER_THERAPY_MENU,
    MEDICAL_FTM_HRT,
    MEDICAL_MTF_HRT,
    MEDICAL_SURGERY_PLANNING,
) = range(12)

# Загрузка переменных окружения из файла .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает разговор и выводит приветственное сообщение с главным меню."""
    await update.message.reply_text(
        START_MESSAGE,
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return MAIN_MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор пользователя в главном меню."""
    user_choice = update.message.text
    if user_choice == "🆘 Попросить о помощи":
        context.user_data["request_type"] = "Помощь"
        await update.message.reply_text(
            HELP_MENU_MESSAGE,
            reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True),
            parse_mode="Markdown",
        )
        return TYPING
    elif user_choice == "➕ Предложить ресурс":
        context.user_data["request_type"] = "Ресурс"
        await update.message.reply_text(RESOURCE_PROMPT_MESSAGE)
        return TYPING
    elif user_choice == "🤝 Стать волонтером":
        context.user_data["request_type"] = "Волонтерство"
        await update.message.reply_text(VOLUNTEER_MESSAGE)
        return VOLUNTEER
    elif user_choice == "💸 Поддержать проект":
        context.user_data["request_type"] = "Донат"
        await update.message.reply_text(
            DONATE_MESSAGE, parse_mode="Markdown", disable_web_page_preview=True
        )
        return TYPING
    elif user_choice == "✉️ Анонимное сообщение":
        context.user_data["request_type"] = "Анонимное сообщение"
        await update.message.reply_text("Пожалуйста, напишите ваше анонимное сообщение:")
        return ANONYMOUS_MESSAGE
    else:
        await update.message.reply_text(CHOOSE_FROM_MENU)
        return MAIN_MENU


async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает ввод текста пользователя для различных запросов."""

    user_text = update.message.text
    request_type = context.user_data.get("request_type", "Сообщение")
    consultation_type = context.user_data.get("consultation_type")
    user_id = update.effective_user.id  # Получаем ID пользователя

    report_admin = f"Новое сообщение от пользователя:\nID: {user_id}\nТип: {request_type}"
    if consultation_type:
        report_admin += f"\nТип консультации: {consultation_type}"
    report_admin += f"\nТекст: {user_text}"

    tasks = []
    if not request_type.startswith("Срочная помощь"):
        # Отправляем сообщение администраторам
        tasks.append(context.bot.send_message(chat_id="t64_admin", text=report_admin))

    if request_type == "Ресурс":
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_misc"), text=user_text))
    elif request_type == "Анонимное сообщение":
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_misc"), text=user_text))
    elif request_type.startswith("Срочная помощь"):
        tasks.append(context.bot.send_message(chat_id="t64_admin", text=user_text))
    elif request_type.startswith("Сообщение о нарушении (юридическое)"):
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_legal"), text=user_text))
    elif request_type.startswith("Юридическая консультация"):
        tasks.append(
            context.bot.send_message(chat_id=CHANNELS.get("t64_legal"), text=f"Запрос на консультацию: {user_text}")
        )
    elif request_type.startswith("Медицинская консультация") or \
            request_type.startswith("Консультация по мужской ГТ") or \
            request_type.startswith("Консультация по женской ГТ") or \
            request_type == "Планирование операции" or \
            request_type == "Планирование ФТМ операции" or \
            request_type == "Планирование МТФ операции":
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_gen"), text=f"Запрос: {user_text}"))
    elif request_type == "Психологическая помощь":
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_psych"), text=user_text))
    elif request_type == "Жилье/финансы":
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_gen"), text=user_text))

    await asyncio.gather(*tasks)

    await update.message.reply_text(
        MESSAGE_SENT_SUCCESS,
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
    )
    return MAIN_MENU


async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор пользователя в меню помощи."""
    user_choice = update.message.text
    if user_choice == BACK_BUTTON:
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
        )
        context.user_data.pop("request_type", None)  # Очищаем тип запроса
        return MAIN_MENU
    else:
        context.user_data["request_type"] = "Помощь - " + user_choice  # Добавляем категорию
        await update.message.reply_text(CHOOSE_HELP_CATEGORY)
        return TYPING


async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает вопросы в разделе юридической помощи."""
    try:
        choice = update.message.text
        if choice == BACK_BUTTON:
            await update.message.reply_text(
                BACK_TO_MAIN_MENU,
                reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
            )
            context.user_data.pop("request_type", None)  # Очищаем тип запроса
            return MAIN_MENU
        elif choice == "🏳️‍🌈 ЛГБТ+ семьи":
            await update.message.reply_text(
                LGBT_FAMILIES_INFO,
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return MAIN_MENU  # Возвращаемся в главное меню
        elif choice == "📝 Как сменить документы":
            response = DOCUMENTS_MESSAGE
            keyboard = ReplyKeyboardMarkup(
                [["Запросить консультацию по смене документов"], [BACK_BUTTON]],
                resize_keyboard=True,
            )
            await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)
            context.user_data["consultation_type"] = "смена документов"
            context.user_data["request_type"] = "Помощь - Юридическая"  # Устанавливаем тип запроса
            return TYPING
        elif choice == "📢 Что такое пропаганда ЛГБТ?":
            response = PROPAGANDA_MESSAGE
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)
            return MAIN_MENU  # Возвращаемся в главное меню
        elif choice == "🗣️ Юридическая консультация":
            await update.message.reply_text(
                CONSULTATION_PROMPT,
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            context.user_data["request_type"] = "Помощь - Юридическая консультация"  # Устанавливаем тип запроса
            return TYPING
        elif choice == "🚨 Сообщить о нарушении":
            await update.message.reply_text(
                REPORT_ABUSE_MESSAGE,
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            context.user_data["request_type"] = "Помощь - Сообщение о нарушении (юридическое)"  # Устанавливаем тип запроса
            return TYPING
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return FAQ_LEGAL
    except Exception as e:
        logger.error(f"Ошибка в faq_legal: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return FAQ_LEGAL


async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор пользователя в медицинском меню."""
    try:
        choice = update.message.text
        if choice == BACK_BUTTON:
            await update.message.reply_text(
                BACK_TO_MAIN_MENU,
                reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
            )
            context.user_data.pop("request_type", None)  # Очищаем тип запроса
            return MAIN_MENU
        elif choice == "🗣️ Медицинская консультация":
            await update.message.reply_text(CONSULTATION_PROMPT)
            context.user_data["request_type"] = "Помощь - Медицинская консультация"
            return TYPING
        elif choice == "💉HRT":
            await update.message.reply_text(
                GENDER_THERAPY_MESSAGE,
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    GENDER_THERAPY_CHOICE_BUTTONS, resize_keyboard=True
                ),
            )
            return MEDICAL_GENDER_THERAPY_MENU
        elif choice == "❓ F64":
            await update.message.reply_text(
                F64_MESSAGE,
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return MAIN_MENU  # Возвращаемся в главное меню
        elif choice == "⚕️ Операции":
            await update.message.reply_text(
                SURGERY_INFO_MESSAGE,
                parse_mode="Markdown",
                reply_markup=SURGERY_INFO_KEYBOARD,
            )
            return MEDICAL_SURGERY_PLANNING  # Переходим в новое состояние для планирования
        elif choice == "🗓️ Спланировать операцию":
            await update.message.reply_text(SURGERY_PLANNING_PROMPT)
            context.user_data["request_type"] = "Помощь - Планирование операции"
            return TYPING
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return MEDICAL_MENU
    except Exception as e:
        logger.error(f"Ошибка в medical_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MEDICAL_MENU


async def medical_gender_therapy_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Обрабатывает выбор направления гормональной терапии."""
    try:
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
                    ],
                    resize_keyboard=True,
                ),
            )
            return MEDICAL_MTF_HRT

        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return MEDICAL_GENDER_THERAPY_MENU
    except Exception as e:
        logger.error(f"Ошибка в medical_gender_therapy_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MEDICAL_GENDER_THERAPY_MENU


async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает вопросы по маскулинизирующей ГТ."""
    try:
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
            return MEDICAL_FTM_HRT  # Остаемся в этом состоянии до выбора
        elif choice == "Запросить консультацию по мужской ГТ" or choice == "Консультация":
            await update.message.reply_text(
                CONSULTATION_PROMPT,
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            context.user_data["consultation_type"] = "мужская ГТ"
            context.user_data["request_type"] = "Помощь - Консультация"  # Устанавливаем тип запроса
            return TYPING
        elif choice == "Я понимаю риски, скачать гайд":
            link = DIY_HRT_GUIDE_LINK
            file_name = DIY_HRT_GUIDE_NAME
            await update.message.reply_text(
                f"Вы можете скачать гайд по DIY ГТ: [{file_name}]({link})",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                ),
                disable_web_page_preview=True,
            )
            return MEDICAL_FTM_HRT  # Возвращаемся в это состояние
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return MEDICAL_FTM_HRT
    except Exception as e:
        logger.error(f"Ошибка в medical_ftm_hrt: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MEDICAL_FTM_HRT


async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает вопросы по феминизирующей ГТ."""
    try:
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
            return MEDICAL_MTF_HRT  # Остаемся в этом состоянии до выбора
        elif choice == "Запросить консультацию по женской ГТ" or choice == "Консультация":
            await update.message.reply_text(
                CONSULTATION_PROMPT,
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            context.user_data["consultation_type"] = "женская ГТ"
            context.user_data["request_type"] = "Помощь - Консультация"  # Устанавливаем тип запроса
            return TYPING
        elif choice == "Я понимаю риски, скачать гайд":
            link = DIY_HRT_GUIDE_LINK
            file_name = DIY_HRT_GUIDE_NAME
            await update.message.reply_text(
                f"Вы можете скачать гайд по DIY ГТ: [{file_name}]({link})",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    [["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                ),
                disable_web_page_preview=True,
            )
            return MEDICAL_MTF_HRT  # Возвращаемся в это состояние
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return MEDICAL_MTF_HRT
    except Exception as e:
        logger.error(f"Ошибка в medical_mtf_hrt: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MEDICAL_MTF_HRT


async def medical_surgery_planning(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Обрабатывает вопросы по планированию операций."""
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_menu(update, context)
    elif choice == "ФТМ Операции":
        await update.message.reply_text(
            FTM_SURGERY_INFO,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return MEDICAL_MENU  # Возвращаемся в мед. меню
    elif choice == "МТФ Операции":
        await update.message.reply_text(
            MTF_SURGERY_INFO,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return MEDICAL_MENU  # Возвращаемся в мед. меню
    elif choice == "🗓️ Спланировать операцию":
        await update.message.reply_text(SURGERY_PLANNING_PROMPT)
        context.user_data["request_type"] = "Помощь - Планирование операции"
        return TYPING
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return MEDICAL_SURGERY_PLANNING


async def volunteer_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало сбора информации о волонтере."""
    await update.message.reply_text("Как вас зовут?")
    context.user_data["volunteer_data"] = {}  # Создаем словарь для данных волонтера
    return VOLUNTEER


async def volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает имя волонтера."""
    context.user_data["volunteer_data"]["name"] = update.message.text
    await update.message.reply_text("Из какого вы региона?")
    return VOLUNTEER


async def volunteer_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает регион волонтера."""
    context.user_data["volunteer_data"]["region"] = update.message.text
    await update.message.reply_text(
        "Выберите тип помощи, которую вы можете предложить:",
        reply_markup=VOLUNTEER_HELP_TYPE_KEYBOARD,
    )
    return VOLUNTEER


async def volunteer_help_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает тип помощи, которую может оказать волонтер."""
    context.user_data["volunteer_data"]["help_type"] = update.message.text
    user_contact = update.effective_user.username
    if user_contact:
        context.user_data["volunteer_data"]["contact"] = f"@{user_contact}"
    else:
        context.user_data["volunteer_data"]["contact"] = "не указан"
    await update.message.reply_text("Как с вами можно связаться (Telegram, email)?")
    return VOLUNTEER


async def volunteer_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает контактные данные волонтера и завершает сбор."""
    context.user_data["volunteer_data"]["contact_other"] = update.message.text
    user_id = update.effective_user.id  # Получаем ID пользователя
    volunteer_info = f"""Новый волонтер!
ID: {user_id}
Имя: {context.user_data["volunteer_data"].get("name", "не указано")}
Регион: {context.user_data["volunteer_data"].get("region", "не указано")}
Тип помощи: {context.user_data["volunteer_data"].get("help_type", "не указано")}
Контакт (Telegram): {context.user_data["volunteer_data"].get("contact", "не указано")}
Контакт (Другое): {context.user_data["volunteer_data"].get("contact_other", "не указано")}"""

    tasks = [context.bot.send_message(chat_id="t64_admin", text=volunteer_info)]

    help_type = context.user_data["volunteer_data"].get("help_type", "").lower()
    if "юридическ" in help_type:
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_legal"), text=volunteer_info))
    elif "психологическ" in help_type:
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_psych"), text=volunteer_info))
    elif (
        "медицинск" in help_type
        or "финансов" in help_type
        or "друг" in help_type
    ):
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_gen"), text=volunteer_info))
    elif (
        "информацион" in help_type
        or "текст" in help_type
        or "модерац" in help_type
    ):
        tasks.append(context.bot.send_message(chat_id=CHANNELS.get("t64_misc"), text=volunteer_info))

    await asyncio.gather(*tasks)

    await update.message.reply_text(
        "Спасибо за вашу готовность помочь! Мы свяжемся с вами в ближайшее время.",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
    )
    context.user_data.pop("volunteer_data", None)  # Очищаем данные волонтера
    context.user_data.pop("request_type", None)  # Очищаем тип запроса
    return MAIN_MENU


async def anonymous_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Получает и пересылает анонимное сообщение."""
    message = update.message.text
    user_id = update.effective_user.id  # Получаем ID пользователя
    await context.bot.send_message(
        chat_id=CHANNELS.get("t64_misc"), text=f"Анонимное сообщение от ID {user_id}: {message}"
    )
    await update.message.reply_text(
        "Ваше анонимное сообщение отправлено администраторам.",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
    )
    context.user_data.pop("request_type", None)  # Очищаем тип запроса
    return MAIN_MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет текущий разговор."""
    await update.message.reply_text(
        CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()  # Очищаем все данные пользователя
    return MAIN_MENU  # Возвращаемся в главное меню


def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(TOKEN).build()

    # Обработчик разговоров
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, faq_legal)],
            FAQ_MED: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_menu)],
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
            VOLUNTEER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_name),
                MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_region),
                MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_help_type),
                MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_contact),
            ],
            ANONYMOUS_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, anonymous_message)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()

