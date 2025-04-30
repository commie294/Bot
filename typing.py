import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from bot_responses import MESSAGE_SENT_SUCCESS, MESSAGE_SEND_ERROR
from keyboards import BACK_BUTTON, FINISH_MENU_KEYBOARD
from channels import CHANNELS

logger = logging.getLogger(__name__)

async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text
    request_type = context.user_data.get("request_type", "Сообщение")

    if user_text and user_text != BACK_BUTTON:
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
            "Помощь - Юридическая консультация (смена документов)": "t64_legal",
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
                return 1  # MAIN_MENU
            except TelegramError as e:
                logger.error(f"Ошибка Telegram API при отправке сообщения: {e}", exc_info=True)
                await update.message.reply_text(
                    MESSAGE_SEND_ERROR.format(e),
                    reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
                )
                return 1  # MAIN_MENU
            except Exception as e:
                logger.error(f"Непредвиденная ошибка при отправке сообщения: {e}", exc_info=True)
                await update.message.reply_text(
                    MESSAGE_SEND_ERROR.format(e),
                    reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
                )
                return 1  # MAIN_MENU
        else:
            await update.message.reply_text(
                "Произошла ошибка при обработке вашего запроса.",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
