import os
import hashlib
import secrets
import json
import logging
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import TelegramError, NetworkError, Forbidden
from bot_responses import MESSAGE_SENT_SUCCESS, MESSAGE_SEND_ERROR, CONSULTATION_PROMPT, SURGERY_PLANNING_PROMPT
from keyboards import MAIN_MENU_BUTTONS, BACK_BUTTON, FINISH_MENU_KEYBOARD
from utils.constants import BotState, REQUEST_TYPES
import traceback

logger = logging.getLogger(__name__)

_channels_cache = None

def generate_message_id(user_id: int) -> str:
    random_bytes = secrets.token_bytes(16)
    return hashlib.sha256(f"{os.getenv('HASH_SALT')}_{user_id}_{random_bytes}".encode()).hexdigest()[:8]

def load_channels():
    global _channels_cache
    if _channels_cache is None:
        try:
            with open("data/channels.json", "r") as f:
                _channels_cache = json.load(f)
        except FileNotFoundError:
            logger.error("Файл channels.json не найден.")
            raise
    return _channels_cache

def update_stats(user_id: int, action: str):
    stats_file = "data/stats.json"
    try:
        with open(stats_file, "r") as f:
            stats = json.load(f)
    except FileNotFoundError:
        stats = {}

    user_key = str(user_id)
    stats.setdefault(user_key, {}).setdefault(action, 0)
    stats[user_key][action] += 1

    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

async def check_rate_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    last_message_time = context.user_data.get(f"last_message_{user_id}")
    now = datetime.now()
    if last_message_time and now - last_message_time < timedelta(seconds=10):
        await update.message.reply_text(
            "Пожалуйста, подождите 10 секунд перед следующим действием\\.",
            parse_mode="MarkdownV2"
        )
        return False
    context.user_data[f"last_message_{user_id}"] = now
    return True

async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from handlers.main_menu import main_menu
    from handlers.help_menu import help_menu

    if not await check_rate_limit(update, context):
        return BotState.TYPING

    request_type = context.user_data.get("request_type", "Сообщение")

    if update.message.document:
        if update.message.document.file_size > 20 * 1024 * 1024:
            await update.message.reply_text(
                "Файл слишком большой\\. Пожалуйста, загрузите файл до 20 МБ\\.",
                parse_mode="MarkdownV2"
            )
            return BotState.TYPING
        try:
            channels = load_channels()
            await context.bot.send_document(
                chat_id=channels.get("t64_misc"),
                document=update.message.document.file_id,
                caption=f"Файл от пользователя: {update.message.caption or 'Без описания'}"
            )
            await update.message.reply_text(
                MESSAGE_SENT_SUCCESS,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👍 Отлично", callback_data="feedback_good")],
                    [InlineKeyboardButton("👎 Плохо", callback_data="feedback_bad")]
                ]),
                parse_mode="MarkdownV2"
            )
            update_stats(update.effective_user.id, f"document_{request_type}")
            return BotState.MAIN_MENU
        except TelegramError as e:
            logger.error(f"Ошибка отправки документа: {e}")
            await update.message.reply_text(
                MESSAGE_SEND_ERROR.format(e),
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU

    user_text = update.message.text
    if len(user_text) > 4000:
        await update.message.reply_text(
            "Ваше сообщение слишком длинное\\. Пожалуйста, сократите его\\.",
            parse_mode="MarkdownV2"
        )
        return BotState.TYPING

    if user_text == BACK_BUTTON:
        if request_type in [REQUEST_TYPES["resource"], REQUEST_TYPES["emergency"], REQUEST_TYPES["housing"], REQUEST_TYPES["psych"]]:
            return await help_menu(update, context)
        return await main_menu(update, context)

    channel_mapping = {
        REQUEST_TYPES["resource"]: "t64_misc",
        REQUEST_TYPES["emergency"]: "t64_gen",
        REQUEST_TYPES["legal_abuse"]: "t64_legal",
        REQUEST_TYPES["legal_consult"]: "t64_legal",
        REQUEST_TYPES["medical_consult"]: "t64_gen",
        REQUEST_TYPES["ftm_hrt"]: "t64_gen",
        REQUEST_TYPES["mtf_hrt"]: "t64_gen",
        REQUEST_TYPES["surgery"]: "t64_gen",
        REQUEST_TYPES["psych"]: "t64_psych",
        REQUEST_TYPES["housing"]: "t64_gen",
    }

    channel_name = channel_mapping.get(request_type)
    if channel_name:
        try:
            channels = load_channels()
            await context.bot.send_message(
                chat_id=channels.get(channel_name),
                text=f"Запрос от пользователя:\n\n{user_text}",
                parse_mode="MarkdownV2"
            )
            await update.message.reply_text(
                MESSAGE_SENT_SUCCESS,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👍 Отлично", callback_data="feedback_good")],
                    [InlineKeyboardButton("👎 Плохо", callback_data="feedback_bad")]
                ]),
                parse_mode="MarkdownV2"
            )
            update_stats(update.effective_user.id, request_type)
            return BotState.MAIN_MENU
        except NetworkError:
            await update.message.reply_text(
                "Ошибка сети\\. Попробуйте позже\\.",
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        except Forbidden:
            logger.error(f"Бот не имеет доступа к каналу {channel_name}")
            await update.message.reply_text(
                "Ошибка конфигурации\\. Свяжитесь с администратором\\.",
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
        except TelegramError as e:
            logger.error(f"Telegram API error: {e}")
            await update.message.reply_text(
                MESSAGE_SEND_ERROR.format(e),
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
    await update.message.reply_text(
        "Ошибка обработки запроса\\.",
        parse_mode="MarkdownV2"
    )
    return BotState.MAIN_MENU

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=True)
    error_trace = "".join(traceback.format_exception(type(context.error), context.error, context.error.__traceback__))
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")
    if admin_chat_id:
        await context.bot.send_message(
            chat_id=admin_chat_id,
            text=f"*⚠️ Ошибка:*\n\n{context.error}\n\n*Трассировка:*\n{error_trace[:4000]}",
            parse_mode="MarkdownV2"
        )
    if update and update.message:
        await update.message.reply_text(
            "Произошла ошибка\\. Пожалуйста, попробуйте позже или свяжитесь с администратором\\.",
            parse_mode="MarkdownV2"
        )

async def request_legal_docs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["request_type"] = REQUEST_TYPES["legal_consult"]
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=CONSULTATION_PROMPT,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
    )
    return BotState.TYPING

async def plan_surgery_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["request_type"] = REQUEST_TYPES["surgery"]
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=SURGERY_PLANNING_PROMPT,
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        parse_mode="MarkdownV2"
    )
    return BotState.TYPING

async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    feedback = "positive" if query.data == "feedback_good" else "negative"
    user_id = query.from_user.id
    with open("data/feedback.json", "a") as f:
        json.dump({"user_id": user_id, "feedback": feedback, "timestamp": datetime.now().isoformat()}, f)
        f.write("\n")
    await query.message.edit_text(
        "Спасибо за ваш отзыв\\!",
        parse_mode="MarkdownV2"
    )
