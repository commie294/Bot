from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from bot_responses import (
    HELP_MENU_MESSAGE, EMERGENCY_MESSAGE, HOUSING_FINANCE_PROMPT, PSYCHOLOGICAL_HELP_PROMPT,
    CHOOSE_HELP_CATEGORY, LGBT_FAMILIES_INFO, DOCUMENTS_MESSAGE, PROPAGANDA_MESSAGE,
    CONSULTATION_PROMPT, REPORT_ABUSE_MESSAGE
)
from keyboards import HELP_MENU_BUTTONS, LEGAL_MENU_BUTTONS, BACK_BUTTON, MAIN_MENU_BUTTONS, MEDICAL_MENU_BUTTONS
from utils.constants import BotState, REQUEST_TYPES
from utils.message_utils import check_rate_limit

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
        elif user_choice == "help_emergency":
            context.user_data["request_type"] = REQUEST_TYPES["emergency"]
            await query.message.edit_text(
                EMERGENCY_MESSAGE.format(emergency_number="112"),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_help")]]),
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        elif user_choice == "help_housing":
            context.user_data["request_type"] = REQUEST_TYPES["housing"]
            await query.message.edit_text(
                HOUSING_FINANCE_PROMPT,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_help")]]),
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        elif user_choice == "help_psych":
            context.user_data["request_type"] = REQUEST_TYPES["psych"]
            await query.message.edit_text(
                PSYCHOLOGICAL_HELP_PROMPT,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_help")]]),
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        elif user_choice == "help_medical":
            await query.message.edit_text(
                escape_markdown("Выберите категорию медицинской помощи:", version=2),
                reply_markup=MEDICAL_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MEDICAL_MENU
        elif user_choice == "help_legal":
            await query.message.edit_text(
                escape_markdown("Выберите категорию юридической помощи:", version=2),
                reply_markup=LEGAL_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.FAQ_LEGAL
    return BotState.HELP_MENU

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        choice = query.data
        if choice == "back_to_help":
            await query.message.edit_text(
                escape_markdown("Выберите категорию помощи:", version=2),
                reply_markup=HELP_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.HELP_MENU
        elif choice == "legal_lgbt":
            await query.message.edit_text(LGBT_FAMILIES_INFO, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_legal")]]))
            return BotState.FAQ_LEGAL
        elif choice == "legal_docs":
            await query.message.edit_text(DOCUMENTS_MESSAGE, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Запросить консультацию", callback_data='request_legal_docs'),
            InlineKeyboardButton("⬅️ Назад", callback_data="back_to_legal")
        ]
    ])
)
        elif choice == "legal_propaganda":
            await query.message.edit_text(PROPAGANDA_MESSAGE, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_legal")]]))
            return BotState.FAQ_LEGAL
        elif choice == "legal_consult":
            context.user_data["request_type"] = REQUEST_TYPES["legal_consult"]
            await context.bot.send_message(chat_id=query.message.chat_id, text=CONSULTATION_PROMPT, parse_mode="MarkdownV2", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            return BotState.TYPING
        elif choice == "legal_abuse":
            context.user_data["request_type"] = REQUEST_TYPES["legal_abuse"]
            await context.bot.send_message(chat_id=query.message.chat_id, text=REPORT_ABUSE_MESSAGE, parse_mode="MarkdownV2", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            return BotState.TYPING
    return BotState.FAQ_LEGAL

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        choice = query.data
        if choice == "back_to_help":
            await query.message.edit_text(
                escape_markdown("Выберите категорию помощи:", version=2),
                reply_markup=HELP_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.HELP_MENU
        elif choice == "medical_consult":
            context.user_data["request_type"] = REQUEST_TYPES["medical_consult"]
            await context.bot.send_message(chat_id=query.message.chat_id, text=CONSULTATION_PROMPT, parse_mode="MarkdownV2", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            return BotState.TYPING
        elif choice == "medical_hrt":
            await query.message.edit_text(GENDER_THERAPY_MESSAGE, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("T", callback_data="hrt_t"), [InlineKeyboardButton("E", callback_data="hrt_e")], [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical")]]))
            return BotState.MEDICAL_GENDER_THERAPY_MENU
        elif choice == "medical_f64":
            await query.message.edit_text(F64_MESSAGE, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical")]]))
            return BotState.MEDICAL_MENU
        elif choice == "medical_surgery":
            await query.message.edit_text(SURGERY_INFO_MESSAGE, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗓️ Спланировать операцию", callback_data='plan_surgery'), [InlineKeyboardButton("ФТМ Операции", callback_data='ftm_surgery')], [InlineKeyboardButton("МТФ Операции", callback_data='mtf_surgery')], [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical")]]))
            return BotState.MEDICAL_SURGERY_PLANNING
    return BotState.MEDICAL_MENU
        elif user_choice == "⚖️ Юридическая помощь":
            keyboard = ReplyKeyboardMarkup(LEGAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(
                escape_markdown("Выберите категорию юридической помощи:", version=2),
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
            return BotState.FAQ_LEGAL
        await update.message.reply_text(
            CHOOSE_HELP_CATEGORY,
            parse_mode="MarkdownV2"
        )
    return BotState.HELP_MENU

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_rate_limit(update, context):
        return BotState.FAQ_LEGAL
    choice = update.message.text
    keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
    if choice == BACK_BUTTON:
        keyboard = HELP_MENU_BUTTONS
        await update.message.reply_text(
            HELP_MENU_MESSAGE,
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.HELP_MENU
    elif choice == "🏳️‍🌈 ЛГБТ+ семьи":
        await update.message.reply_text(
            LGBT_FAMILIES_INFO,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        return BotState.FAQ_LEGAL
    elif choice == "📝 Как сменить документы":
        keyboard_inline = InlineKeyboardMarkup([
            [InlineKeyboardButton("Запросить консультацию", callback_data='request_legal_docs')]
        ])
        await update.message.reply_text(
            DOCUMENTS_MESSAGE,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard_inline
        )
        return BotState.FAQ_LEGAL
    elif choice == "📢 Что такое пропаганда ЛГБТ?":
        await update.message.reply_text(
            PROPAGANDA_MESSAGE,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        return BotState.FAQ_LEGAL
    elif choice == "🗣️ Юридическая консультация":
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        context.user_data["request_type"] = REQUEST_TYPES["legal_consult"]
        return BotState.TYPING
    elif choice == "🚨 Сообщить о нарушении":
        await update.message.reply_text(
            REPORT_ABUSE_MESSAGE,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        context.user_data["request_type"] = REQUEST_TYPES["legal_abuse"]
        return BotState.TYPING
    await update.message.reply_text(
        escape_markdown("Пожалуйста, выберите опцию из меню.", version=2),
        parse_mode="MarkdownV2"
    )
    return BotState.FAQ_LEGAL
