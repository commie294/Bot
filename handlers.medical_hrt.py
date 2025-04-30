import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from bot_responses import DIY_HRT_WARNING, CONSULTATION_PROMPT, DIY_HRT_GUIDE_NAME
from keyboards import BACK_BUTTON
import os

logger = logging.getLogger(__name__)
DIY_HRT_GUIDE_PATH = os.getenv("DIY_HRT_GUIDE_PATH")

async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return 12  # MEDICAL_GENDER_THERAPY_MENU
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            DIY_HRT_WARNING, parse_mode="Markdown", reply_markup=keyboard
        )
        return 13  # MEDICAL_FTM_HRT
    elif choice == "Запросить консультацию по мужской ГТ":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = "Помощь - Консультация по мужской ГТ"
        return 3  # TYPING
    elif choice == "Я понимаю риски, скачать гайд":
        if DIY_HRT_GUIDE_PATH:
            try:
                with open(DIY_HRT_GUIDE_PATH, 'rb') as pdf_file:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=pdf_file,
                        filename=DIY_HRT_GUIDE_NAME,
                    )
                    keyboard = ReplyKeyboardMarkup(
                        [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
                        resize_keyboard=True,
                    )
                    return 13  # MEDICAL_FTM_HRT
            except FileNotFoundError:
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text("Файл гайда не найден.", reply_markup=keyboard)
                return 13  # MEDICAL_FTM_HRT
            except TelegramError as e:
                logger.error(f"Ошибка Telegram API при отправке файла: {e}", exc_info=True)
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text(f"Произошла ошибка при отправке файла: {e}", reply_markup=keyboard)
                return 13  # MEDICAL_FTM_HRT
            else:
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text("Путь к файлу гайда не настроен.", reply_markup=keyboard)
                return 13  # MEDICAL_FTM_HRT
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return 13  # MEDICAL_FTM_HRT

async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == BACK_BUTTON:
        return 12  # MEDICAL_GENDER_THERAPY_MENU
    elif choice == "DIY":
        keyboard = ReplyKeyboardMarkup(
            [["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True
        )
        await update.message.reply_text(
            DIY_HRT_WARNING, parse_mode="Markdown", reply_markup=keyboard
        )
        return 14  # MEDICAL_MTF_HRT
    elif choice == "Запросить консультацию по женской ГТ":
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text(
            CONSULTATION_PROMPT,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        context.user_data["request_type"] = "Помощь - Консультация по женской ГТ"
        return 3  # TYPING
    elif choice == "Я понимаю риски, скачать гайд":
        if DIY_HRT_GUIDE_PATH:
            try:
                with open(DIY_HRT_GUIDE_PATH, 'rb') as pdf_file:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=pdf_file,
                        filename=DIY_HRT_GUIDE_NAME,
                    )
                    keyboard = ReplyKeyboardMarkup(
                        [["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
                        resize_keyboard=True,
                    )
                    return 14  # MEDICAL_MTF_HRT
            except FileNotFoundError:
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text("Файл гайда не найден.", reply_markup=keyboard)
                return 14  # MEDICAL_MTF_HRT
            except TelegramError as e:
                logger.error(f"Ошибка Telegram API при отправке файла: {e}", exc_info=True)
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text(f"Произошла ошибка при отправке файла: {e}", reply_markup=keyboard)
                return 14  # MEDICAL_MTF_HRT
            else:
                keyboard = ReplyKeyboardMarkup(
                    [["Запросить консультацию по женской ГТ"], [BACK_BUTTON]],
                    resize_keyboard=True,
                )
                await update.message.reply_text("Путь к файлу гайда не настроен.", reply_markup=keyboard)
                return 14  # MEDICAL_MTF_HRT
    else:
        await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
        return 14  # MEDICAL_MTF_HRT
