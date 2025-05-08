from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.helpers import escape_markdown
from utils.message_utils import load_channels
from utils.resource_utils import load_resources
from utils.constants import BotState
from bot_responses import MESSAGE_SENT_SUCCESS, BACK_TO_MAIN_MENU
from keyboards import MAIN_MENU_BUTTONS, BACK_BUTTON, FINISH_MENU_KEYBOARD
import json
import logging

logger = logging.getLogger(__name__)

async def handle_resource_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text
    if user_text == BACK_BUTTON:
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=MAIN_MENU_BUTTONS,
            parse_mode="MarkdownV2"
        )
        return BotState.MAIN_MENU
    try:
        channels = load_channels()
        await context.bot.send_message(
            chat_id=channels["t64_misc"],
            text=f"*Предложенный ресурс:*\n\n{escape_markdown(user_text, version=2)}",
            parse_mode="MarkdownV2"
        )
        await update.message.reply_text(
            MESSAGE_SENT_SUCCESS,
            reply_markup=FINISH_MENU_KEYBOARD,
            parse_mode="MarkdownV2"
        )
        return BotState.MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка при отправке предложенного ресурса: {e}", exc_info=True)
        await update.message.reply_text(
            escape_markdown("Произошла ошибка при обработке вашего ресурса. Пожалуйста, попробуйте позже.", version=2),
            reply_markup=MAIN_MENU_BUTTONS,
            parse_mode="MarkdownV2"
        )
        return BotState.MAIN_MENU

async def list_resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    resources = load_
