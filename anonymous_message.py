import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from bot_responses import BACK_TO_MAIN_MENU, ANONYMOUS_CONFIRMATION
from keyboards import BACK_BUTTON, MAIN_MENU_BUTTONS, FINISH_MENU_KEYBOARD
from utils.message_id_generator import generate_message_id
from channels import CHANNELS

logger = logging.getLogger(__name__)

async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message.text
    if message == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=keyboard,
        )
        return 1  # MAIN_MENU
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
            return 1  # MAIN_MENU
        except TelegramError as e:
            logger.error(f"Ошибка Telegram API при отправке анонимного сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                "Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return 1  # MAIN_MENU
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при отправке анонимного сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                "Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            return 1  # MAIN_MENU
    else:
        await update.message.reply_text("Пожалуйста, введите ваше сообщение  или нажмите '⬅️ Назад'.")
        return 11  # ANONYMOUS_MESSAGE
