from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError
import os
from telegram.helpers import escape_markdown
from bot_responses import (
    CONSULTATION_PROMPT, GENDER_THERAPY_MESSAGE, MASCULINIZING_HRT_INFO, FEMINIZING_HRT_INFO,
    DIY_HRT_WARNING, F64_MESSAGE, SURGERY_INFO_MESSAGE, FTM_SURGERY_INFO, MTF_SURGERY_INFO
from keyboards import (
    MEDICAL_MENU_BUTTONS, SURGERY_INFO_KEYBOARD, BACK_BUTTON, HELP_MENU_BUTTONS,
    GENDER_THERAPY_CHOICE_KEYBOARD, GENDER_CHOICE_KEYBOARD, MAIN_MENU_BUTTONS
)
from utils.constants import BotState, REQUEST_TYPES
import logging

logger = logging.getLogger(__name__)

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            choice = query.data
            
            if choice == "back_to_help":
                await query.message.edit_text(
                    escape_markdown("Выберите категорию помощи:", version=2),
                    reply_markup=HELP_MENU_BUTTONS,
                    parse_mode="MarkdownV2"
                )
                return BotState.HELP_MENU
            
            elif choice == "medical_consult":
                context.user_data["request_type"] = REQUEST_TYPES["medical_consult"]
                await context.bot.send_message(
                    chat_id=query.message.chat_id, 
                    text=CONSULTATION_PROMPT, 
                    parse_mode="MarkdownV2", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical")]])
                )
                return BotState.TYPING
            
            elif choice == "medical_hrt":
                await query.message.edit_text(
                    GENDER_THERAPY_MESSAGE,
                    parse_mode="MarkdownV2",
                    reply_markup=GENDER_THERAPY_CHOICE_KEYBOARD
                )
                return BotState.MEDICAL_GENDER_THERAPY_INLINE
            
            elif choice == "medical_f64":
                await query.message.edit_text(
                    F64_MESSAGE,
                    parse_mode="MarkdownV2",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical")]])
                )
                return BotState.MEDICAL_MENU
            
            elif choice == "medical_surgery":
                await query.message.edit_text(
                    SURGERY_INFO_MESSAGE,
                    parse_mode="MarkdownV2",
                    reply_markup=SURGERY_INFO_KEYBOARD
                )
                return BotState.MEDICAL_SURGERY_PLANNING

        return BotState.MEDICAL_MENU

    except Exception as e:
        logger.error(f"Error in medical_menu: {e}", exc_info=True)
        if update.callback_query:
            await update.callback_query.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже.",
                parse_mode="MarkdownV2"
            )
        return BotState.MAIN_MENU

async def handle_gender_therapy_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        query = update.callback_query
        await query.answer()
        choice = query.data

        if choice == "hrt_t":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("DIY", callback_data="diy_ftm"),
                 InlineKeyboardButton("Запросить консультацию", callback_data="consult_ftm")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]
            ])
            await query.message.edit_text(
                MASCULINIZING_HRT_INFO,
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )
            return BotState.MEDICAL_FTM_HRT
        
        elif choice == "hrt_e":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("DIY", callback_data="diy_mtf"),
                 InlineKeyboardButton("Запросить консультацию", callback_data="consult_mtf")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]
            ])
            await query.message.edit_text(
                FEMINIZING_HRT_INFO,
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )
            return BotState.MEDICAL_MTF_HRT
        
        elif choice == "back_to_medical":
            await query.message.edit_text(
                escape_markdown("Выберите категорию медицинской помощи:", version=2),
                reply_markup=MEDICAL_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MEDICAL_MENU

        return BotState.MEDICAL_GENDER_THERAPY_INLINE

    except Exception as e:
        logger.error(f"Error in handle_gender_therapy_choice: {e}", exc_info=True)
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_MENU

async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data == "back_to_medical_inline":
                await query.message.edit_text(
                    GENDER_THERAPY_MESSAGE,
                    parse_mode="MarkdownV2",
                    reply_markup=GENDER_THERAPY_CHOICE_KEYBOARD
                )
                return BotState.MEDICAL_GENDER_THERAPY_INLINE
            
            elif query.data == "diy_ftm":
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Я понимаю риски, скачать гайд", callback_data="guide_ftm")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]
                ])
                await query.message.edit_text(
                    DIY_HRT_WARNING,
                    parse_mode="MarkdownV2",
                    reply_markup=keyboard
                )
                return BotState.MEDICAL_FTM_HRT
            
            elif query.data == "consult_ftm":
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=CONSULTATION_PROMPT,
                    parse_mode="MarkdownV2",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]])
                )
                context.user_data["request_type"] = REQUEST_TYPES["ftm_hrt"]
                return BotState.TYPING
            
            elif query.data == "guide_ftm":
                return await send_hrt_guide(update, context, "ftm")

        return BotState.MEDICAL_FTM_HRT

    except Exception as e:
        logger.error(f"Error in medical_ftm_hrt: {e}", exc_info=True)
        await update.callback_query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_MENU

async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data == "back_to_medical_inline":
                await query.message.edit_text(
                    GENDER_THERAPY_MESSAGE,
                    parse_mode="MarkdownV2",
                    reply_markup=GENDER_THERAPY_CHOICE_KEYBOARD
                )
                return BotState.MEDICAL_GENDER_THERAPY_INLINE
            
            elif query.data == "diy_mtf":
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Я понимаю риски, скачать гайд", callback_data="guide_mtf")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]
                ])
                await query.message.edit_text(
                    DIY_HRT_WARNING,
                    parse_mode="MarkdownV2",
                    reply_markup=keyboard
                )
                return BotState.MEDICAL_MTF_HRT
            
            elif query.data == "consult_mtf":
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=CONSULTATION_PROMPT,
                    parse_mode="MarkdownV2",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]])
                )
                context.user_data["request_type"] = REQUEST_TYPES["mtf_hrt"]
                return BotState.TYPING
            
            elif query.data == "guide_mtf":
                return await send_hrt_guide(update, context, "mtf")

        return BotState.MEDICAL_MTF_HRT

    except Exception as e:
        logger.error(f"Error in medical_mtf_hrt: {e}", exc_info=True)
        await update.callback_query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_MENU

async def send_hrt_guide(update: Update, context: ContextTypes.DEFAULT_TYPE, guide_type: str) -> int:
    try:
        guide_path = os.getenv("DIY_HRT_GUIDE_PATH")
        if not guide_path:
            await update.callback_query.message.reply_text(
                escape_markdown("Путь к файлу гайда не настроен.", version=2),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ", 
                                       callback_data=f"consult_{'ftm' if guide_type == 'ftm' else 'mtf'}"),
                    InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")
                ]]),
                parse_mode="MarkdownV2"
            )
            return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT

        with open(guide_path, "rb") as pdf_file:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=pdf_file,
                filename="diyHRTguide.pdf",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ", 
                                       callback_data=f"consult_{'ftm' if guide_type == 'ftm' else 'mtf'}"),
                    InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")
                ]])
            )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT

    except FileNotFoundError:
        await update.callback_query.message.reply_text(
            escape_markdown("Файл гайда не найден.", version=2),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ", 
                                   callback_data=f"consult_{'ftm' if guide_type == 'ftm' else 'mtf'}"),
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")
            ]]),
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT

    except TelegramError as e:
        await update.callback_query.message.reply_text(
            escape_markdown(f"Произошла ошибка при отправке файла: {str(e)}", version=2),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ", 
                                   callback_data=f"consult_{'ftm' if guide_type == 'ftm' else 'mtf'}"),
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")
            ]]),
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT

