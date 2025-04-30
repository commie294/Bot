import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from bot_responses import CANCEL_MESSAGE, VOLUNTEER_MESSAGE, FINISH_MENU_KEYBOARD
from keyboards import VOLUNTEER_HELP_TYPE_KEYBOARD, VOLUNTEER_START_KEYBOARD
from channels import CHANNELS

logger = logging.getLogger(__name__)

async def volunteer_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик для inline-кнопки 'Стать волонтером'."""
    query = update.callback_query
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=VOLUNTEER_MESSAGE,
        reply_markup=VOLUNTEER_START_KEYBOARD
    )
    return 6  # VOLUNTEER_CONFIRM_START

async def ask_volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Пожалуйста, введите ваше имя.")
    return 7  # VOLUNTEER_NAME

async def get_volunteer_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text
    if name == "Отмена":
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return -1  # ConversationHandler.END
    elif not name:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text("Пожалуйста, введите ваше имя.", reply_markup=keyboard)
        return 7  # VOLUNTEER_NAME
    context.user_data["volunteer_data"] = {"name": name}
    keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
    await update.message.reply_text("Из какого вы региона?", reply_markup=keyboard)
    return 8  # VOLUNTEER_REGION

async def volunteer_help_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    region = update.message.text
    if region == "Отмена":
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return -1  # ConversationHandler.END
    elif not region:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text("Пожалуйста, введите ваш регион.", reply_markup=keyboard)
        return 8  # VOLUNTEER_REGION
    context.user_data["volunteer_data"]["region"] = region
    await update.message.reply_text(
        "Чем вы готовы помочь?",
        reply_markup=VOLUNTEER_HELP_TYPE_KEYBOARD,
    )
    return 9  # VOLUNTEER_HELP_TYPE

async def volunteer_contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    help_type = update.message.text
    if help_type == "Отмена":
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return -1  # ConversationHandler.END
    context.user_data["volunteer_data"]["help_type"] = help_type
    user_contact = update.effective_user.username
    context.user_data["volunteer_data"]["contact"] = f"@{user_contact}" if user_contact else "не указан"
    keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
    await update.message.reply_text("Как с вами можно связаться (Telegram, email)?", reply_markup=keyboard)
    return 10  # VOLUNTEER_CONTACT

async def volunteer_finish_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact_other = update.message.text
    if contact_other == "Отмена":
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return -1  # ConversationHandler.END
    elif not contact_other:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text("Пожалуйста, введите ваши контактные данные.", reply_markup=keyboard)
        return 10  # VOLUNTEER_CONTACT
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
    return 1  # MAIN_MENU
