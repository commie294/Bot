from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.helpers import escape_markdown
from bot_responses import START_MESSAGE, CHOOSE_FROM_MENU, VOLUNTEER_MESSAGE, DONATE_MESSAGE, FAREWELL_MESSAGE
from keyboards import MAIN_MENU_BUTTONS, VOLUNTEER_START_KEYBOARD, BACK_BUTTON, DONE_BUTTON, HELP_MENU_BUTTONS
from utils.constants import BotState, REQUEST_TYPES
from utils.message_utils import check_rate_limit
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.effective_user.id} initiated /start.")
    try:
        region = escape_markdown("России и странах СНГ", version=2)
        await update.message.reply_text(
            START_MESSAGE.format(region=region),
            reply_markup=MAIN_MENU_BUTTONS,
            parse_mode="MarkdownV2"
        )
        return BotState.MAIN_MENU
    except Exception as e:
        logger.error(f"Error in /start for user {update.effective_user.id}: {e}", exc_info=True)
        await update.message.reply_text(
            escape_markdown("Произошла ошибка. Пожалуйста, попробуйте позже.", version=2),
            parse_mode="MarkdownV2"
        )
        return ConversationHandler.END

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    logger.info(f"Handling main menu action for user {user_id}.")
    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            user_choice = query.data
            logger.info(f"Callback query '{user_choice}' from user {user_id}.")
            if user_choice == "back_to_main":
                await query.message.edit_text(
                    escape_markdown("Вы вернулись в главное меню.", version=2),
                    reply_markup=MAIN_MENU_BUTTONS,
                    parse_mode="MarkdownV2"
                )
                return BotState.MAIN_MENU
            elif user_choice == "main_help":
                await query.message.edit_text(
                    escape_markdown("Выберите категорию помощи:", version=2),
                    reply_markup=HELP_MENU_BUTTONS,
                    parse_mode="MarkdownV2"
                )
                return BotState.HELP_MENU
            elif user_choice == "main_resource":
                await query.message.edit_text(
                    escape_markdown("Опишите, какой ресурс вы хотите предложить:", version=2),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
                    parse_mode="MarkdownV2"
                )
                context.user_data["resource_step"] = "title"
                return BotState.RESOURCE_PROPOSAL
            elif user_choice == "main_volunteer":
                await query.message.edit_text(
                    VOLUNTEER_MESSAGE,
                    reply_markup=VOLUNTEER_START_KEYBOARD,
                    parse_mode="MarkdownV2"
                )
                return BotState.VOLUNTEER_CONFIRM_START
            elif user_choice == "main_donate":
                await query.message.edit_text(
                    DONATE_MESSAGE,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
                    parse_mode="MarkdownV2"
                )
                return BotState.DONATE_INFO # Изменено на правильное состояние
            elif user_choice == "main_anonymous":
                await query.message.edit_text(
                    escape_markdown("Пожалуйста, напишите ваше анонимное сообщение:", version=2),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
                    parse_mode="MarkdownV2"
                )
                context.user_data["request_type"] = REQUEST_TYPES["anonymous"]
                return BotState.ANONYMOUS_MESSAGE
            else:
                await query.message.reply_text(
                    CHOOSE_FROM_MENU,
                    parse_mode="MarkdownV2"
                )
                return BotState.MAIN_MENU
        else:
            await update.message.reply_text(
                CHOOSE_FROM_MENU,
                reply_markup=MAIN_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
    except Exception as e:
        logger.error(f"Error in main_menu for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(
            escape_markdown("Произошла ошибка. Пожалуйста, попробуйте позже.", version=2),
            parse_mode="MarkdownV2"
        )
        return ConversationHandler.END
