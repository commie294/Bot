import os
import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from handlers.main_menu import start, main_menu
from handlers.help_menu import help_menu, faq_legal, medical_menu
from handlers.resources import handle_resource_proposal, list_resources
from handlers.anonymous import anonymous_message
from handlers.volunteer import volunteer_start, ask_volunteer_name, get_volunteer_region, volunteer_help_type_handler, volunteer_contact_handler, volunteer_finish_handler
from handlers.donate import donate_info
from handlers.farewell import farewell
from utils.constants import BotState
from utils.error_handler import error_handler
from message_utils import handle_typing, request_legal_docs_callback, plan_surgery_callback, feedback_handler

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

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

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
                CallbackQueryHandler(volunteer_start, pattern='^volunteer_start$'),
                CallbackQueryHandler(main_menu, pattern='^back_to_main$'),
            ],
            BotState.VOLUNTEER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_volunteer_name),
            ],
            BotState.VOLUNTEER_REGION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_volunteer_region),
            ],
            BotState.VOLUNTEER_HELP_TYPE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_help_type_handler),
            ],
            BotState.VOLUNTEER_CONTACT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_contact_handler),
            ],
            BotState.VOLUNTEER_FINISH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_finish_handler),
                CallbackQueryHandler(main_menu, pattern='^back_to_main$'),
            ],
            BotState.DONATE_INFO: [
                CallbackQueryHandler(donate_info, pattern='^main_donate$'),
                CallbackQueryHandler(main_menu, pattern='^back_to_main$'),
            ],
            BotState.FAREWELL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, farewell),
            ],
            BotState.LIST_RESOURCES: [
                CallbackQueryHandler(list_resources, pattern='^main_list_resources$'),
                CallbackQueryHandler(main_menu, pattern='^back_to_main$'),
            ],
            BotState.MEDICAL_GENDER_THERAPY_MENU: [
                # Обработчики для выбора T или E
                CallbackQueryHandler(medical_menu), # Временный обработчик, нужно детализировать
                CallbackQueryHandler(main_menu, pattern='^back_to_medical$'),
            ],
            BotState.MEDICAL_FTM_HRT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_menu), # Временный
                CallbackQueryHandler(medical_menu, pattern='^back_to_hrt$'),
            ],
            BotState.MEDICAL_MTF_HRT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_menu), # Временный
                CallbackQueryHandler(medical_menu, pattern='^back_to_hrt$'),
            ],
            BotState.MEDICAL_SURGERY_PLANNING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_menu), # Временный
                CallbackQueryHandler(medical_menu, pattern='^back_to_medical$'),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(request_legal_docs_callback, pattern='^request_legal_docs$'))
    application.add_handler(CallbackQueryHandler(plan_surgery_callback, pattern='^plan_surgery$'))
    application.add_handler(CallbackQueryHandler(feedback_handler, pattern='^feedback_'))
    application.add_error_handler(error_handler)

    # Добавление обработчиков без состояний (команды вне ConversationHandler)
    application.add_handler(CommandHandler("resources", list_resources))

    application.run_polling()

if __name__ == "__main__":
    main()
