import logging
from datetime import datetime
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot_responses import MEDICAL_CONSULTATION_PROMPT, FTM_HRT_MESSAGE, MTF_HRT_MESSAGE, GENDER_THERAPY_PROMPT, SURGERY_PLANNING_PROMPT
from keyboards import MEDICAL_GENDER_THERAPY_BUTTONS, BACK_BUTTON, MAIN_MENU_BUTTONS
from utils.message_utils import update_stats
from utils.constants import BotState, REQUEST_TYPES

logger = logging.getLogger(__name__)

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True)
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=keyboard,
        )
        return BotState.MAIN_MENU
    elif choice == "🗣️ Медицинская консультация":
        context.user_data["request_type"] = REQUEST_TYPES["medical_consult"]
        await update.message.reply_text(
            MEDICAL_CONSULTATION_PROMPT,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return BotState.TYPING
    elif choice == "💉HRT":
        keyboard = ReplyKeyboardMarkup(MEDICAL_GENDER_THERAPY_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            GENDER_THERAPY_PROMPT,
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_GENDER_THERAPY_MENU
    elif choice == "❓ F64":
        context.user_data["request_type"] = REQUEST_TYPES["medical_consult"]
        await update.message.reply_text(
            "Опишите ваш вопрос по F64, и мы постараемся помочь:",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return BotState.TYPING
    elif choice == "⚕️ Операции":
        context.user_data["request_type"] = REQUEST_TYPES["surgery"]
        await update.message.reply_text(
            SURGERY_PLANNING_PROMPT,
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return BotState.TYPING
    elif choice == "⏰ Напоминания":
        await update.message.reply_text(
            "Введите время напоминания (в формате ЧЧ:ММ, например, 08:00) и сообщение (например, 'Принять эстрадиол'):",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return BotState.SET_REMINDER
    await update.message.reply_text(
        "Пожалуйста, выберите одну из опций.",
        reply_markup=ReplyKeyboardMarkup([["🗣️ Медицинская консультация"], ["💉HRT"], ["❓ F64"], ["⚕️ Операции"], ["⏰ Напоминания"], [BACK_BUTTON]], resize_keyboard=True),
    )
    return BotState.MEDICAL_MENU

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Устанавливает напоминание о медицинской процедуре."""
    user_input = update.message.text
    if user_input == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup([["🗣️ Медицинская консультация"], ["💉HRT"], ["❓ F64"], ["⚕️ Операции"], ["⏰ Напоминания"], [BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Вы вернулись в медицинское меню.",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_MENU

    try:
        time_str, reminder_message = user_input.split(" ", 1)
        reminder_time = datetime.strptime(time_str, "%H:%M").replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day if datetime.now().time() < datetime.strptime(time_str, "%H:%M").time() else datetime.now().day + 1
        )
        user_id = str(update.effective_user.id)
        
        # Сохраняем напоминание в reminders.json
        try:
            with open("data/reminders.json", "r") as f:
                reminders = json.load(f)
        except FileNotFoundError:
            reminders = {}

        if user_id not in reminders:
            reminders[user_id] = []
        reminders[user_id].append({
            "time": reminder_time.strftime("%Y-%m-%d %H:%M"),
            "message": reminder_message
        })

        with open("data/reminders.json", "w") as f:
            json.dump(reminders, f, indent=2)

        # Устанавливаем задачу в job_queue
        context.job_queue.run_once(
            callback=send_reminder,
            when=reminder_time,
            data={"user_id": user_id, "message": reminder_message},
            name=f"reminder_{user_id}_{reminder_time.timestamp()}"
        )

        await update.message.reply_text(
            f"Напоминание установлено на {time_str}: {reminder_message}",
            reply_markup=ReplyKeyboardMarkup([["🗣️ Медицинская консультация"], ["💉HRT"], ["❓ F64"], ["⚕️ Операции"], ["⏰ Напоминания"], [BACK_BUTTON]], resize_keyboard=True),
        )
        update_stats(user_id, "set_reminder")
        return BotState.MEDICAL_MENU

    except ValueError:
        await update.message.reply_text(
            "Неверный формат. Пожалуйста, введите время в формате ЧЧ:ММ и сообщение (например, '08:00 Принять эстрадиол').",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return BotState.SET_REMINDER

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет напоминание пользователю."""
    job = context.job
    user_id = job.data["user_id"]
    message = job.data["message"]
    await context.bot.send_message(
        chat_id=user_id,
        text=f"⏰ Напоминание: {message}"
    )

async def medical_gender_therapy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup([["🗣️ Медицинская консультация"], ["💉HRT"], ["❓ F64"], ["⚕️ Операции"], ["⏰ Напоминания"], [BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Вы вернулись в медицинское меню.",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_MENU
    elif choice == "👨‍⚕️ FTM":
        context.user_data["request_type"] = REQUEST_TYPES["ftm_hrt"]
        await update.message.reply_text(
            FTM_HRT_MESSAGE,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return BotState.MEDICAL_FTM_HRT
    elif choice == "👩‍⚕️ MTF":
        context.user_data["request_type"] = REQUEST_TYPES["mtf_hrt"]
        await update.message.reply_text(
            MTF_HRT_MESSAGE,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        )
        return BotState.MEDICAL_MTF_HRT
    await update.message.reply_text(
        "Пожалуйста, выберите одну из опций.",
        reply_markup=ReplyKeyboardMarkup(MEDICAL_GENDER_THERAPY_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True),
    )
    return BotState.MEDICAL_GENDER_THERAPY_MENU

async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(MEDICAL_GENDER_THERAPY_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            GENDER_THERAPY_PROMPT,
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_GENDER_THERAPY_MENU
    return await medical_menu(update, context)

async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(MEDICAL_GENDER_THERAPY_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            GENDER_THERAPY_PROMPT,
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_GENDER_THERAPY_MENU
    return await medical_menu(update, context)

async def medical_surgery_planning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup([["🗣️ Медицинская консультация"], ["💉HRT"], ["❓ F64"], ["⚕️ Операции"], ["⏰ Напоминания"], [BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Вы вернулись в медицинское меню.",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_MENU
    return await medical_menu(update, context)
