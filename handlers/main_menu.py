from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot_responses import START_MESSAGE, RESOURCE_PROMPT_MESSAGE, VOLUNTEER_MESSAGE, DONATE_MESSAGE, EMERGENCY_MESSAGE, HOUSING_FINANCE_PROMPT, PSYCHOLOGICAL_HELP_PROMPT, CONSULTATION_PROMPT, BACK_TO_MAIN_MENU, CHOOSE_FROM_MENU, FAREWELL_MESSAGE
from keyboards import MAIN_MENU_BUTTONS, HELP_MENU_BUTTONS, BACK_BUTTON, VOLUNTEER_START_KEYBOARD, FINISH_MENU_KEYBOARD

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(START_MESSAGE, reply_markup=keyboard, parse_mode="Markdown")
    return 1  # MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = None
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == 'volunteer_start_callback':
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=VOLUNTEER_MESSAGE,
                reply_markup=VOLUNTEER_START_KEYBOARD
            )
            return 6  # VOLUNTEER_CONFIRM_START
        elif query.data == 'request_legal_docs':
            # Обработка колбека перенесена в faq_legal.py
            pass
        elif query.data == 'plan_surgery':
            # Обработка колбека перенесена в medical_surgery.py
            pass
    elif update.message:
        user_choice = update.message.text
        if user_choice == "🆘 Попросить о помощи":
            keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(RESOURCE_PROMPT_MESSAGE, reply_markup=keyboard, parse_mode="Markdown")
            return 2  # HELP_MENU
        elif user_choice == "➕ Предложить ресурс":
            context.user_data["request_type"] = "Ресурс"
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(RESOURCE_PROMPT_MESSAGE, reply_markup=keyboard)
            return 3  # TYPING
        elif user_choice == "🤝 Стать волонтером":
            await update.message.reply_text(VOLUNTEER_MESSAGE, reply_markup=VOLUNTEER_START_KEYBOARD)
            return 6  # VOLUNTEER_CONFIRM_START
        elif user_choice == "💸 Поддержать проект":
            await update.message.reply_text(DONATE_MESSAGE, parse_mode="Markdown")
            return 1  # MAIN_MENU
        elif user_choice == "✉️ Анонимное сообщение":
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(
                "Пожалуйста, напишите ваше анонимное сообщение:",
                reply_markup=keyboard,
            )
            context.user_data["request_type"] = "Анонимное сообщение"
            return 11  # ANONYMOUS_MESSAGE
        elif user_choice == BACK_BUTTON or user_choice == "✅ Готово":
            await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove())
            return -1  # ConversationHandler.END
        else:
            await update.message.reply_text(CHOOSE_FROM_MENU)
            return 1  # MAIN_MENU
    return 1  # MAIN_MENU
