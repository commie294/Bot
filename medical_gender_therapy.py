from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot_responses import MASCULINIZING_HRT_INFO, FEMINIZING_HRT_INFO, GENDER_THERAPY_MESSAGE
from keyboards import BACK_BUTTON

async def medical_gender_therapy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return 5  # MEDICAL_MENU
    elif choice == "T":
        keyboard = ReplyKeyboardMarkup(
            [
                ["DIY"],
                ["Запросить консультацию по мужской ГТ"],
                [BACK_BUTTON],
            ],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            MASCULINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return 13  # MEDICAL_FTM_HRT
    elif choice == "E":
        keyboard = ReplyKeyboardMarkup(
            [
                ["DIY"],
                ["Запросить консультацию по женской ГТ"],
                [BACK_BUTTON],
            ],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            FEMINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return 14  # MEDICAL_MTF_HRT
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return 12  # MEDICAL_GENDER_THERAPY_MENU
