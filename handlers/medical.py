from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import TelegramError
import os
from telegram.helpers import escape_markdown
from bot_responses import (
    CONSULTATION_PROMPT, GENDER_THERAPY_MESSAGE, MASCULINIZING_HRT_INFO, FEMINIZING_HRT_INFO,
    DIY_HRT_WARNING, F64_MESSAGE, SURGERY_INFO_MESSAGE, FTM_SURGERY_INFO, MTF_SURGERY_INFO
)
from keyboards import MEDICAL_MENU_BUTTONS, SURGERY_INFO_KEYBOARD, BACK_BUTTON, HELP_MENU_BUTTONS, GENDER_THERAPY_CHOICE_KEYBOARD, GENDER_CHOICE_KEYBOARD, FTM_SURGERY_CHOICE_KEYBOARD, MTF_SURGERY_CHOICE_KEYBOARD, BUDGET_CHOICE_KEYBOARD
from utils.constants import BotState, REQUEST_TYPES
from utils.message_utils import check_rate_limit
import logging

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
        elif choice == "plan_surgery":
    await query.message.edit_text(
        "Какое направление вас интересует?",
        reply_markup=GENDER_CHOICE_KEYBOARD,
        parse_mode="MarkdownV2"
    )
    return BotState.SURGERY_START
    async def surgery_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    gender = query.data.split("_")[-1]
    context.user_data["surgery_gender"] = gender
    if gender == "ftm":
        await query.message.edit_text(
            "Какие операции вас интересуют?",
            reply_markup=FTM_SURGERY_CHOICE_KEYBOARD,
            parse_mode="MarkdownV2"
        )
        return BotState.SURGERY_CHOICE
    elif gender == "mtf":
        await query.message.edit_text(
            "Какие операции вас интересуют?",
            reply_markup=MTF_SURGERY_CHOICE_KEYBOARD,
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

    if choice == "back_to_surgery_start":
        await query.message.edit_text(
            "Какое направление вас интересует?",
            reply_markup=GENDER_CHOICE_KEYBOARD,
            parse_mode="MarkdownV2"
        )
        return BotState.SURGERY_START

    if gender == "ftm" and choice == "ftm_surgery_next_budget":
        selected_surgeries = [cb.data.split("_")[-1] for cb in query.message.reply_markup.inline_keyboard[:-2]] # Get all surgery options
        context.user_data["selected_surgeries"] = context.user_data.get("selected_surgeries", []) + [s for s in selected_surgeries if s.startswith("ftm_surgery_")]
        await query.message.edit_text(
            "Какой у вас бюджет?",
            reply_markup=BUDGET_CHOICE_KEYBOARD,
            parse_mode="MarkdownV2"
        )
        return BotState.SURGERY_BUDGET
    elif gender == "mtf" and choice == "mtf_surgery_next_budget":
        selected_surgeries = [cb.data.split("_")[-1] for cb in query.message.reply_markup.inline_keyboard[:-2]] # Get all surgery options
        context.user_data["selected_surgeries"] = context.user_data.get("selected_surgeries", []) + [s for s in selected_surgeries if s.startswith("mtf_surgery_")]
        await query.message.edit_text(
            "Какой у вас бюджет?",
            reply_markup=BUDGET_CHOICE_KEYBOARD,
            parse_mode="MarkdownV2"
        )
        return BotState.SURGERY_BUDGET

    # Обработка выбора конкретных операций (пока просто сохраняем)
    if "selected_surgeries" not in context.user_data:
        context.user_data["selected_surgeries"] = []
    if gender == "ftm" and choice.startswith("ftm_surgery_"):
        context.user_data["selected_surgeries"].append(choice.split("_")[-1])
    elif gender == "mtf" and choice.startswith("mtf_surgery_"):
        context.user_data["selected_surgeries"].append(choice.split("_")[-1])

    # You might want to provide visual feedback to the user about their selections
    # For simplicity, we'll proceed to the budget choice after the "Далее" button
    return BotState.SURGERY_CHOICE

async def surgery_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    budget = query.data.split("_")[-1]
    context.user_data["budget"] = budget
    gender = context.user_data.get("surgery_gender")
    selected_surgeries = context.user_data.get("selected_surgeries", [])

    # --- ЛОГИКА ПОДБОРА КЛИНИК ---
    suggested_clinics = []

    # Примерная логика (нужно будет доработать с реальными данными о клиниках)
    if gender == "ftm" and "top" in selected_surgeries and budget == "economy":
        suggested_clinics.append("Возможно, Urodoc Clinic")
    elif gender == "mtf" and "breast" in selected_surgeries and budget == "medium":
        suggested_clinics.append("Возможно, Kamol Hospital")
    elif budget == "premium":
        suggested_clinics.append("Возможно, Yanhee International Hospital")

    if suggested_clinics:
        response = "На основе ваших предпочтений, вот несколько возможных клиник:\n" + "\n".join(suggested_clinics)
    else:
        response = "К сожалению, на данный момент мы не можем предложить клиники, полностью соответствующие вашим критериям."

    response += "\n\nВы можете вернуться в главное меню."
    await query.message.edit_text(
        response,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад в главное меню", callback_data="back_to_main")]]) if query.message else None,
        parse_mode="MarkdownV2"
    )
    return BotState.SURGERY_RESULT # Или BotState.MAIN_MENU

async def surgery_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "back_to_main":
        await query.message.edit_text(
            escape_markdown("Вы вернулись в главное меню.", version=2),
            reply_markup=MAIN_MENU_BUTTONS,
            parse_mode="MarkdownV2"
        )
        return BotState.MAIN_MENU
    return ConversationHandler.END


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
