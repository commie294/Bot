import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from handlers.main_menu import start, main_menu
from handlers.help_menu import help_menu, faq_legal
from handlers.resources import handle_resource_proposal, list_resources
from handlers.anonymous import anonymous_message
from handlers.volunteer import ask_volunteer_name, get_volunteer_region, volunteer_help_type_handler, volunteer_contact_handler, volunteer_finish_handler
from utils.constants import BotState
from utils.error_handler import error_handler
from utils.message_utils import handle_typing, request_legal_docs_callback, plan_surgery_callback, feedback_handler
from bot_responses import DONATE_MESSAGE, FAREWELL_MESSAGE
from dotenv import load_dotenv
from telegram.ext import Application
from handlers.medical import medical_menu, handle_gender_therapy_choice, medical_ftm_hrt, medical_mtf_hrt, medical_surgery_planning, send_hrt_guide, surgery_start, surgery_choice, surgery_budget, surgery_result

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def donate_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет информацию о способах поддержки проекта."""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(
            DONATE_MESSAGE,
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]])
        )
    elif update.message:
        await update.message.reply_text(
            DONATE_MESSAGE,
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]])
        )

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.effective_user
    await update.message.reply_text(
        "Действие отменено.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
async def farewell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает прощальные сообщения."""
    if update.message:
        await update.message.reply_text(FAREWELL_MESSAGE, reply_markup=ReplyKeyboardRemove(), parse_mode="MarkdownV2")
    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BotState.MAIN_MENU: [
                CallbackQueryHandler(main_menu),
            ],
            BotState.HELP_MENU: [
                CallbackQueryHandler(help_menu),
            ],
            BotState.FAQ_LEGAL: [
                CallbackQueryHandler(faq_legal),
            ],
            BotState.MEDICAL_MENU: [
                CallbackQueryHandler(medical_menu),
            ],
            BotState.MEDICAL_GENDER_THERAPY_INLINE: [
                CallbackQueryHandler(handle_gender_therapy_choice),
            ],
            BotState.MEDICAL_FTM_HRT: [
                CallbackQueryHandler(medical_ftm_hrt),
            ],
            BotState.MEDICAL_MTF_HRT: [
                CallbackQueryHandler(medical_mtf_hrt),
            ],
            BotState.MEDICAL_SURGERY_PLANNING: [
                CallbackQueryHandler(medical_surgery_planning),
            ],
            BotState.SURGERY_START: [
                CallbackQueryHandler(surgery_start),
            ],
            BotState.SURGERY_CHOICE: [
                CallbackQueryHandler(surgery_choice),
            ],
            BotState.SURGERY_BUDGET: [
                CallbackQueryHandler(surgery_budget),
            ],
            BotState.SURGERY_RESULT: [
                CallbackQueryHandler(surgery_result),
            ],
            BotState.TYPING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing),
                MessageHandler(filters.Document.ALL, handle_typing),
            ],
            BotState.RESOURCE_PROPOSAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_resource_proposal),
                CallbackQueryHandler(main_menu, pattern='^back_to_main$'),
            ],
            BotState.ANONYMOUS_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, anonymous_message),
                MessageHandler(filters.COMMAND, main_menu),
            ],
            BotState.VOLUNTEER_CONFIRM_START: [
                CallbackQueryHandler(ask_volunteer_name, pattern='^volunteer_start$'),
                CallbackQueryHandler(main_menu, pattern='^back_to_main$'),
            ],
            BotState.VOLUNTEER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_volunteer_name),
            ],
            BotState.VOLUNTEER_REGION: [
                CallbackQueryHandler(get_volunteer_region, pattern='^region_'),
            ],
            BotState.VOLUNTEER_HELP_TYPE: [
                CallbackQueryHandler(volunteer_help_type_handler, pattern='^volunteer_help_'),
            ],
            BotState.VOLUNTEER_CONTACT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_contact_handler),
            ],
            BotState.VOLUNTEER_FINISH: [
                CallbackQueryHandler(volunteer_finish_handler, pattern='^volunteer_finish$|^back_to_main$'),
            ],
            BotState.DONATE_INFO: [
                CallbackQueryHandler(donate_info, pattern='^main_donate$'),
                CallbackQueryHandler(main_menu, pattern='^back_to_main$'),
            ],
            BotState.FAREWELL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, farewell),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # **ADD THIS LINE:** This will catch any callback queries within the conversation
    # and route them to the appropriate state handler.
    application.add_handler(CallbackQueryHandler(conv_handler.handle_update))

    application.add_handler(CallbackQueryHandler(request_legal_docs_callback, pattern='^request_legal_docs$'))
    application.add_handler(CallbackQueryHandler(plan_surgery_callback, pattern='^plan_surgery$'))
    application.add_handler(CallbackQueryHandler(feedback_handler, pattern='^feedback_'))
    application.add_error_handler(error_handler)

    # Добавление обработчиков без состояний (команды вне ConversationHandler)
    application.add_handler(CommandHandler("resources", list_resources))

    application.run_polling()

if __name__ == "__main__":
    main()
