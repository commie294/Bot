from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError
import os
from telegram.helpers import escape_markdown
from bot_responses import (
    CONSULTATION_PROMPT, GENDER_THERAPY_MESSAGE, MASCULINIZING_HRT_INFO, FEMINIZING_HRT_INFO,
    DIY_HRT_WARNING, F64_MESSAGE, SURGERY_INFO_MESSAGE, FTM_SURGERY_INFO, MTF_SURGERY_INFO,
    SURGERY_BUDGET_CLINICS_INTRO, SURGERY_BUDGET_CLINIC_FORMAT, SURGERY_BUDGET_CLINIC_DETAILS_FORMAT,
    SURGERY_BUDGET_DISCLAIMER, SURGERY_BUDGET_NO_CLINICS, SURGERY_BUDGET_BACK_TO_MAIN
)
from keyboards import MEDICAL_MENU_BUTTONS, SURGERY_INFO_KEYBOARD, BACK_BUTTON, HELP_MENU_BUTTONS, GENDER_THERAPY_CHOICE_KEYBOARD, GENDER_CHOICE_KEYBOARD, FTM_SURGERY_CHOICE_KEYBOARD, MTF_SURGERY_CHOICE_KEYBOARD, BUDGET_CHOICE_KEYBOARD, MAIN_MENU_BUTTONS
from utils.constants import BotState, REQUEST_TYPES
from utils.message_utils import check_rate_limit
import logging
from data.clinics import CLINICS_DATA

logger = logging.getLogger(__name__)

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            await context.bot.send_message(chat_id=query.message.chat_id, text=CONSULTATION_PROMPT, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical")]])
            )
            return BotState.TYPING
        elif choice == "medical_hrt":
            keyboard = GENDER_THERAPY_CHOICE_KEYBOARD
            await query.message.edit_text(
                GENDER_THERAPY_MESSAGE,
                parse_mode="MarkdownV2",
                reply_markup=keyboard
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

async def handle_gender_therapy_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    choice = query.data
    if choice == "hrt_t":
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("DIY", callback_data="diy_ftm"),
              InlineKeyboardButton("Запросить консультацию", callback_data="consult_ftm")],
             [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]]
        )
        await query.message.edit_text(
            MASCULINIZING_HRT_INFO,
            parse_mode="MarkdownV2",
            reply_markup=keyboard
        )
        return BotState.MEDICAL_FTM_HRT
    elif choice == "hrt_e":
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("DIY", callback_data="diy_mtf"),
              InlineKeyboardButton("Запросить консультацию", callback_data="consult_mtf")],
             [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]]
        )
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

async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Я понимаю риски, скачать гайд", callback_data="guide_ftm")],
                 [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]]
            )
            await query.message.edit_text(
                DIY_HRT_WARNING,
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )
            return BotState.MEDICAL_FTM_HRT
        elif query.data == "consult_ftm":
            await context.bot.send_message(chat_id=query.message.chat_id, text=CONSULTATION_PROMPT, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]])
            )
            context.user_data["request_type"] = REQUEST_TYPES["ftm_hrt"]
            return BotState.TYPING
        elif query.data == "guide_ftm":
            return await send_hrt_guide(update, context, "ftm")
    return BotState.MEDICAL_FTM_HRT

async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Я понимаю риски, скачать гайд", callback_data="guide_mtf")],
                 [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]]
            )
            await query.message.edit_text(
                DIY_HRT_WARNING,
                parse_mode="MarkdownV2",
                reply_markup=keyboard
            )
            return BotState.MEDICAL_MTF_HRT
        elif query.data == "consult_mtf":
            await context.bot.send_message(chat_id=query.message.chat_id, text=CONSULTATION_PROMPT, parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")]])
            )
            context.user_data["request_type"] = REQUEST_TYPES["mtf_hrt"]
            return BotState.TYPING
        elif query.data == "guide_mtf":
            return await send_hrt_guide(update, context, "mtf")
    return BotState.MEDICAL_MTF_HRT

async def send_hrt_guide(
    update: Update, context: ContextTypes.DEFAULT_TYPE, guide_type: str
) -> int:
    guide_path = os.getenv("DIY_HRT_GUIDE_PATH")
    if not guide_path:
        await update.callback_query.message.reply_text(
            escape_markdown("Путь к файлу гайда не настроен.", version=2),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ", callback_data=f"consult_{'ftm' if guide_type == 'ftm' else 'mtf'}"),
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")
            ]]),
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT
    try:
        with open(guide_path, "rb") as pdf_file:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=pdf_file,
                filename="diyHRTguide.pdf",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ", callback_data=f"consult_{'ftm' if guide_type == 'ftm' else 'mtf'}"),
                    InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")
                ]])
            )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT
    except FileNotFoundError:
        await update.callback_query.message.reply_text(
            escape_markdown("Файл гайда не найден.", version=2),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ", callback_data=f"consult_{'ftm' if guide_type == 'ftm' else 'mtf'}"),
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")
            ]]),
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT
    except TelegramError as e:
        await update.callback_query.message.reply_text(
            escape_markdown(f"Произошла ошибка при отправке файла: {str(e)}", version=2),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"Запросить консультацию по {'мужской' if guide_type == 'ftm' else 'женской'} ГТ", callback_data=f"consult_{'ftm' if guide_type == 'ftm' else 'mtf'}"),
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical_inline")
            ]]),
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_FTM_HRT if guide_type == "ftm" else BotState.MEDICAL_MTF_HRT

async def medical_surgery_planning(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "back_to_medical":
            await query.message.edit_text(
                escape_markdown("Выберите категорию медицинской помощи:", version=2),
                reply_markup=MEDICAL_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MEDICAL_MENU
        elif query.data == "plan_surgery":
            await query.message.edit_text(
                "Какое направление вас интересует?",
                reply_markup=GENDER_CHOICE_KEYBOARD,
                parse_mode="MarkdownV2"
            )
            return BotState.SURGERY_START
        elif query.data == "ftm_surgery":
            await query.message.edit_text(
                FTM_SURGERY_INFO,
                parse_mode="MarkdownV2",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical")]])
            )
            return BotState.MEDICAL_SURGERY_PLANNING
        elif query.data == "mtf_surgery":
            await query.message.edit_text(
                MTF_SURGERY_INFO,
                parse_mode="MarkdownV2",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical")]])
            )
            return BotState.MEDICAL_SURGERY_PLANNING
    return BotState.MEDICAL_SURGERY_PLANNING

async def surgery_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    gender = query.data.split("_")[-1]
    context.user_data["surgery_gender"] = gender
    if gender == "ftm":
        await query.message.edit_text(
            "Какие операции вас интересуют?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Топэктомия/Мастэктомия", callback_data="ftm_surgery_top")],
                [InlineKeyboardButton("Гистерэктомия", callback_data="ftm_surgery_hysterectomy")],
                [InlineKeyboardButton("Овариэктомия", callback_data="ftm_surgery_oophorectomy")],
                [InlineKeyboardButton("Фаллопластика", callback_data="ftm_surgery_phalloplasty")],
                [InlineKeyboardButton("Метоидиопластика", callback_data="ftm_surgery_metoidioplasty")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_surgery_start")],
                [InlineKeyboardButton("Далее", callback_data="ftm_surgery_next_budget")]
            ]),
            parse_mode="MarkdownV2"
        )
        return BotState.SURGERY_CHOICE
    elif gender == "mtf":
        await query.message.edit_text(
            "Какие операции вас интересуют?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Вагинопластика", callback_data="mtf_surgery_vaginoplasty")],
                [InlineKeyboardButton("Увеличение груди", callback_data="mtf_surgery_breast")],
                [InlineKeyboardButton("Феминизирующая хирургия лица (FFS)", callback_data="mtf_surgery_ffs")],
                [InlineKeyboardButton("Орхиэктомия", callback_data="mtf_surgery_orchiectomy")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_surgery_start")],
                [InlineKeyboardButton("Далее", callback_data="mtf_surgery_next_budget")]
            ]),
            parse_mode="MarkdownV2"
        )
        return BotState.SURGERY_CHOICE
    elif query.data == "back_to_medical":
        await query.message.edit_text(
            escape_markdown("Выберите категорию медицинской помощи:", version=2),
            reply_markup=MEDICAL_MENU_BUTTONS,
            parse_mode="MarkdownV2"
        )
        return BotState.MEDICAL_MENU
    return BotState.SURGERY_START

async def surgery_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    choice = query.data
    gender = context.user_data.get("surgery_gender")

    logger.info(f"surgery_choice: choice={choice}, gender={gender}")

    if choice == "back_to_surgery_start":
        await query.message.edit_text(
            "Какое направление вас интересует?",
            reply_markup=GENDER_CHOICE_KEYBOARD,
            parse_mode="MarkdownV2"
        )
        return BotState.SURGERY_START

    if gender == "ftm" and choice == "ftm_surgery_next_budget":
        selected_surgeries = [cb.data.split("_")[-1] for row in query
