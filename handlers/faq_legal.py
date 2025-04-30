from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from bot_responses import LGBT_FAMILIES_INFO, DOCUMENTS_MESSAGE, PROPAGANDA_MESSAGE, CONSULTATION_PROMPT, REPORT_ABUSE_MESSAGE, BACK_TO_MAIN_MENU
from keyboards import BACK_BUTTON, HELP_MENU_BUTTONS

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=keyboard,
        )
        return 2  # HELP_MENU
    elif choice == "🏳️‍🌈 ЛГБТ+ семьи":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            LGBT_FAMILIES_INFO,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return 4  # FAQ_LEGAL
    elif choice == "📝 Как сменить документы":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Запросить консультацию", callback_data='request_legal_docs')]
        ])
        await update.message.reply_text(DOCUMENTS_MESSAGE, parse_mode="Markdown", reply_markup=keyboard)
        return 4  # FAQ_LEGAL
    elif choice == "📢 Что такое пропаганда ЛГБТ?":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(PROPAGANDA_MESSAGE, parse_mode="Markdown", reply_markup=keyboard)
        return 4  # FAQ_LEGAL
    elif choice == "🗣️ Юридическая консультация":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = "Помощь - Юридическая консультация"
        return 3  # TYPING
    elif choice == "🚨 Сообщить о нарушении":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            REPORT_ABUSE_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = "Помощь - Сообщение о нарушении (юридическое)"
        return 3  # TYPING
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return 4  # FAQ_LEGAL

async def request_legal_docs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик для inline-кнопки запроса консультации по документам."""
    query = update.callback_query
    await query.answer()  # Уведомляет пользователя о получении запроса
    context.user_data["request_type"] = "Помощь - Юридическая консультация (смена документов)"
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=CONSULTATION_PROMPT,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
    )
    return 3  # TYPING
