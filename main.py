import os
import logging
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from telegram.error import TelegramError

from handlers.main_menu import start, main_menu
from handlers.help_menu import help_menu
from handlers.typing import handle_typing
from handlers.faq_legal import faq_legal, request_legal_docs_callback
from handlers.medical_menu import medical_menu
from handlers.medical_gender_therapy import medical_gender_therapy_menu
from handlers.medical_hrt import medical_ftm_hrt, medical_mtf_hrt
from handlers.medical_surgery import medical_surgery_planning, plan_surgery_callback
from handlers.volunteer import (
    volunteer_start_callback,
    ask_volunteer_name,
    get_volunteer_region,
    volunteer_help_type_handler,
    volunteer_contact_handler,
    volunteer_finish_handler,
)
from handlers.anonymous_message import anonymous_message
from handlers.cancel import cancel
from utils.message_id_generator import generate_message_id  # Импортируем утилиту
from keyboards import MAIN_MENU_BUTTONS
from channels import CHANNELS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
DIY_HRT_GUIDE_PATH = os.getenv("DIY_HRT_GUIDE_PATH")

if BOT_TOKEN:
    print(f"Токен бота: {BOT_TOKEN}")
else:
    print("Ошибка: Переменная BOT_TOKEN не найдена.")

(
    START,
    MAIN_MENU,
    HELP_MENU,
    TYPING,
    FAQ_LEGAL,
    MEDICAL_MENU,
    VOLUNTEER_CONFIRM_START,
    VOLUNTEER_NAME,
    VOLUNTEER_REGION,
    VOLUNTEER_HELP_TYPE,
    VOLUNTEER_CONTACT,
    ANONYMOUS_MESSAGE,
    MEDICAL_GENDER_THERAPY_MENU,
    MEDICAL_FTM_HRT,
    MEDICAL_MTF_HRT,
    MEDICAL_SURGERY_PLANNING,
    DONE_STATE,
) = range(17)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a telegram message to notify the developer."""
    logger.error(f"Exception while handling an update {update}:", exc_info=context.error)
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"⚠️ Произошла ошибка при обработке обновления `{update}`:\n\n`{context.error}`",
                parse_mode="MarkdownV2",            )
        except TelegramError as e:
            logger.error(f"Ошибка Telegram API при отправке сообщения об ошибке администратору: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при отправке сообщения об ошибке администратору: {e}", exc_info=True)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_menu)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, faq_legal)],
            MEDICAL_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_menu)],
            MEDICAL_GENDER_THERAPY_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_gender_therapy_menu)
            ],
            MEDICAL_FTM_HRT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_ftm_hrt)
            ],
            MEDICAL_MTF_HRT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_mtf_hrt)
            ],
            MEDICAL_SURGERY_PLANNING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, medical_surgery_planning)
            ],
            VOLUNTEER_CONFIRM_START: [MessageHandler(filters.TEXT & filters.Regex("^Далее$"), ask_volunteer_name)],
            VOLUNTEER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Отмена)$"), get_volunteer_region)],
            VOLUNTEER_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Отмена)$"), volunteer_help_type_handler)],
            VOLUNTEER_HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Отмена)$"), volunteer_contact_handler)],
            VOLUNTEER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Отмена)$"), volunteer_finish_handler)],
            ANONYMOUS_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, anonymous_message)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^volunteer_start_callback$')) # Обработчик в main_menu
    application.add_handler(CallbackQueryHandler(faq_legal, pattern='^request_legal_docs$'))     # Обработчик в faq_legal
    application.add_handler(CallbackQueryHandler(medical_surgery_planning, pattern='^plan_surgery$')) # Обработчик в medical_surgery
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
