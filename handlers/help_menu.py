from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot_responses import (
    HELP_MENU_MESSAGE, EMERGENCY_MESSAGE, HOUSING_FINANCE_PROMPT, PSYCHOLOGICAL_HELP_PROMPT,
    CHOOSE_HELP_CATEGORY, LGBT_FAMILIES_INFO, DOCUMENTS_MESSAGE, PROPAGANDA_MESSAGE,
    CONSULTATION_PROMPT, REPORT_ABUSE_MESSAGE
)
from keyboards import HELP_MENU_BUTTONS, LEGAL_MENU_BUTTONS, BACK_BUTTON, MAIN_MENU_BUTTONS, MEDICAL_MENU_BUTTONS
from utils.constants import BotState, REQUEST_TYPES
from utils.message_utils import check_rate_limit

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_choice = query.data
        if user_choice == "back_to_main":
            await query.message.edit_text(
                "Вы вернулись в главное меню\\.",
                reply_markup=MAIN_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        elif user_choice == "help_emergency":
            context.user_data["request_type"] = REQUEST_TYPES["emergency"]
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await query.message.edit_text(
                EMERGENCY_MESSAGE.format(emergency_number="112"),
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        elif user_choice == "help_housing":
            context.user_data["request_type"] = REQUEST_TYPES["housing"]
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await query.message.edit_text(
                HOUSING_FINANCE_PROMPT,
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        elif user_choice == "help_psych":
            context.user_data["request_type"] = REQUEST_TYPES["psych"]
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await query.message.edit_text(
                PSYCHOLOGICAL_HELP_PROMPT,
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        elif user_choice == "help_medical":
            keyboard = ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
            await query.message.edit_text(
                "Выберите категорию медицинской помощи:",
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.MEDICAL_MENU
        elif user_choice == "help_legal":
            keyboard = ReplyKeyboardMarkup(LEGAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
            await query.message.edit_text(
                "Выберите категорию юридической помощи:",
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.FAQ_LEGAL
    else:
        if not await check_rate_limit(update, context):
            return BotState.HELP_MENU
        user_choice = update.message.text
        if user_choice == BACK_BUTTON:
            keyboard = MAIN_MENU_BUTTONS
            await update.message.reply_text(
                "Вы вернулись в главное меню.",
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        elif user_choice == "🚨 Срочная помощь":
            context.user_data["request_type"] = REQUEST_TYPES["emergency"]
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(
                EMERGENCY_MESSAGE.format(emergency_number="112"),
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        elif user_choice == "🏠 Жилье/финансы":
            context.user_data["request_type"] = REQUEST_TYPES["housing"]
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(
                HOUSING_FINANCE_PROMPT,
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        elif user_choice == "🧠 Психологическая помощь":
            context.user_data["request_type"] = REQUEST_TYPES["psych"]
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(
                PSYCHOLOGICAL_HELP_PROMPT,
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        elif user_choice == "🩺 Медицинская помощь":
            keyboard = ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(
                "Выберите категорию медицинской помощи:",
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return Bot
