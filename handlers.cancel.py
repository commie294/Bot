from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from bot_responses import CANCEL_MESSAGE, BACK_TO_MAIN_MENU
from keyboards import MAIN_MENU_BUTTONS

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(BACK_TO_MAIN_MENU, reply_markup=keyboard)
    return 1  # MAIN_MENU
