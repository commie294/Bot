from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot_responses import HELP_MENU_MESSAGE, EMERGENCY_MESSAGE, HOUSING_FINANCE_PROMPT, PSYCHOLOGICAL_HELP_PROMPT, CONSULTATION_PROMPT, CHOOSE_HELP_CATEGORY, BACK_TO_MAIN_MENU
from keyboards import HELP_MENU_BUTTONS, BACK_BUTTON, MEDICAL_MENU_BUTTONS, LEGAL_MENU_BUTTONS

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = update.message.text
    if user_choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=keyboard,
        )
        return 1  # MAIN_MENU
    elif user_choice == "🚨 Срочная помощь":
        context.user_data["request_type"] = "Срочная помощь"
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(EMERGENCY_MESSAGE, reply_markup=keyboard)
        return 3  # TYPING
    elif user_choice == "🏠 Жилье/финансы":
        context.user_data["request_type"] = "Жилье/финансы"
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(HOUSING_FINANCE_PROMPT, reply_markup=keyboard)
        return 3  # TYPING
    elif user_choice == "🧠 Психологическая помощь":
        context.user_data["request_type"] = "Психологическая помощь"
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(PSYCHOLOGICAL_HELP_PROMPT, reply_markup=keyboard)
        return 3  # TYPING
    elif user_choice == "🩺 Медицинская помощь":
        keyboard = ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Выберите категорию медицинской помощи:",
            reply_markup=keyboard,
        )
        return 5  # MEDICAL_MENU
    elif user_choice == "⚖️ Юридическая помощь":
        keyboard = ReplyKeyboardMarkup(LEGAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Выберите категорию юридической помощи:",
            reply_markup=keyboard,
        )
        return 4  # FAQ_LEGAL
    else:
        await update.message.reply_text(CHOOSE_HELP_CATEGORY)
        return 2  # HELP_MENU
