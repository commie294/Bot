from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot_responses import FTM_SURGERY_INFO, MTF_SURGERY_INFO, SURGERY_PLANNING_PROMPT
from keyboards import BACK_BUTTON

async def medical_surgery_planning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return 5  # MEDICAL_MENU
    elif choice == "ФТМ Операции":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            FTM_SURGERY_INFO,
            reply_markup=keyboard,
        )
        return 15  # MEDICAL_SURGERY_PLANNING
    elif choice == "МТФ Операции":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            MTF_SURGERY_INFO,
            reply_markup=keyboard,
        )
        return 15  # MEDICAL_SURGERY_PLANNING
    elif update.callback_query and update.callback_query.data == 'plan_surgery':
        query = update.callback_query
        await query.answer()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=SURGERY_PLANNING_PROMPT,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        context.user_data["request_type"] = "Помощь - Планирование операции"
        return 3  # TYPING
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return 15  # MEDICAL_SURGERY_PLANNING

async def plan_surgery_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик для inline-кнопки запроса планирования операции."""
    query = update.callback_query
    await query.answer()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=SURGERY_PLANNING_PROMPT,
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
    )
    context.user_data["request_type"] = "Помощь - Планирование операции"
    return 3  # TYPING
