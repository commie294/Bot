import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
)
from handlers.main_menu import start, main_menu
from handlers.help_menu import help_menu, faq_legal
from handlers.medical import medical_menu, medical_gender_therapy_menu, medical_ftm_hrt, medical_mtf_hrt, medical_surgery_planning, set_reminder
from handlers.volunteer import ask_volunteer_name, get_volunteer_region, volunteer_help_type_handler, volunteer_contact_handler, volunteer_finish_handler
from handlers.anonymous import anonymous_message
from handlers.donate import donate
from utils.message_utils import error_handler, request_legal_docs_callback, plan_surgery_callback, handle_typing, feedback_handler
from utils.constants import BotState, check_env_vars
from keyboards import MAIN_MENU_BUTTONS

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

def main() -> None:
    check_env_vars()
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BotState.MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            BotState.HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_menu)],
            BotState.TYPING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing),
                MessageHandler(filters.Document.ALL, handle_typing),
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
            BotState.DONE_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            BotState.SET_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_reminder)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Регистрация обработчиков
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(request_legal_docs_callback, pattern="^request_legal_docs$"))
    application.add_handler(CallbackQueryHandler(plan_surgery_callback, pattern="^plan_surgery$"))
    application.add_handler(CallbackQueryHandler(feedback_handler, pattern="^feedback_(good|bad)$"))
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет текущее действие и возвращает в главное меню."""
    await update.message.reply_text(
        "Действие отменено.", reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
    await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=keyboard)
    return BotState.MAIN_MENU

if __name__ == "__main__":
    main()
