import os
import sys
import logging
import hashlib
import dotenv
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
from telegram.error import TelegramError
from bot_responses import *
from keyboards import *
from channels import CHANNELS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
HASH_SALT = os.getenv("HASH_SALT")

if not BOT_TOKEN:
    logger.error("Не удалось загрузить BOT_TOKEN из .env")
    sys.exit(1)

(
    START,
    MAIN_MENU,
    HELP_MENU,
    TYPING,
    FAQ_LEGAL,
    MEDICAL_MENU,
    VOLUNTEER_START,
    VOLUNTEER_NAME,
    VOLUNTEER_REGION,
    VOLUNTEER_HELP_TYPE,
    VOLUNTEER_CONTACT,
    ANONYMOUS_MESSAGE,
    MEDICAL_GENDER_THERAPY,
    MEDICAL_FTM_HRT,
    MEDICAL_MTF_HRT,
    MEDICAL_SURGERY,
    CONFIRM
) = range(17)

def generate_message_id(user_id: int) -> str:
    return hashlib.sha256(f"{HASH_SALT}_{user_id}_{os.urandom(16)}".encode()).hexdigest()[:8]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        START_MESSAGE,
        reply_markup=MAIN_MENU,
        parse_mode="Markdown"
    )
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    
    if text == "🆘 Попросить о помощи":
        await update.message.reply_text(
            HELP_MENU_MESSAGE,
            reply_markup=HELP_INLINE_MENU
        )
        return HELP_MENU
    elif text == "➕ Предложить ресурс":
        context.user_data["request_type"] = "Ресурс"
        await update.message.reply_text(
            RESOURCE_PROMPT_MESSAGE,
            reply_markup=BASIC_NAVIGATION
        )
        return TYPING
    elif text == "🤝 Стать волонтером":
        await update.message.reply_text(
            VOLUNTEER_MESSAGE,
            reply_markup=VOLUNTEER_KEYBOARD
        )
        return VOLUNTEER_START
    elif text == "💸 Поддержать проект":
        await update.message.reply_text(
            DONATE_MESSAGE,
            parse_mode="Markdown",
            reply_markup=MAIN_MENU
        )
        return MAIN_MENU
    elif text == "✉️ Анонимное сообщение":
        await update.message.reply_text(
            "Пожалуйста, напишите ваше анонимное сообщение:",
            reply_markup=ANONYMOUS_KEYBOARD
        )
        context.user_data["request_type"] = "Анонимное сообщение"
        return ANONYMOUS_MESSAGE
    else:
        await update.message.reply_text(CHOOSE_FROM_MENU)
        return MAIN_MENU

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == "help_legal":
            await query.edit_message_text(
                "Выберите категорию юридической помощи:",
                reply_markup=LEGAL_INLINE_MENU
            )
            return FAQ_LEGAL
        elif query.data == "help_medical":
            await query.edit_message_text(
                "Выберите категорию медицинской помощи:",
                reply_markup=MEDICAL_INLINE_MENU
            )
            return MEDICAL_MENU
        elif query.data == "help_emergency":
            context.user_data["request_type"] = "Срочная помощь"
            await query.edit_message_text(EMERGENCY_MESSAGE)
            return TYPING
        elif query.data == "back_main":
            await query.edit_message_text(
                START_MESSAGE,
                reply_markup=MAIN_MENU
            )
            return MAIN_MENU
    else:
        text = update.message.text
        if text == "⬅️ Назад":
            await update.message.reply_text(
                START_MESSAGE,
                reply_markup=MAIN_MENU
            )
            return MAIN_MENU
    
    return HELP_MENU

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == "legal_families":
        await query.edit_message_text(
            LGBT_FAMILIES_INFO,
            parse_mode="Markdown"
        )
    elif query.data == "legal_docs":
        await query.edit_message_text(
            DOCUMENTS_MESSAGE,
            parse_mode="Markdown"
        )
    elif query.data == "legal_consult":
        context.user_data["request_type"] = "Юридическая консультация"
        await query.edit_message_text(CONSULTATION_PROMPT)
        return TYPING
    elif query.data == "back_help":
        await query.edit_message_text(
            HELP_MENU_MESSAGE,
            reply_markup=HELP_INLINE_MENU
        )
        return HELP_MENU
    
    return FAQ_LEGAL

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == "med_hrt":
        await query.edit_message_text(
            GENDER_THERAPY_MESSAGE,
            reply_markup=HRT_INLINE_MENU,
            parse_mode="Markdown"
        )
        return MEDICAL_GENDER_THERAPY
    elif query.data == "med_surgery":
        await query.edit_message_text(
            SURGERY_INFO_MESSAGE,
            reply_markup=SURGERY_INLINE_MENU,
            parse_mode="Markdown"
        )
        return MEDICAL_SURGERY
    elif query.data == "med_consult":
        context.user_data["request_type"] = "Медицинская консультация"
        await query.edit_message_text(CONSULTATION_PROMPT)
        return TYPING
    elif query.data == "back_help":
        await query.edit_message_text(
            HELP_MENU_MESSAGE,
            reply_markup=HELP_INLINE_MENU
        )
        return HELP_MENU
    
    return MEDICAL_MENU

async def medical_gender_therapy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == "hrt_male":
        await query.edit_message_text(
            MASCULINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["DIY"],
                    ["Запросить консультацию по мужской ГТ"],
                    ["⬅️ Назад"],
                ],
                resize_keyboard=True,
            ),
        )
        return MEDICAL_FTM_HRT
    elif query.data == "hrt_female":
        await query.edit_message_text(
            FEMINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["DIY"],
                    ["Запросить консультацию по женской ГТ"],
                    ["⬅️ Назад"],
                ],
                resize_keyboard=True,
            ),
        )
        return MEDICAL_MTF_HRT
    elif query.data == "back_medical":
        await query.edit_message_text(
            "Медицинская помощь:",
            reply_markup=MEDICAL_INLINE_MENU
        )
        return MEDICAL_MENU
    
    return MEDICAL_GENDER_THERAPY

async def medical_surgery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == "surgery_ftm":
        await query.edit_message_text(
            FTM_SURGERY_INFO,
            reply_markup=SURGERY_INLINE_MENU,
            parse_mode="Markdown"
        )
    elif query.data == "surgery_mtf":
        await query.edit_message_text(
            MTF_SURGERY_INFO,
            reply_markup=SURGERY_INLINE_MENU,
            parse_mode="Markdown"
        )
    elif query.data == "surgery_plan":
        context.user_data["request_type"] = "Планирование операции"
        await query.edit_message_text(
            SURGERY_PLANNING_PROMPT,
            reply_markup=BASIC_NAVIGATION
        )
        return TYPING
    elif query.data == "back_medical":
        await query.edit_message_text(
            "Медицинская помощь:",
            reply_markup=MEDICAL_INLINE_MENU
        )
        return MEDICAL_MENU
    
    return MEDICAL_SURGERY

async def send_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE, channel_key: str, message_type: str):
    try:
        message_id = generate_message_id(update.effective_user.id)
        await context.bot.send_message(
            chat_id=CHANNELS[channel_key],
            text=f"Новый запрос ({message_type}) [{message_id}]:\n\n{update.message.text}"
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        return False

async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == BACK_BUTTON:
        return await main_menu(update, context)
    
    request_type = context.user_data.get("request_type")
    user_text = update.message.text
    
    channel_map = {
        "Ресурс": "t64_misc",
        "Срочная помощь": "t64_gen",
        "Юридическая консультация": "t64_legal",
        "Медицинская консультация": "t64_gen",
        "Планирование операции": "t64_gen",
        "Анонимное сообщение": "t64_misc"
    }
    
    channel = channel_map.get(request_type)
    if not channel or channel not in CHANNELS:
        await update.message.reply_text(MESSAGE_SEND_ERROR)
        return MAIN_MENU
    
    if await send_to_channel(update, context, channel, request_type):
        await update.message.reply_text(
            MESSAGE_SENT_SUCCESS,
            reply_markup=MAIN_MENU
        )
    else:
        await update.message.reply_text(
            MESSAGE_SEND_ERROR,
            reply_markup=MAIN_MENU
        )
    
    return MAIN_MENU

async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == BACK_BUTTON:
        return await main_menu(update, context)
    
    if await send_to_channel(update, context, "t64_misc", "Анонимное сообщение"):
        await update.message.reply_text(
            "Ваше анонимное сообщение отправлено!",
            reply_markup=MAIN_MENU
        )
    else:
        await update.message.reply_text(
            "Ошибка отправки. Попробуйте позже.",
            reply_markup=MAIN_MENU
        )
    
    return MAIN_MENU
    
async def volunteer_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Как вас зовут? (реальное имя или псевдоним)",
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
    )
    return VOLUNTEER_NAME

async def volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name) < 2 or len(name) > 50:
        await update.message.reply_text("Имя должно быть от 2 до 50 символов. Попробуйте еще раз.")
        return VOLUNTEER_NAME
    
    context.user_data["volunteer"] = {"name": name}
    await update.message.reply_text(
        "Из какого вы региона/города?",
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
    )
    return VOLUNTEER_REGION

async def volunteer_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    region = update.message.text.strip()
    if len(region) < 2:
        await update.message.reply_text("Укажите корректный регион.")
        return VOLUNTEER_REGION
    
    context.user_data["volunteer"]["region"] = region
    await update.message.reply_text(
        "Выберите тип помощи:",
        reply_markup=VOLUNTEER_TYPES
    )
    return VOLUNTEER_HELP_TYPE

async def volunteer_help_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    help_type = update.message.text
    if help_type not in [btn[0] for row in VOLUNTEER_TYPES.keyboard for btn in row]:
        await update.message.reply_text("Пожалуйста, выберите вариант из предложенных.")
        return VOLUNTEER_HELP_TYPE
    
    context.user_data["volunteer"]["help_type"] = help_type
    await update.message.reply_text(
        "Как с вами связаться? (телеграм @username или телефон)",
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
    )
    return VOLUNTEER_CONTACT

async def volunteer_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact = update.message.text.strip()
    if not contact:
        await update.message.reply_text("Пожалуйста, укажите контакты.")
        return VOLUNTEER_CONTACT
    
    volunteer_data = context.user_data["volunteer"]
    volunteer_data["contact"] = contact
    user = update.effective_user
    
    summary = (
        "Новая заявка волонтера:\n\n"
        f"Имя: {volunteer_data['name']}\n"
        f"Регион: {volunteer_data['region']}\n"
        f"Тип помощи: {volunteer_data['help_type']}\n"
        f"Контакты: {contact}\n\n"
        f"ID: {user.id}\n"
        f"Username: @{user.username if user.username else 'нет'}"
    )
    
    try:
        await context.bot.send_message(
            chat_id=CHANNELS["t64_admin"],
            text=summary
        )
        await update.message.reply_text(
            "Спасибо! Ваша заявка отправлена.",
            reply_markup=MAIN_MENU
        )
    except Exception as e:
        logger.error(f"Ошибка отправки заявки: {e}")
        await update.message.reply_text(
            "Ошибка отправки. Попробуйте позже.",
            reply_markup=MAIN_MENU
        )
    
    context.user_data.clear()
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=MAIN_MENU
    )
    context.user_data.clear()
    return MAIN_MENU

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=True)
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"Ошибка в боте:\n{context.error}"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить ошибку админу: {e}")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            HELP_MENU: [CallbackQueryHandler(help_menu)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing)],
            FAQ_LEGAL: [CallbackQueryHandler(faq_legal)],
            MEDICAL_MENU: [CallbackQueryHandler(medical_menu)],
            MEDICAL_GENDER_THERAPY: [CallbackQueryHandler(medical_gender_therapy)],
            MEDICAL_SURGERY: [CallbackQueryHandler(medical_surgery)],
            VOLUNTEER_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_start)],
            VOLUNTEER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_name)],
            VOLUNTEER_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_region)],
            VOLUNTEER_HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_help_type)],
            VOLUNTEER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_contact)],
            ANONYMOUS_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, anonymous_message)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
