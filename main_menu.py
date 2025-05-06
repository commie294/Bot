from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from bot_responses import START_MESSAGE, CHOOSE_FROM_MENU, VOLUNTEER_MESSAGE, DONATE_MESSAGE, FAREWELL_MESSAGE
from keyboards import MAIN_MENU_BUTTONS, VOLUNTEER_START_KEYBOARD, BACK_BUTTON, DONE_BUTTON
from utils.constants import BotState, MAIN_MENU_ACTIONS, REQUEST_TYPES

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Инициирует взаимодействие с ботом."""
    keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(
        START_MESSAGE.format(region="России и странах СНГ"),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    return BotState.MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор пользователя в главном меню."""
    user_choice = update.message.text
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == 'volunteer_start_callback':
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=VOLUNTEER_MESSAGE,
                reply_markup=VOLUNTEER_START_KEYBOARD
            )
            return BotState.VOLUNTEER_CONFIRM_START

    if user_choice == BACK_BUTTON or user_choice == DONE_BUTTON:
        await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    if user_choice in MAIN_MENU_ACTIONS:
        keyboard, message, state = MAIN_MENU_ACTIONS[user_choice]
        context.user_data["request_type"] = REQUEST_TYPES.get(user_choice.lower(), user_choice)
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode="Markdown")
        return state
    elif user_choice == "🤝 Стать волонтером":
        await update.message.reply_text(VOLUNTEER_MESSAGE, reply_markup=VOLUNTEER_START_KEYBOARD)
        return BotState.VOLUNTEER_CONFIRM_START
    elif user_choice == "💸 Поддержать проект":
        await update.message.reply_text(DONATE_MESSAGE, parse_mode="Markdown")
        return BotState.MAIN_MENU
    elif user_choice == "✉️ Анонимное сообщение":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Пожалуйста, напишите ваше анонимное сообщение:",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = REQUEST_TYPES["anonymous"]
        return BotState.ANONYMOUS_MESSAGE
    await update.message.reply_text(CHOOSE_FROM_MENU)
    return BotState.MAIN_MENU
