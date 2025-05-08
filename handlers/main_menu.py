from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from bot_responses import START_MESSAGE, CHOOSE_FROM_MENU, VOLUNTEER_MESSAGE, DONATE_MESSAGE, FAREWELL_MESSAGE
from keyboards import MAIN_MENU_BUTTONS, VOLUNTEER_START_KEYBOARD, BACK_BUTTON, DONE_BUTTON, HELP_MENU_BUTTONS
from utils.constants import BotState, MAIN_MENU_ACTIONS, REQUEST_TYPES
from utils.message_utils import check_rate_limit

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    region = escape_markdown("России и странах СНГ", version=2)  # Экранируем регион
    await update.message.reply_photo(
        photo="https://your-image-url.com/welcome.jpg",
        caption=START_MESSAGE.format(region=region),
        reply_markup=MAIN_MENU_BUTTONS,
        parse_mode="MarkdownV2"
    )
    return BotState.MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_choice = query.data
        if user_choice == "back_to_main":
            await query.message.edit_text(
                escape_markdown("Вы вернулись в главное меню.", version=2),
                reply_markup=MAIN_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        elif user_choice == "main_help":
            await query.message.edit_text(
                escape_markdown("Выберите категорию помощи:", version=2),
                reply_markup=HELP_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.HELP_MENU
        elif user_choice == "main_resource":
            await query.message.edit_text(
                escape_markdown("Введите название ресурса:", version=2),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]),
                parse_mode="MarkdownV2"
            )
            context.user_data["resource_step"] = "title"
            return BotState.RESOURCE_PROPOSAL
        elif user_choice == "main_volunteer":
            await query.message.edit_text(
                VOLUNTEER_MESSAGE,
                reply_markup=VOLUNTEER_START_KEYBOARD,
                parse_mode="MarkdownV2"
            )
            return BotState.VOLUNTEER_CONFIRM_START
        elif user_choice == "main_donate":
            await query.message.edit_text(
                DONATE_MESSAGE,
                reply_markup=MAIN_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        elif user_choice == "main_anonymous":
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await query.message.edit_text(
                escape_markdown("Пожалуйста, напишите ваше анонимное сообщение:", version=2),
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            context.user_data["request_type"] = REQUEST_TYPES["anonymous"]
            return BotState.ANONYMOUS_MESSAGE
        elif user_choice == "volunteer_start_callback":
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=VOLUNTEER_MESSAGE,
                reply_markup=VOLUNTEER_START_KEYBOARD,
                parse_mode="MarkdownV2"
            )
            return BotState.VOLUNTEER_CONFIRM_START
    else:
        if not await check_rate_limit(update, context):
            return BotState.MAIN_MENU
        user_choice = update.message.text
        if user_choice == BACK_BUTTON or user_choice == DONE_BUTTON:
            await update.message.reply_text(
                FAREWELL_MESSAGE,
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="MarkdownV2"
            )
            return ConversationHandler.END
        if user_choice in MAIN_MENU_ACTIONS:
            keyboard, message, state = MAIN_MENU_ACTIONS[user_choice]
            context.user_data["request_type"] = REQUEST_TYPES.get(user_choice.lower(), user_choice)
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return state
        elif user_choice == "🤝 Стать волонтером":
            await update.message.reply_text(
                VOLUNTEER_MESSAGE,
                reply_markup=VOLUNTEER_START_KEYBOARD,
                parse_mode="MarkdownV2"
            )
            return BotState.VOLUNTEER_CONFIRM_START
        elif user_choice == "💸 Поддержать проект":
            await update.message.reply_text(
                DONATE_MESSAGE,
                reply_markup=MAIN_MENU_BUTTONS,
                parse_mode="MarkdownV2"  # Исправляем MarkdownV.ini на MarkdownV2
            )
            return BotState.MAIN_MENU
        elif user_choice == "✉️ Анонимное сообщение":
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(
                escape_markdown("Пожалуйста, напишите ваше анонимное сообщение:", version=2),
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            context.user_data["request_type"] = REQUEST_TYPES["anonymous"]
            return BotState.ANONYMOUS_MESSAGE
        await update.message.reply_text(
            CHOOSE_FROM_MENU,
            parse_mode="MarkdownV2"
        )
    return BotState.MAIN_MENU
