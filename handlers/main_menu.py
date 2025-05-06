import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot_responses import START_MESSAGE, RESOURCES_MESSAGE
from keyboards import MAIN_MENU_BUTTONS, HELP_MENU_BUTTONS, BACK_BUTTON
from utils.message_utils import update_stats
from utils.constants import BotState

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(START_MESSAGE, reply_markup=keyboard)
    return BotState.MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    user_id = update.effective_user.id

    if choice == "⚖️ Юридическая помощь":
        from handlers.legal import legal_menu
        return await legal_menu(update, context)
    elif choice == "🩺 Медицинская помощь":
        from handlers.medical import medical_menu
        return await medical_menu(update, context)
    elif choice == "📩 Стать волонтёром":
        from handlers.volunteer import volunteer_confirm_start
        return await volunteer_confirm_start(update, context)
    elif choice == "✉️ Анонимное сообщение":
        from handlers.anonymous import anonymous_message
        await update.message.reply_text(
            "Введите ваше анонимное сообщение или нажмите '⬅️ Назад':",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return BotState.ANONYMOUS_MESSAGE
    elif choice == "💰 Поддержать проект":
        from handlers.donate import donate
        return await donate(update, context)
    elif choice == "📚 Полезные ресурсы":  # Новая опция
        await update.message.reply_text(
            RESOURCES_MESSAGE,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
        )
        update_stats(user_id, "resources_view")
        return BotState.MAIN_MENU

    await update.message.reply_text(
        "Пожалуйста, выберите одну из опций.",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
    )
    return BotState.MAIN_MENU
