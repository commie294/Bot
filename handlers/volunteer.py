import asyncio
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError
from telegram.helpers import escape_markdown
from bot_responses import CANCEL_MESSAGE
from keyboards import VOLUNTEER_START_KEYBOARD, VOLUNTEER_HELP_TYPE_KEYBOARD, FINISH_MENU_KEYBOARD, REGIONS
from utils.message_utils import load_channels, update_stats, check_rate_limit
from utils.constants import BotState

logger = logging.getLogger(__name__)

async def ask_volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "volunteer_start":
            await query.message.edit_text(
                escape_markdown("📋 *Шаг 1/4:* Пожалуйста, введите ваше имя.", version=2),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="cancel_volunteer")]]),
                parse_mode="MarkdownV2"
            )
            return BotState.VOLUNTEER_NAME
        elif query.data == "back_to_main":
            await query.message.edit_text(
                escape_markdown("Действие отменено.", version=2),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
                parse_mode="MarkdownV2"
            )
            context.user_data.clear()
            return BotState.MAIN_MENU
    elif update.message and update.message.text == "Отмена":
        await update.message.reply_text(
            CANCEL_MESSAGE,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
            parse_mode="MarkdownV2"
        )
        context.user_data.clear()
        return ConversationHandler.END
    return BotState.VOLUNTEER_CONFIRM_START

async def get_volunteer_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        region = query.data.replace("region_", "") # Получаем регион из callback_data
        if region == "другой":
            await query.message.edit_text(
                escape_markdown("📍 *Шаг 2/4:* Пожалуйста, введите ваш регион.", version=2),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="cancel_volunteer")]]),
                parse_mode="MarkdownV2"
            )
            context.user_data["awaiting_region_input"] = True
            return BotState.VOLUNTEER_REGION
        elif region == "отмена_регион":
            await query.message.edit_text(
                CANCEL_MESSAGE,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
                parse_mode="MarkdownV2"
            )
            context.user_data.clear()
            return ConversationHandler.END
        else:
            context.user_data["volunteer_data"]["region"] = escape_markdown(region, version=2)
            help_keyboard = [[InlineKeyboardButton(text, callback_data=f"help_type_{text}")] for row in VOLUNTEER_HELP_TYPE_KEYBOARD.inline_keyboard for text in row]
            help_keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_volunteer")])
            await query.message.edit_text(
                escape_markdown("🤝 *Шаг 3/4:* Чем вы готовы помочь?", version=2),
                reply_markup=InlineKeyboardMarkup(help_keyboard),
                parse_mode="MarkdownV2"
            )
            return BotState.VOLUNTEER_HELP_TYPE
    elif update.message and context.user_data.get("awaiting_region_input"):
        region_text = update.message.text
        if region_text == "Отмена":
            await update.message.reply_text(
                CANCEL_MESSAGE,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
                parse_mode="MarkdownV2"
            )
            context.user_data.clear()
            return ConversationHandler.END
        context.user_data["volunteer_data"]["region"] = escape_markdown(region_text, version=2)
        help_keyboard = [[InlineKeyboardButton(text, callback_data=f"help_type_{text}")] for row in VOLUNTEER_HELP_TYPE_KEYBOARD.inline_keyboard for text in row]
        help_keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_volunteer")])
        await update.message.reply_text(
            escape_markdown("🤝 *Шаг 3/4:* Чем вы готовы помочь?", version=2),
            reply_markup=InlineKeyboardMarkup(help_keyboard),
            parse_mode="MarkdownV2"
        )
        del context.user_data["awaiting_region_input"]
        return BotState.VOLUNTEER_HELP_TYPE
    elif update.message and update.message.text:
        name = update.message.text
        context.user_data["volunteer_data"] = {"name": escape_markdown(name, version=2)}
        regions_keyboard = [[InlineKeyboardButton(text, callback_data=f"region_{text}")] for row in REGIONS for text in row]
        regions_keyboard.append([InlineKeyboardButton("Другой регион", callback_data="region_другой")])
        regions_keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_volunteer")])
        await update.message.reply_text(
            escape_markdown("📍 *Шаг 2/4:* Из какого вы региона?", version=2),
            reply_markup=InlineKeyboardMarkup(regions_keyboard),
            parse_mode="MarkdownV2"
        )
        return BotState.VOLUNTEER_REGION
    return BotState.VOLUNTEER_NAME

async def volunteer_help_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "cancel_volunteer":
            await query.message.edit_text(
                CANCEL_MESSAGE,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
                parse_mode="MarkdownV2"
            )
            context.user_data.clear()
            return ConversationHandler.END
        help_type = query.data.replace("help_type_", "")
        context.user_data["volunteer_data"]["help_type"] = escape_markdown(help_type, version=2)
        user_contact = update.effective_user.username
        context.user_data["volunteer_data"]["contact"] = f"@{user_contact}" if user_contact else "не указан"
        await query.message.edit_text(
            escape_markdown("📞 *Шаг 4/4:* Как с вами можно связаться (Telegram, email)?", version=2),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="cancel_volunteer")]]),
            parse_mode="MarkdownV2"
        )
        return BotState.VOLUNTEER_CONTACT
    return BotState.VOLUNTEER_HELP_TYPE

async def volunteer_contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        contact_other = update.message.text
        if contact_other == "Отмена":
            await update.message.reply_text(
                CANCEL_MESSAGE,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
                parse_mode="MarkdownV2"
            )
            context.user_data.clear()
            return ConversationHandler.END
        if not contact_other:
            await update.message.reply_text(
                escape_markdown("Пожалуйста, введите ваши контактные данные.", version=2),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="cancel_volunteer")]]),
                parse_mode="MarkdownV2"
            )
            return BotState.VOLUNTEER_CONTACT
        context.user_data["volunteer_data"]["contact_other"] = escape_markdown(contact_other, version=2)
        user_id = update.effective_user.id
        name = context.user_data["volunteer_data"].get("name", "не указано")
        region = context.user_data["volunteer_data"].get("region", "не указано")
        help_type = context.user_data["volunteer_data"].get("help_type", "не указано")
        contact = context.user_data["volunteer_data"].get("contact", "не указано")
        contact_other = context.user_data["volunteer_data"].get("contact_other", "не указано")
        volunteer_info = f"""*Новый волонтёр!*
*ID:* {user_id}
*Имя:* {name}
*Регион:* {region}
*Тип помощи:* {help_type}
*Контакт \\(Telegram\\):* {contact}
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
        help_type_lower = context.user_data["volunteer_data"].get("help_type", "").lower()
        for keyword, channel_name in channel_map.items():
            if keyword in help_type_lower:
                tasks.append(context.bot.send_message(chat_id=channels[channel_name], text=volunteer_info, parse_mode="MarkdownV2"))

        try:
            await asyncio.gather(*tasks)
            logger.info(f"Данные волонтёра отправлены: {volunteer_info}")
        except TelegramError as e:
            logger.error(f"Ошибка отправки данных волонтёра: {e}", exc_info=True)

        await update.message.reply_text(
            escape_markdown("Спасибо за вашу готовность помочь! Ваша заявка принята и будет рассмотрена.", version=2),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Готово", callback_data="volunteer_finish")]]) if update.message else InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]) ,
            parse_mode="MarkdownV2"
        )
        update_stats(user_id, "volunteer_registration")
        context.user_data.clear()
        return BotState.VOLUNTEER_FINISH if update.message else BotState.MAIN_MENU
    elif update.callback_query and update.callback_query.data == "cancel_volunteer":
        await update.callback_query.message.edit_text(
            CANCEL_MESSAGE,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
            parse_mode="MarkdownV2"
        )
        context.user_data.clear()
        return ConversationHandler.END
    return BotState.VOLUNTEER_CONTACT

async def volunteer_finish_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "volunteer_finish":
            await query.message.edit_text(
                escape_markdown("Добро пожаловать в команду!", version=2),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад в главное меню", callback_data="back_to_main")]]),
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        elif query.data == "back_to_main":
            await query.message.edit_text(
                escape_markdown("Вы вернулись в главное меню.", version=2),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🆘 Попросить о помощи", callback_data="main_help"),
                                                  InlineKeyboardButton("➕ Предложить ресурс", callback_data="main_resource")],
                                                 [InlineKeyboardButton("🤝 Стать волонтёром", callback_data="main_volunteer"),
                                                  InlineKeyboardButton("💸 Поддержать проект", callback_data="main_donate")],
                                                 [InlineKeyboardButton("✉️ Анонимное сообщение", callback_data="main_anonymous")]
                                                ]),
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
    return BotState.VOLUNTEER_FINISH
