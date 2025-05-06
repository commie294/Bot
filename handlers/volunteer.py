import asyncio
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from bot_responses import CANCEL_MESSAGE
from keyboards import VOLUNTEER_START_KEYBOARD, VOLUNTEER_HELP_TYPE_KEYBOARD, FINISH_MENU_KEYBOARD, REGIONS
from utils.message_utils import load_channels, update_stats, check_rate_limit
from utils.constants import BotState

logger = logging.getLogger(__name__)

async def ask_volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_rate_limit(update, context):
        return BotState.VOLUNTEER_CONFIRM_START
    await update.message.reply_text(
        "📋 *Шаг 1/4:* Пожалуйста, введите ваше имя\\.",
        reply_markup=ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True),
        parse_mode="MarkdownV2"
    )
    return BotState.VOLUNTEER_NAME

async def get_volunteer_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_rate_limit(update, context):
        return BotState.VOLUNTEER_NAME
    name = update.message.text
    if not name:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text(
            "Пожалуйста, введите ваше имя\\.",
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.VOLUNTEER_NAME
    context.user_data["volunteer_data"] = {"name": name}
    keyboard = ReplyKeyboardMarkup(REGIONS + [["Отмена"]], resize_keyboard=True)
    await update.message.reply_text(
        "📍 *Шаг 2/4:* Из какого вы региона\\?",
        reply_markup=keyboard,
        parse_mode="MarkdownV2"
    )
    return BotState.VOLUNTEER_REGION

async def volunteer_help_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_rate_limit(update, context):
        return BotState.VOLUNTEER_REGION
    region = update.message.text
    if region == "Отмена":
        await update.message.reply_text(
            CANCEL_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="MarkdownV2"
        )
        context.user_data.clear()
        return ConversationHandler.END
    if not region:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text(
            "Пожалуйста, введите ваш регион\\.",
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.VOLUNTEER_REGION
    context.user_data["volunteer_data"]["region"] = region
    await update.message.reply_text(
        "🤝 *Шаг 3/4:* Чем вы готовы помочь\\?",
        reply_markup=VOLUNTEER_HELP_TYPE_KEYBOARD,
        parse_mode="MarkdownV2"
    )
    return BotState.VOLUNTEER_HELP_TYPE

async def volunteer_contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_rate_limit(update, context):
        return BotState.VOLUNTEER_HELP_TYPE
    help_type = update.message.text
    if help_type == "Отмена":
        await update.message.reply_text(
            CANCEL_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="MarkdownV2"
        )
        context.user_data.clear()
        return ConversationHandler.END
    context.user_data["volunteer_data"]["help_type"] = help_type
    user_contact = update.effective_user.username
    context.user_data["volunteer_data"]["contact"] = f"@{user_contact}" if user_contact else "не указан"
    keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
    await update.message.reply_text(
        "📞 *Шаг 4/4:* Как с вами можно связаться \\(Telegram, email\\)\\?",
        reply_markup=keyboard,
        parse_mode="MarkdownV2"
    )
    return BotState.VOLUNTEER_CONTACT

async def volunteer_finish_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_rate_limit(update, context):
        return BotState.VOLUNTEER_CONTACT
    contact_other = update.message.text
    if contact_other == "Отмена":
        await update.message.reply_text(
            CANCEL_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="MarkdownV2"
        )
        context.user_data.clear()
        return ConversationHandler.END
    if not contact_other:
        keyboard = ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True)
        await update.message.reply_text(
            "Пожалуйста, введите ваши контактные данные\\.",
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.VOLUNTEER_CONTACT
    context.user_data["volunteer_data"]["contact_other"] = contact_other
    user_id = update.effective_user.id
    volunteer_info = f"""*Новый волонтёр!*
*ID:* {user_id}
*Имя:* {context.user_data["volunteer_data"].get("name", "не указано")}
*Регион:* {context.user_data["volunteer_data"].get("region", "не указано")}
*Тип помощи:* {context.user_data["volunteer_data"].get("help_type", "не указано")}
*Контакт \\(Telegram\\):* {context.user_data["volunteer_data"].get("contact", "не указано")}
*Контакт \\(Другое\\):* {contact_other}"""

    channels = load_channels()
    channel_map = {
        "юридическ": "t64_legal",
        "психологическ": "t64_psych",
        "медицинск": "t64_gen",
        "финансов": "t64_gen",
        "техническ": "t64_gen",
        "друг": "t64_gen",
        "информацион": "t64_misc",
        "текст": "t64_misc",
        "модерац": "t64_misc",
    }

    tasks = [context.bot.send_message(chat_id=channels["t64_admin"], text=volunteer_info, parse_mode="MarkdownV2")]
    help_type = context.user_data["volunteer_data"].get("help_type", "").lower()
    for keyword, channel_name in channel_map.items():
        if keyword in help_type:
            tasks.append(context.bot.send_message(chat_id=channels[channel_name], text=volunteer_info, parse_mode="MarkdownV2"))

    try:
        await asyncio.gather(*tasks)
        logger.info(f"Данные волонтёра отправлены: {volunteer_info}")
    except TelegramError as e:
        logger.error(f"Ошибка отправки данных волонтёра: {e}", exc_info=True)

    await update.message.reply_text(
        "Спасибо за вашу готовность помочь\\! Ваша заявка принята и будет рассмотрена\\.",
        reply_markup=FINISH_MENU_KEYBOARD,
        parse_mode="MarkdownV2"
    )
    update_stats(user_id, "volunteer_registration")
    context.user_data.clear()
    return BotState.MAIN_MENU
