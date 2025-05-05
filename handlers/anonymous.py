from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError
import logging
from bot_responses import ANONYMOUS_CONFIRMATION
from keyboards import MAIN_MENU_BUTTONS, BACK_BUTTON, FINISH_MENU_KEYBOARD
from utils.message_utils import generate_message_id, load_channels, update_stats
from utils.constants import BotState

logger = logging.getLogger(__name__)

async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает анонимные сообщения."""
    message = update.message.text
    if message == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=keyboard,
        )
        return BotState.MAIN_MENU
    if message:
        message_id = generate_message_id(update.effective_user.id)
        try:
            channels = load_channels()
            await context.bot.send_message(
                chat_id=channels.get("t64_misc"),
                text=f"🔒 Анонимное сообщение [{message_id}]:\n\n{message}"
            )
            await update.message.reply_text(
                ANONYMOUS_CONFIRMATION,
                reply_markup=FINISH_MENU_KEYBOARD,
            )
            update_stats(update.effective_user.id, "anonymous_message")
            if "request_type" in context.user_data:
                del context.user_data["request_type"]
            return BotState.MAIN_MENU
        except TelegramError as e:
            logger.error(f"Ошибка отправки анонимного сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                "Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return BotState.MAIN_MENU
    await update.message.reply_text("Пожалуйста, введите ваше сообщение или нажмите '⬅️ Назад'.")
    return BotState.ANONYMOUS_MESSAGE
