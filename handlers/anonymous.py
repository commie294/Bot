from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest, Forbidden
import logging
from telegram.helpers import escape_markdown
from bot_responses import ANONYMOUS_CONFIRMATION
from keyboards import MAIN_MENU_BUTTONS, BACK_BUTTON, FINISH_MENU_KEYBOARD
from utils.message_utils import generate_message_id, load_channels, update_stats, check_rate_limit
from utils.constants import BotState

logger = logging.getLogger(__name__)

async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "back_to_main":
            await query.message.edit_text(
                escape_markdown("Вы вернулись в главное меню.", version=2),
                reply_markup=MAIN_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        elif query.data == "volunteer_finish": # Обработка кнопки "Готово"
            await query.message.edit_text(
                escape_markdown("Спасибо за ваше анонимное сообщение!", version=2),
                reply_markup=MAIN_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        return BotState.ANONYMOUS_MESSAGE # Обработка других callback_data, если появятся

    message = update.message.text
    if message:
        if len(message) > 4096:
            await update.message.reply_text(
                escape_markdown("Сообщение слишком длинное. Максимальная длина — 4096 символов. Пожалуйста, сократите его.", version=2),
                reply_markup=FINISH_MENU_KEYBOARD, # Используем inline-кнопку "Назад"
                parse_mode="MarkdownV2"
            )
            return BotState.ANONYMOUS_MESSAGE
        message_id = generate_message_id(update.effective_user.id)
        channels = load_channels()
        channel_id = channels.get("t64_misc")
        if not channel_id:
            logger.error("Канал t64_misc не найден в channels.json")
            await update.message.reply_text(
                escape_markdown("Ошибка: канал для анонимных сообщений не настроен. Свяжитесь с администратором.", version=2),
                reply_markup=MAIN_MENU_BUTTONS, # Используем inline-кнопку "Назад"
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        try:
            escaped_message = escape_markdown(message, version=2)
            await context.bot.send_message(
                chat_id=channel_id,
                text=escape_markdown(f"🔒 Анонимное сообщение [{message_id}]:\n\n", version=2) + escaped_message,
                parse_mode="MarkdownV2"
            )
            await update.message.reply_text(
                ANONYMOUS_CONFIRMATION,
                reply_markup=FINISH_MENU_KEYBOARD,
                parse_mode="MarkdownV2"
            )
            update_stats(update.effective_user.id, "anonymous_message")
            if "request_type" in context.user_data:
                del context.user_data["request_type"]
            return BotState.MAIN_MENU
        except Forbidden as e:
            logger.error(f"Бот не имеет доступа к каналу {channel_id}: {e}", exc_info=True)
            await update.message.reply_text(
                escape_markdown("Ошибка: бот не имеет доступа к каналу. Добавьте бота в канал и назначьте администратором.", version=2),
                reply_markup=MAIN_MENU_BUTTONS, # Используем inline-кнопку "Назад"
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        except BadRequest as e:
            logger.error(f"Ошибка формата сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                escape_markdown("Ошибка формата сообщения. Попробуйте снова или сократите текст.", version=2),
                reply_markup=FINISH_MENU_KEYBOARD, # Используем inline-кнопку "Назад"
                parse_mode="MarkdownV2"
            )
            return BotState.ANONYMOUS_MESSAGE
        except TelegramError as e:
            logger.error(f"Ошибка отправки анонимного сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                escape_markdown("Ошибка при отправке сообщения. Пожалуйста, попробуйте позже.", version=2),
                reply_markup=MAIN_MENU_BUTTONS, # Используем inline-кнопку "Назад"
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
    else:
        await update.message.reply_text(
            escape_markdown("Пожалуйста, введите ваше сообщение или нажмите '⬅️ Назад'.", version=2),
            reply_markup=MAIN_MENU_BUTTONS, # Используем inline-кнопку "Назад"
            parse_mode="MarkdownV2"
        )
        return BotState.ANONYMOUS_MESSAGE
