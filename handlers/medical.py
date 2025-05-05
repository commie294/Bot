from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import TelegramError
import os
from bot_responses import (
    CONSULTATION_PROMPT, GENDER_THERAPY_MESSAGE, MASCULINIZING_HRT_INFO, FEMINIZING_HRT_INFO,
    DIY_HRT_WARNING, F64_MESSAGE, SURGERY_INFO_MESSAGE, FTM_SURGERY_INFO, MTF_SURGERY_INFO
)
from keyboards import MEDICAL_MENU_BUTTONS, GENDER_THERAPY_CHOICE_BUTTONS, SURGERY_INFO_KEYBOARD, BACK_BUTTON
from utils.constants import BotState, REQUEST_TYPES

elif choice == "🩺 Медицинская помощь":
    keyboard = ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
    await update.message.reply_text(
        "Выберите категорию медицинской помощи:",
        reply_markup=keyboard,
    )
    return BotState.MEDICAL_MENU

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор в меню медицинской помощи."""
    choice = update.message.text
    if choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Выберите категорию помощи:",
            reply_markup=keyboard,
        )
        return BotState.HELP_MENU
    elif choice == "🗣️ Медицинская консультация":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = REQUEST_TYPES["medical_consult"]
        return BotState.TYPING
    elif choice == "💉HRT":
        keyboard = ReplyKeyboardMarkup(
            GENDER_THERAPY_CHOICE_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            GENDER_THERAPY_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_GENDER_THERAPY_MENU
    elif choice == "❓ F64":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            F64_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_MENU
    elif choice == "⚕️ Операции":
        await update.message.reply_text(
            SURGERY_INFO_MESSAGE,
            parse_mode="Markdown",
            reply_markup=SURGERY_INFO_KEYBOARD,
        )
        return BotState.MEDICAL_SURGERY_PLANNING
    await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
    return BotState.MEDICAL_MENU

async def medical_gender_therapy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор направления гормональной терапии."""
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_menu(update, context)
    elif choice == "T":
        keyboard = ReplyKeyboardMarkup(
            [["DIY"], ["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            MASCULINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_FTM_HRT
    elif choice == "E":
        keyboard = ReplyKeyboardMarkup(
            [["DIY"], ["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            FEMINIZING_HRT_INFO,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_MTF_HRT
    await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
    return BotState.MEDICAL_GENDER_THERAPY_MENU

async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает запросы по мужской ГТ."""
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_gender_therapy_menu(update, context)
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            DIY_HRT_WARNING, parse_mode="Markdown", reply_markup=keyboard
        )
        return BotState.MEDICAL_FTM_HRT
    elif choice == "Запросить консультацию по мужской ГТ":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = REQUEST_TYPES["ftm_hrt"]
        return BotState.TYPING
    elif choice == "Я понимаю риски, скачать гайд":
        return await send_hrt_guide(update, context, "ftm")
    await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
    return BotState.MEDICAL_FTM_HRT

async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает запросы по женской ГТ."""
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_gender_therapy_menu(update, context)
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор в меню медицинской помощи."""
    choice = update.message.text
    if choice == BACK_BUTTON:
        keyboard = ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Выберите категорию помощи:",
            reply_markup=keyboard,
        )
        return BotState.HELP_MENU
    elif choice == "🩺 Медицинская помощь":
        keyboard = ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            "Выберите категорию медицинской помощи:",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_MENU
    elif choice == "🗣️ Медицинская консультация":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = REQUEST_TYPES["medical_consult"]
        return BotState.TYPING
    elif choice == "💉HRT":
        keyboard = ReplyKeyboardMarkup(
            GENDER_THERAPY_CHOICE_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            GENDER_THERAPY_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_GENDER_THERAPY_MENU
    elif choice == "❓ F64":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            F64_MESSAGE,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return BotState.MEDICAL_MENU
    elif choice == "⚕️ Операции":
        await update.message.reply_text(
            SURGERY_INFO_MESSAGE,
            parse_mode="Markdown",
            reply_markup=SURGERY_INFO_KEYBOARD,
        )
        return BotState.MEDICAL_SURGERY_PLANNING
    await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
    return BotState.MEDICAL_MENU
