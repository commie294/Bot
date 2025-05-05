from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot_responses import (
    HELP_MENU_MESSAGE, EMERGENCY_MESSAGE, HOUSING_FINANCE_PROMPT, PSYCHOLOGICAL_HELP_PROMPT,
    CHOOSE_HELP_CATEGORY, LGBT_FAMILIES_INFO, DOCUMENTS_MESSAGE, PROPAGANDA_MESSAGE,
    CONSULTATION_PROMPT, REPORT_ABUSE_MESSAGE
)
from keyboards import HELP_MENU_BUTTONS, LEGAL_MENU_BUTTONS, BACK_BUTTON
from utils.constants import BotState, REQUEST_TYPES

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор пользователя в меню помощи."""
    user_choice = update.message.text
    if user_choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=keyboard,
        )
        return BotState.MAIN_MENU
    elif user_choice == "🚨 Срочная помощь":
        context.user_data["request_type"] = REQUEST_TYPES["emergency"]
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(EMERGENCY_MESSAGE, reply_markup=keyboard)
        return BotState.TYPING
    elif user_choice == "🏠 Жилье/финансы":
        context.user_data["request_type"] = REQUEST_TYPES["housing"]
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(HOUSING_FINANCE_PROMPT, reply_markup=keyboard)
        return BotState.TYPING
    elif user_choice == "🧠 Психологическая помощь":
        context.user_data["request_type"] = REQUEST_TYPES["psych"]
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(PSYCHOLOGICAL_HELP_PROMPT, reply_markup=keyboard)
        return BotState.TYPING
    elif user_choice == "🩺 Медицинская помощь":
        keyboard = ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Выберите категорию медицинской помощи:",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_MENU
    elif user_choice == "⚖️ Юридическая помощь":
        keyboard = ReplyKeyboardMarkup(LEGAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Выберите категорию юридической помощи:",
            reply_markup=keyboard,
        )
        return BotState.FAQ_LEGAL
    await update.message.reply_text(CHOOSE_HELP_CATEGORY)
    return BotState.HELP_MENU

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает юридические запросы."""
    choice = update.message.text
    keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
    if choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            HELP_MENU_MESSAGE,
            reply_markup=keyboard,
        )
        return BotState.HELP_MENU
    elif choice == "🏳️‍🌈 ЛГБТ+ семьи":
        await update.message.reply_text(
            LGBT_FAMILIES_INFO,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return BotState.FAQ_LEGAL
    elif choice == "📝 Как сменить документы":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Запросить консультацию", callback_data='request_legal_docs')]
        ])
        await update.message.reply_text(DOCUMENTS_MESSAGE, parse_mode="Markdown", reply_markup=keyboard)
        return BotState.FAQ_LEGAL
    elif choice == "📢 Что такое пропаганда ЛГБТ?":
        await update.message.reply_text(PROPAGANDA_MESSAGE, parse_mode="Markdown", reply_markup=keyboard)
        return BotState.FAQ_LEGAL
    elif choice == "🗣️ Юридическая консультация":
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = REQUEST_TYPES["legal_consult"]
        return BotState.TYPING
    elif choice == "🚨 Сообщить о нарушении":
        await update.message.reply_text(
            REPORT_ABUSE_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = REQUEST_TYPES["legal_abuse"]
        return BotState.TYPING
    await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
    return BotState.FAQ_LEGAL
