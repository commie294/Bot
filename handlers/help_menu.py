from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from bot_responses import (
    HELP_MENU_MESSAGE, EMERGENCY_MESSAGE, HOUSING_FINANCE_PROMPT, 
    PSYCHOLOGICAL_HELP_PROMPT, CHOOSE_HELP_CATEGORY, 
    LGBT_FAMILIES_INFO, DOCUMENTS_MESSAGE, PROPAGANDA_MESSAGE,
    CONSULTATION_PROMPT, REPORT_ABUSE_MESSAGE
)
from keyboards import (
    HELP_MENU_BUTTONS, LEGAL_MENU_BUTTONS, MAIN_MENU_BUTTONS, 
    MEDICAL_MENU_BUTTONS
)
from utils.constants import BotState, REQUEST_TYPES
import logging

logger = logging.getLogger(__name__)

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик главного меню помощи"""
    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            user_choice = query.data
            
            if user_choice == "back_to_main":
                await query.message.edit_text(
                    escape_markdown("Вы вернулись в главное меню.", version=2),
                    reply_markup=MAIN_MENU_BUTTONS,
                    parse_mode="MarkdownV2"
                )
                return BotState.MAIN_MENU
            
            elif user_choice == "help_emergency":
                context.user_data["request_type"] = REQUEST_TYPES["emergency"]
                await query.message.edit_text(
                    EMERGENCY_MESSAGE.format(emergency_number="112"),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_help")]]),
                    parse_mode="MarkdownV2"
                )
                return BotState.TYPING
            
            elif user_choice == "help_housing":
                context.user_data["request_type"] = REQUEST_TYPES["housing"]
                await query.message.edit_text(
                    HOUSING_FINANCE_PROMPT,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_help")]]),
                    parse_mode="MarkdownV2"
                )
                return BotState.TYPING
            
            elif user_choice == "help_psych":
                context.user_data["request_type"] = REQUEST_TYPES["psych"]
                await query.message.edit_text(
                    PSYCHOLOGICAL_HELP_PROMPT,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_help")]]),
                    parse_mode="MarkdownV2"
                )
                return BotState.TYPING
            
            elif user_choice == "help_medical":
                await query.message.edit_text(
                    escape_markdown("Выберите категорию медицинской помощи:", version=2),
                    reply_markup=MEDICAL_MENU_BUTTONS,
                    parse_mode="MarkdownV2"
                )
                return BotState.MEDICAL_MENU
            
            elif user_choice == "help_legal":
                await query.message.edit_text(
                    escape_markdown("Выберите категорию юридической помощи:", version=2),
                    reply_markup=LEGAL_MENU_BUTTONS,
                    parse_mode="MarkdownV2"
                )
                return BotState.FAQ_LEGAL
        
        return BotState.HELP_MENU

    except Exception as e:
        logger.error(f"Error in help_menu: {e}", exc_info=True)
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже.",
                parse_mode="MarkdownV2"
            )
        return BotState.MAIN_MENU

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик меню юридической помощи"""
    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            choice = query.data
            
            if choice == "back_to_help":
                await query.message.edit_text(
                    escape_markdown("Выберите категорию помощи:", version=2),
                    reply_markup=HELP_MENU_BUTTONS,
                    parse_mode="MarkdownV2"
                )
                return BotState.HELP_MENU
            
            elif choice == "legal_lgbt":
                await query.message.edit_text(
                    LGBT_FAMILIES_INFO, 
                    parse_mode="MarkdownV2", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_legal")]])
                )
                return BotState.FAQ_LEGAL
            
            elif choice == "legal_docs":
                await query.message.edit_text(
                    DOCUMENTS_MESSAGE, 
                    parse_mode="MarkdownV2", 
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Запросить консультацию", callback_data='request_legal_docs')],
                        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_legal")]
                    ])
                )
                return BotState.FAQ_LEGAL
            
            elif choice == "legal_propaganda":
                await query.message.edit_text(
                    PROPAGANDA_MESSAGE, 
                    parse_mode="MarkdownV2", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_legal")]])
                )
                return BotState.FAQ_LEGAL
            
            elif choice == "legal_consult":
                context.user_data["request_type"] = REQUEST_TYPES["legal_consult"]
                await context.bot.send_message(
                    chat_id=query.message.chat_id, 
                    text=CONSULTATION_PROMPT, 
                    parse_mode="MarkdownV2", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_legal")]])
                )
                return BotState.TYPING
            
            elif choice == "legal_abuse":
                context.user_data["request_type"] = REQUEST_TYPES["legal_abuse"]
                await context.bot.send_message(
                    chat_id=query.message.chat_id, 
                    text=REPORT_ABUSE_MESSAGE, 
                    parse_mode="MarkdownV2", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_legal")]])
                )
                return BotState.TYPING
            
            elif choice == "back_to_legal":
                await query.message.edit_text(
                    escape_markdown("Выберите категорию юридической помощи:", version=2),
                    reply_markup=LEGAL_MENU_BUTTONS,
                    parse_mode="MarkdownV2"
                )
                return BotState.FAQ_LEGAL
        
        return BotState.FAQ_LEGAL

    except Exception as e:
        logger.error(f"Error in faq_legal: {e}", exc_info=True)
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже.",
                parse_mode="MarkdownV2"
            )
        return BotState.MAIN_MENU
