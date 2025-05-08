import os
import logging
import signal
import asyncio
import json
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, InlineQueryHandler
from handlers.main_menu import start, main_menu
from handlers.help_menu import help_menu, faq_legal
from handlers.medical import medical_menu, medical_gender_therapy_menu, medical_ftm_hrt, medical_mtf_hrt, medical_surgery_planning
from handlers.volunteer import ask_volunteer_name, get_volunteer_region, volunteer_help_type_handler, volunteer_contact_handler, volunteer_finish_handler
from handlers.anonymous import anonymous_message
from handlers.resources import resource_proposal, list_resources
from utils.message_utils import error_handler, request_legal_docs_callback, plan_surgery_callback, handle_typing, feedback_handler, check_rate_limit
from utils.resource_utils import load_resources, fetch_resources_from_post, update_telegram_post, approve_resource
from utils.constants import BotState, MAIN_MENU_ACTIONS, REQUEST_TYPES, check_env_vars
from keyboards import MAIN_MENU_BUTTONS, VOLUNTEER_START_KEYBOARD, BACK_BUTTON, DONE_BUTTON, HELP_MENU_BUTTONS
from bot_responses import START_MESSAGE, CHOOSE_FROM_MENU, VOLUNTEER_MESSAGE, DONATE_MESSAGE, FAREWELL_MESSAGE

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
    return ConversationHandler.END

async def update_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != os.getenv("ADMIN_CHAT_ID"):
        await update.message.reply_text(CHOOSE_FROM_MENU, parse_mode="MarkdownV2")
        return
    resources = await fetch_resources_from_post(context.bot, "-1002457776742", 9)
    with open("data/resources.json", "w") as f:
        json.dump(resources, f, indent=2)
    await update.message.reply_text(f"Обновлено {len(resources)} ресурсов\\.", parse_mode="MarkdownV2")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != os.getenv("ADMIN_CHAT_ID"):
        await update.message.reply_text(CHOOSE_FROM_MENU, parse_mode="MarkdownV2")
        return
    try:
        with open("data/stats.json", "r") as f:
            stats = json.load(f)
        message = "*Статистика:*\n\n"
        for user_id, actions in stats.items():
            message += f"Пользователь {user_id}:\n"
            for action, count in actions.items():
                message += f"  {action}: {count}\n"
        await update.message.reply_text(message, parse_mode="MarkdownV2")
    except FileNotFoundError:
        await update.message.reply_text("Статистика не найдена\\.", parse_mode="MarkdownV2")

async def resource_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action, resource_id = query.data.split("_", 1)
    resource_id = int(resource_id.split("_")[-1])
    if action == "approve_resource":
        resource = await approve_resource(resource_id)
        if resource:
            await query.message.edit_text(
                f"*Ресурс одобрен:*\n\n*Название:* {resource['title']}\n*Описание:* {resource['description']}\n*Ссылка:* {resource['link']}",
                parse_mode="MarkdownV2"
            )
            await update_telegram_post(context.bot, "@tperehod", 9)
        else:
            await query.message.edit_text("Ресурс не найден\\.", parse_mode="MarkdownV2")
    elif action == "reject_resource":
        await query.message.edit_text("Ресурс отклонён\\.", parse_mode="MarkdownV2")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    resources = load_resources()
    results = [
        InlineQueryResultArticle(
            id=str(res["id"]),
            title=res["title"],
            input_message_content=InputTextMessageContent(
                f"📚 *{res['title']}*\n{res['description']}\n🔗 {res['link']}",
                parse_mode="MarkdownV2"
            )
        )
        for res in resources if query.lower() in res["title"].lower() or query.lower() in res["description"].lower()
    ]
    await update.inline_query.answer(results)

async def main() -> None:
    check_env_vars()
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN не найден в файле .env")
        return

    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BotState.MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
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
            BotState.RESOURCE_PROPOSAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, resource_proposal)],
            BotState.DONE_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(request_legal_docs_callback, pattern='^request_legal_docs$'))
    application.add_handler(CallbackQueryHandler(plan_surgery_callback, pattern='^plan_surgery$'))
    application.add_handler(CallbackQueryHandler(feedback_handler, pattern='^feedback_(good|bad)$'))
    application.add_handler(CallbackQueryHandler(resource_moderation, pattern='^(approve|reject)_resource_'))
    application.add_handler(CommandHandler("resources", list_resources))
    application.add_handler(CommandHandler("updateresources", update_resources))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_error_handler(error_handler)

    # Запуск polling (правильный способ)
    logger.info("Starting bot with polling...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Future()  # Держим event loop запущенным

if __name__ == "__main__":
    asyncio.run(main())
