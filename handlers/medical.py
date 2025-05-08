from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError
import os
from telegram.helpers import escape_markdown
from bot_responses import (
    CONSULTATION_PROMPT, GENDER_THERAPY_MESSAGE, MASCULINIZING_HRT_INFO, FEMINIZING_HRT_INFO,
    DIY_HRT_WARNING, F64_MESSAGE, SURGERY_INFO_MESSAGE, FTM_SURGERY_INFO, MTF_SURGERY_INFO
)
from keyboards import MEDICAL_MENU_BUTTONS, GENDER_THERAPY_CHOICE_BUTTONS, SURGERY_INFO_KEYBOARD, BACK_BUTTON, HELP_MENU_BUTTONS
from utils.constants import BotState, REQUEST_TYPES
from utils.message_utils import check_rate_limit
import logging

logger = logging.getLogger(__name__)

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_rate_limit(update, context):
        return BotState.MEDICAL_MENU
    choice = update.message.text
    if choice == BACK_BUTTON:
        keyboard = HELP_MENU_BUTTONS
        await update.message.reply_text(
            escape_markdown("Выберите категорию помощи:", version=2),
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.HELP_MENU
    elif choice == "🩺 Медицинская помощь":
        keyboard = ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            escape_markdown("Выберите категорию медицинской помощи:", version=2),
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_MENU
    elif choice == "🗣️ Медицинская консультация":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        context.user_data["request_type"] = REQUEST_TYPES["medical_consult"]
        return BotState.TYPING
    elif choice == "💉HRT":
        keyboard = ReplyKeyboardMarkup(
            GENDER_THERAPY_CHOICE_BUTTONS + [[BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            GENDER_THERAPY_MESSAGE,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        return BotState.MEDICAL_GENDER_THERAPY_MENU
    elif choice == "❓ F64":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            F64_MESSAGE,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        return BotState.MEDICAL_MENU
    elif choice == "⚕️ Операции":
        await update.message.reply_text(
            SURGERY_INFO_MESSAGE,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=SURGERY_INFO_KEYBOARD
        )
        return BotState.MEDICAL_SURGERY_PLANNING
    await update.message.reply_text(
        escape_markdown("Пожалуйста, выберите опцию из меню.", version=2),
        parse_mode="MarkdownV2"
    )
    return BotState.MEDICAL_MENU

async def medical_gender_therapy_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if not await check_rate_limit(update, context):
        return BotState.MEDICAL_GENDER_THERAPY_MENU
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
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        return BotState.MEDICAL_FTM_HRT
    elif choice == "E":
        keyboard = ReplyKeyboardMarkup(
            [["DIY"], ["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            FEMINIZING_HRT_INFO,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        return BotState.MEDICAL_MTF_HRT
    await update.message.reply_text(
        escape_markdown("Пожалуйста, выберите опцию из меню.", version=2),
        parse_mode="MarkdownV2"
    )
    return BotState.MEDICAL_GENDER_THERAPY_MENU

async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_rate_limit(update, context):
        return BotState.MEDICAL_FTM_HRT
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_gender_therapy_menu(update, context)
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            DIY_HRT_WARNING,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        return BotState.MEDICAL_FTM_HRT
    elif choice == "Запросить консультацию по мужской ГТ":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        context.user_data["request_type"] = REQUEST_TYPES["ftm_hrt"]
        return BotState.TYPING
    elif choice == "Я понимаю риски, скачать гайд":
        return await send_hrt_guide(update, context, "ftm")
    await update.message.reply_text(
        escape_markdown("Пожалуйста, выберите опцию из меню.", version=2),
        parse_mode="MarkdownV2"
    )
    return BotState.MEDICAL_FTM_HRT

async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_rate_limit(update, context):
        return BotState.MEDICAL_MTF_HRT
    choice = update.message.text
    if choice == BACK_BUTTON:
        return await medical_gender_therapy_menu(update, context)
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            DIY_HRT_WARNING,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        return BotState.MEDICAL_MTF_HRT
    elif choice == "Запросить консультацию по женской ГТ":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="MarkdownV2",  # Меняем на MarkdownV2
            reply_markup=keyboard
        )
        context.user_data["request_type"] = REQUEST_TYPES["mtf_hrt"]
        return BotState.TYPING
    elif choice == "Я понимаю риски, скачать гайд":
        return await send_hrt_guide(update, context, "mtf")
    await update.message.reply_text(
        escape_markdown("Пожалуйста, выберите опцию из меню.", version=2),
        parse_mode="MarkdownV2"
    )
    return BotState.MEDICAL_MTF_HRT

async def send_hrt_guide(
    update: Update, context: ContextTypes.DEFAULT_TYPE, guide_type: str
) -> int:
    guide_path = os.getenv("DIY_HRT_GUIDE_PATH")
    if not guide_path:
        keyboard = ReplyKeyboardMarkup(
            [[f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ"], [BACK_BUTTON]],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            escape_markdown("Путь к файлу гайда не настроен.", version=2),
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT
    try:
        with open(guide_path, "rb") as pdf_file:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=pdf_file,
                filename="diyHRTguide.pdf",
            )
        keyboard = ReplyKeyboardMarkup(
            [[f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ"], [BACK_BUTTON]],
            resize_keyboard=True,
        )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT
    except FileNotFoundError:
        keyboard = ReplyKeyboardMarkup(
            [[f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ"], [BACK_BUTTON]],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            escape_markdown("Файл гайда не найден.", version=2),
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT
    except TelegramError as e:
        keyboard = ReplyKeyboardMarkup(
            [[f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ"], [BACK_BUTTON]],
            resize_keyboard=True,
        )
        await update.message.reply_text(
            escape_markdown(f"Произошла ошибка при отправке файла: {str(e)}", version=2),
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT

async def medical_surgery_planning(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if not await check_rate_limit(update, context):
        return BotState.MEDICAL_SURGERY_PLANNING
    choice = update.message.text
    keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
    if choice == BACK_BUTTON:
        return await medical_menu(update, context)
    elif choice == "ФТМ Операции":
        await update.message.reply_text(
            FTM_SURGERY_INFO,
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_SURGERY_PLANNING
    elif choice == "МТФ Операции":
        await update.message.reply_text(
            MTF_SURGERY_INFO,
            reply_markup=keyboard,
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_SURGERY_PLANNING
    await update.message.reply_text(
        escape_markdown("Пожалуйста, выберите опцию из меню.", version=2),
        parse_mode="MarkdownV2"
    )
    return BotState.MEDICAL_SURGERY_PLANNING
