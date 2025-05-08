import os
import logging
import signal
import asyncio
import json
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, InlineQueryHandler
from telegram.helpers import escape_markdown
from handlers.main_menu import start, main_menu
from handlers.help_menu import help_menu, faq_legal
from handlers.medical import medical_menu, medical_gender_therapy_menu, medical_ftm_hrt, medical_mtf_hrt, medical_surgery_planning
from handlers.volunteer import ask_volunteer_name, get_volunteer_region, volunteer_help_type_handler, volunteer_contact_handler, volunteer_finish_handler
from handlers.anonymous import anonymous_message
from handlers.resources import handle_resource_proposal, list_resources # Обновлен импорт
from utils.message_utils import error_handler, request_legal_docs_callback, plan_surgery_callback, handle_typing, feedback_handler, check_rate_limit, load_channels # Импорт load_channels
from utils.constants import BotState, check_env_vars
from keyboards import MAIN_MENU_BUTTONS, VOLUNTEER_START_KEYBOARD, BACK_BUTTON, DONE_BUTTON, HELP_MENU_BUTTONS
from bot_responses import VOLUNTEER_MESSAGE, DONATE_MESSAGE, FAREWELL_MESSAGE, CHOOSE_FROM_MENU, RESOURCE_PROMPT_MESSAGE, ANONYMOUS_CONFIRMATION

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    await update.message.reply_text(escape_markdown("Вы вернулись в главное меню.", version=2), reply_markup=MAIN_MENU_BUTTONS, parse_mode="MarkdownV2")
    return BotState.MAIN_MENU

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        escape_markdown("Выберите категорию помощи:", version=2),
        reply_markup=HELP_MENU_BUTTONS,
        parse_mode="MarkdownV2"
    )
    return BotState.HELP_MENU

async def resource_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
    await query.message.edit_text(
        escape_markdown("Пожалуйста, напишите описание или ссылку на ресурс:", version=2),
        reply_markup=keyboard,
        parse_mode="MarkdownV2"
    )
    return BotState.RESOURCE_PROPOSAL

async def volunteer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        VOLUNTEER_MESSAGE,
        reply_markup=VOLUNTEER_START_KEYBOARD,
        parse_mode="MarkdownV2"
    )
    return BotState.VOLUNTEER_CONFIRM_START

async def donate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    donate_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
    ])
    await query.message.edit_text(
        DONATE_MESSAGE,
        reply_markup=donate_keyboard,
        parse_mode="MarkdownV2"
    )
    return BotState.MAIN_MENU

async def anonymous_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
    await query.message.edit_text(
        escape_markdown("Пожалуйста, напишите ваше анонимное сообщение:", version=2),
        reply_markup=keyboard,
        parse_mode="MarkdownV2"
    )
    return BotState.ANONYMOUS_MESSAGE

async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        escape_markdown("Вы вернулись в главное меню.", version=2),
        reply_markup=MAIN_MENU_BUTTONS,
        parse_mode="MarkdownV2"
    )
    return BotState.MAIN_MENU

async def update_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != os.getenv("ADMIN_CHAT_ID"):
        await update.message.reply_text(CHOOSE_FROM_MENU, parse_mode="MarkdownV2")
        return
    await update.message.reply_text("Функция обновления ресурсов временно отключена.", parse_mode="MarkdownV2")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != os.getenv("ADMIN_CHAT_ID"):
        await update.message.reply_text(CHOOSE_FROM_MENU, parse_mode="MarkdownV2")
        return
    await update.message.reply_text("Функция статистики временно отключена.", parse_mode="MarkdownV2")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.inline_query.answer([]) # Отключаем inline-поиск ресурсов

async def main() -> None:
    check_env_vars()
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN не найден в файле .env")
        return

    application = Application.builder().token(token).build()

    main_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BotState.MAIN_MENU: [CallbackQueryHandler(main_menu), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            BotState.HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_menu)],
            BotState.TYPING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing),
                MessageHandler(filters.Document.ALL, handle_typing)
            ],
            BotState.FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, faq_legal)],
            BotState.MEDICAL_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_menu)],
            BotState.MEDICAL_GENDER_THERAPY_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_gender_therapy_menu)],
            BotState.MEDICAL_FTM_HRT: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_ftm_hrt)],
            BotState.MEDICAL_MTF_HRT: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_mtf_hrt)],
            BotState.MEDICAL_SURGERY_PLANNING: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_surgery_planning)],
            BotState.VOLUNTEER_CONFIRM_START: [MessageHandler(filters.TEXT & filters.Regex("^Далее$"), ask_volunteer_name)],
            BotState.VOLUNTEER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Отмена)$"), get_volunteer_region)],
            BotState.VOLUNTEER_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Отмена)$"), volunteer_help_type_handler)],
            BotState.VOLUNTEER_HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Отмена)$"), volunteer_contact_handler)],
            BotState.VOLUNTEER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Отмена)$"), volunteer_finish_handler)],
            BotState.ANONYMOUS_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, anonymous_message)],
            BotState.DONE_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: BotState.MAIN_MENU)],
            BotState.RESOURCE_PROPOSAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_resource_proposal)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(main_conv_handler)
    application.add_handler(CallbackQueryHandler(help_callback, pattern='^main_help$'))
    application.add_handler(CallbackQueryHandler(volunteer_callback, pattern='^main_volunteer$'))
    application.add_handler(CallbackQueryHandler(donate_callback, pattern='^main_donate$'))
    application.add_handler(CallbackQueryHandler(anonymous_callback, pattern='^main_anonymous$'))
    application.add_handler(CallbackQueryHandler(request_legal_docs_callback, pattern='^request_legal_docs$'))
    application.add_handler(CallbackQueryHandler(plan_surgery_callback, pattern='^plan_surgery$'))
    application.add_handler(CallbackQueryHandler(feedback_handler, pattern='^feedback_(good|bad)$'))
    application.add_handler(CommandHandler("resources", list_resources))
    application.add_handler(CommandHandler("updateresources", update_resources))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_error_handler(error_handler)

    logger.info("Starting bot with polling...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
