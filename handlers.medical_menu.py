from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot_responses import CONSULTATION_PROMPT, GENDER_THERAPY_MESSAGE, F64_MESSAGE, SURGERY_INFO_MESSAGE, CHOOSE_HELP_CATEGORY, BACK_TO_MAIN_MENU
from keyboards import BACK_BUTTON, HELP_MENU_BUTTONS, MEDICAL_MENU_BUTTONS, GENDER_THERAPY_CHOICE_BUTTONS, SURGERY_INFO_KEYBOARD

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=keyboard,
        )
        return 2  # HELP_MENU
    elif choice == "🗣️ Медицинская консультация":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = "Помощь - Медицинская консультация"
        return 3  # TYPING
    elif choice == "💉HRT":
        keyboard = ReplyKeyboardMarkup(
            GENDER_THERAPY_CHOICE_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            GENDER_THERAPY_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return 12  # MEDICAL_GENDER_THERAPY_MENU
    elif choice == "❓ F64":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            F64_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return 5  # MEDICAL_MENU
    elif choice == "⚕️ Операции":
        await update.message.reply_text(
            SURGERY_INFO_MESSAGE,
            parse_mode="Markdown",
            reply_markup=SURGERY_INFO_KEYBOARD,
        )
        return 15  # MEDICAL_SURGERY_PLANNING
    else:
        await update.message.reply_text(CHOOSE_HELP_CATEGORY)
        return 5  # MEDICAL_MENU
