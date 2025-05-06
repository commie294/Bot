import os
import hashlib
import secrets
import json
import logging
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, JobQueue
from telegram.error import TelegramError, NetworkError, Forbidden
from bot_responses import MESSAGE_SENT_SUCCESS, MESSAGE_SEND_ERROR, CONSULTATION_PROMPT, SURGERY_PLANNING_PROMPT
from keyboards import MAIN_MENU_BUTTONS, BACK_BUTTON, FINISH_MENU_KEYBOARD
from utils.constants import BotState, REQUEST_TYPES

logger = logging.getLogger(__name__)

def generate_message_id(user_id: int) -> str:
    random_bytes = secrets.token_bytes(16)
    return hashlib.sha256(f"{os.getenv('HASH_SALT')}_{user_id}_{random_bytes}".encode()).hexdigest()[:8]

def load_channels():
    try:
        with open("data/channels.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Файл channels.json не найден.")
        raise

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

def load_reminders():
    try:
        with open("data/reminders.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_reminder(user_id: int, reminder_time: str, message: str, job_queue: JobQueue):
    reminders = load_reminders()
    reminder_id = f"{user_id}_{len(reminders.get(str(user_id), []))}"
    reminders.setdefault(str(user_id), []).append({"id": reminder_id, "time": reminder_time, "message": message})
    with open("data/reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)
    # Планирование напоминания
    job_queue.run_once(send_reminder, datetime.fromisoformat(reminder_time), data={"user_id": user_id, "message": message, "reminder_id": reminder_id})

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(job.data["user_id"], f"⏰ Напоминание: {job.data['message']}")
    # Удаление напоминания после отправки (опционально)
    reminders = load_reminders()
    user_reminders = reminders.get(str(job.data["user_id"]), [])
    reminders[str(job.data["user_id"])] = [r for r in user_reminders if r["id"] != job.data["reminder_id"]]
    with open("data/reminders.json", "w") as f:
        json.dump(reminders, f, indent=2)

# Оставшиеся функции (handle_typing, error_handler, etc.) остаются без изменений

def generate_message_id(user_id: int) -> str:
    """Генерирует хеш для анонимной идентификации сообщений."""
    random_bytes = secrets.token_bytes(16)
    return hashlib.sha256(f"{os.getenv('HASH_SALT')}_{user_id}_{random_bytes}".encode()).hexdigest()[:8]

def load_channels():
    """Загружает каналы из JSON."""
    try:
        with open("data/channels.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Файл channels.json не найден.")
        raise

def update_stats(user_id: int, action: str):
    """Обновляет статистику использования."""
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

async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает текстовый ввод и вложения пользователя."""
    from handlers.main_menu import main_menu
    from handlers.help_menu import help_menu

    request_type = context.user_data.get("request_type", "Сообщение")
    
    # Rate limiting
    user_id = update.effective_user.id
    last_message_time = context.user_data.get(f"last_message_{user_id}")
    now = datetime.now()
    if last_message_time and now - last_message_time < timedelta(seconds=10):
        await update.message.reply_text("Пожалуйста, подождите 10 секунд перед отправкой нового сообщения.")
        return BotState.TYPING
    context.user_data[f"last_message_{user_id}"] = now

    # Обработка вложений
    if update.message.document:
        if update.message.document.file_size > 20 * 1024 * 1024:  # Лимит 20 МБ
            await update.message.reply_text("Файл слишком большой. Пожалуйста, загрузите файл до 20 МБ.")
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
                ])
            )
            update_stats(user_id, f"document_{request_type}")
            return BotState.MAIN_MENU
        except TelegramError as e:
            logger.error(f"Ошибка отправки документа: {e}")
            await update.message.reply_text(MESSAGE_SEND_ERROR.format(e))
            return BotState.MAIN_MENU

    # Обработка текста
    user_text = update.message.text
    if len(user_text) > 4000:
        await update.message.reply_text("Ваше сообщение слишком длинное. Пожалуйста, сократите его.")
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
                text=f"Запрос от пользователя:\n\n{user_text}"
            )
            await update.message.reply_text(
                MESSAGE_SENT_SUCCESS,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👍 Отлично", callback_data="feedback_good")],
                    [InlineKeyboardButton("👎 Плохо", callback_data="feedback_bad")]
                ])
            )
            update_stats(user_id, request_type)
            return BotState.MAIN_MENU
        except NetworkError:
            await update.message.reply_text("Ошибка сети. Попробуйте позже.")
            return BotState.MAIN_MENU
        except Forbidden:
            logger.error(f"Бот не имеет доступа к каналу {channel_name}")
            await update.message.reply_text("Ошибка конфигурации. Свяжитесь с администратором.")
            return BotState.MAIN_MENU
        except TelegramError as e:
            logger.error(f"Telegram API error: {e}")
            await update.message.reply_text(MESSAGE_SEND_ERROR.format(e))
            return BotState.MAIN_MENU
    await update.message.reply_text("Ошибка обработки запроса.")
    return BotState.MAIN_MENU

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логирует ошибки и уведомляет пользователя."""
    logger.error(f"Exception: {context.error}", exc_info=True)
    if update and update.message:
        await update.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте позже или свяжитесь с администратором."
        )
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")
    if admin_chat_id:
        try:
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=f"⚠️ Ошибка: {context.error}",
                parse_mode="Markdown"
            )
        except TelegramError as e:
            logger.error(f"Ошибка отправки ошибки администратору: {e}")

async def request_legal_docs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик для запроса консультации по документам."""
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
    """Обработчик для планирования операции."""
    query = update.callback_query
    await query.answer()
    context.user_data["request_type"] = REQUEST_TYPES["surgery"]
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=SURGERY_PLANNING_PROMPT,
        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
    )
    return BotState.TYPING

async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает обратную связь от пользователя."""
    query = update
