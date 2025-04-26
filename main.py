# -*- coding: utf-8 -*-
import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters as Filters,
    ContextTypes,
    ConversationHandler,
)
import sys
sys.path.append('/data/data/com.termux/files/usr/lib/python3.12/site-packages')

# Импорт констант и ответов из отдельных файлов
from bot_responses import (
    START_MESSAGE,
    HELP_MENU_MESSAGE,
    RESOURCE_PROMPT_MESSAGE,
    VOLUNTEER_MESSAGE,
    DONATE_MESSAGE,
    EMERGENCY_MESSAGE,
    HOUSING_FINANCE_PROMPT,
    PSYCHOLOGICAL_HELP_PROMPT,
    CONSULTATION_PROMPT,
    MESSAGE_SENT_SUCCESS,
    MESSAGE_SEND_ERROR,
    CANCEL_MESSAGE,
    BACK_TO_MAIN_MENU,
    CHOOSE_FROM_MENU,
    CHOOSE_HELP_CATEGORY,
    GENDER_THERAPY_MESSAGE,
    FEMINIZING_HRT_INFO,
    MASCULINIZING_HRT_INFO,
    DIY_HRT_WARNING,
    LGBT_FAMILIES_INFO,
    REPORT_ABUSE_MESSAGE,
    TRANS_FRIENDLY_ENDO_CONSULT_PROMPT,
    SURGERY_CONSULT_PROMPT,
    FTM_SURGERY_INFO,
    MTF_SURGERY_INFO,
    LEGAL_FAMILIES_CHOICE_MESSAGE,
    GENDER_THERAPY_CHOICE_MESSAGE,
    SURGERY_INFO_MESSAGE,
)
from keyboards import (
    BACK_BUTTON,
    MAIN_MENU_BUTTONS,
    HELP_MENU_BUTTONS,
    LEGAL_MENU_BUTTONS,
    LEGAL_FAMILIES_BUTTONS,
    GENDER_THERAPY_CHOICE_BUTTONS,
    MASCULINIZING_HRT_BUTTONS,
    FEMINIZING_HRT_BUTTONS,
    SURGERY_CHOICE_BUTTONS,
)
from faq_responses import FAQ_RESPONSES
from channels import CHANNELS

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Настройка логирования
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Состояния диалога
(
    START,
    MAIN_MENU,
    HELP_MENU,
    TYPING,
    FAQ_LEGAL,
    FAQ_MED,
    VOLUNTEER_START,
    VOLUNTEER_NAME,
    VOLUNTEER_REGION,
    VOLUNTEER_HELP_TYPE,
    VOLUNTEER_CONTACT,
    ANONYMOUS_MESSAGE,
    LEGAL_FAMILIES_MENU,
    LEGAL_DOCUMENTS_CONSULT,
    LEGAL_PROPAGANDA_CONSULT,
    LEGAL_CONSULT,
    LEGAL_REPORT_ABUSE,
    MEDICAL_MENU,
    MEDICAL_GENDER_THERAPY_MENU,
    MEDICAL_FTM_HRT,
    MEDICAL_MTF_HRT,
    MEDICAL_F64_CONSULT,
    MEDICAL_SURGERY_MENU,
    MEDICAL_SURGERY_FTM_CONSULT,
    MEDICAL_SURGERY_MTF_CONSULT,
    MEDICAL_ENDO_CONSULT,
    MEDICAL_SURGEON_CONSULT,
) = range(27)

async def volunteer_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        await update.message.reply_text("Давайте начнем небольшое интервью. Как вас зовут?")
        return VOLUNTEER_NAME
    except Exception as e:
        logger.error(f"Ошибка в volunteer_start: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}")
        return MAIN_MENU

async def volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["volunteer_name"] = update.message.text
        await update.message.reply_text("Из какого вы региона?")
        return VOLUNTEER_REGION
    except Exception as e:
        logger.error(f"Ошибка в volunteer_name: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}")
        return MAIN_MENU

async def volunteer_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["volunteer_region"] = update.message.text
        keyboard = ReplyKeyboardMarkup([
            ["Психологическая помощь"],
            ["Юридические услуги"],
            ["Медицинские услуги"],
            ["Информационные услуги (тексты, модерация)"],
            ["Финансовая поддержка"],
            ["Другое..."],
        ], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Какую помощь вы готовы предоставить?", reply_markup=keyboard)
        return VOLUNTEER_HELP_TYPE
    except Exception as e:
        logger.error(f"Ошибка в volunteer_region: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}")
        return MAIN_MENU

async def volunteer_help_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["volunteer_help_type"] = update.message.text
        await update.message.reply_text("Пожалуйста, укажите ваш Telegram-ник для связи.")
        return VOLUNTEER_CONTACT
    except Exception as e:
        logger.error(f"Ошибка в volunteer_help_type: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}")
        return MAIN_MENU

async def volunteer_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["volunteer_contact"] = update.message.text
        volunteer_info = (
            f"Новый потенциальный волонтер:\n"
            f"Имя: {context.user_data.get('volunteer_name', 'не указано')}\n"
            f"Регион: {context.user_data.get('volunteer_region', 'не указано')}\n"
            f"Направление: {context.user_data.get('volunteer_help_type', 'не указано')}\n"
            f"Контакт: @{context.user_data.get('volunteer_contact', 'не указано')}"
        )

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=volunteer_info)
        keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
        await update.message.reply_text("Спасибо! Ваша информация передана администраторам. Мы свяжемся с вами при необходимости.", reply_markup=keyboard)

        context.user_data.clear() # Очищаем данные интервью
        return MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в volunteer_contact: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}")
        return MAIN_MENU

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data.clear()
        await update.message.reply_text(START_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
        return MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в start: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return START

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "Попросить о помощи":
            await update.message.reply_text(HELP_MENU_MESSAGE, reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True))
            return HELP_MENU
        elif choice == "Предложить ресурс":
            await update.message.reply_text(RESOURCE_PROMPT_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Предложение ресурса"
            return TYPING
        elif choice == "Стать волонтером":
            return await volunteer_start(update, context) # Запускаем интервью
        elif choice == "Поддержать проект":
            await update.message.reply_text(DONATE_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), disable_web_page_preview=True, parse_mode="HTML")
            context.user_data["type"] = "Поддержка проекта"
            return TYPING
        elif choice == "Анонимное сообщение":
            await update.message.reply_text("Пожалуйста, напишите ваше анонимное сообщение:", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Анонимное сообщение"
            return TYPING
        else:
            await update.message.reply_text(CHOOSE_FROM_MENU)
            return MAIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в main_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MAIN_MENU

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "🆘 Срочная помощь":
            await update.message.reply_text(EMERGENCY_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True), disable_web_page_preview=True, parse_mode="HTML")
            context.user_data["type"] = "Срочная помощь"
            return TYPING
        elif choice == "💼 Юридическая помощь":
            await update.message.reply_text("Выберите раздел:", reply_markup=ReplyKeyboardMarkup(LEGAL_MENU_BUTTONS, resize_keyboard=True))
            return FAQ_LEGAL
        elif choice == "🏥 Медицинская помощь":
            await update.message.reply_text("Выберите раздел:", reply_markup=ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS, resize_keyboard=True))
            return MEDICAL_MENU
        elif choice == "🏠 Жилье/финансы":
            await update.message.reply_text(HOUSING_FINANCE_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Жилье/финансы"
            return TYPING
        elif choice == "🧠 Психологическая помощь":
            await update.message.reply_text(PSYCHOLOGICAL_HELP_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Психологическая помощь"
            return TYPING
        elif choice == BACK_BUTTON:
            return await main_menu(update, context)
        else:
            await update.message.reply_text(CHOOSE_FROM_MENU)
            return HELP_MENU
    except Exception as e:
        logger.error(f"Ошибка в help_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return HELP_MENU

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "ЛГБТ+ семьи":
            await update.message.reply_text(LGBT_FAMILIES_INFO, parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(LEGAL_FAMILIES_BUTTONS, resize_keyboard=True))
            return LEGAL_FAMILIES_MENU
        elif choice == "Как сменить документы":
            response = FAQ_RESPONSES.get(choice, "Информация отсутствует.")
            keyboard = ReplyKeyboardMarkup([["Запросить консультацию по смене документов"], [BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(response, parse_mode="HTML", reply_markup=keyboard)
            context.user_data["consultation_type"] = "смена документов"
            return TYPING
        elif choice == "Что такое пропаганда ЛГБТ?":
            response = FAQ_RESPONSES.get(choice, "Информация отсутствует.")
            keyboard = ReplyKeyboardMarkup([["Запросить консультацию по вопросам пропаганды"], [BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(response, parse_mode="HTML", reply_markup=keyboard)
            context.user_data["consultation_type"] = "вопросы пропаганды"
            return TYPING
        elif choice == "Консультация":
            await update.message.reply_text(CONSULTATION_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Юридическая консультация"
            return TYPING
        elif choice == "Сообщить о нарушении":
            await update.message.reply_text(REPORT_ABUSE_MESSAGE, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Сообщение о нарушении (юридическое)"
            return TYPING
        elif choice == BACK_BUTTON:
            return await help_menu(update, context)
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return FAQ_LEGAL
    except Exception as e:
        logger.error(f"Ошибка в faq_legal: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return FAQ_LEGAL

async def legal_families_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "ЛГБТ семьи":
            await update.message.reply_text(LGBT_FAMILIES_INFO, parse_mode="HTML", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            return LEGAL_FAMILIES_MENU
        elif choice == "Запросить консультацию по партнерским соглашениям":
            await update.message.reply_text(CONSULTATION_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Консультация по партнерским соглашениям"
            return TYPING
        elif choice == BACK_BUTTON:
            return await faq_legal(update, context)
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return LEGAL_FAMILIES_MENU
    except Exception as e:
        logger.error(f"Ошибка в legal_families_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return LEGAL_FAMILIES_MENU

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "ГТ":
            await update.message.reply_text(GENDER_THERAPY_MESSAGE, reply_markup=ReplyKeyboardMarkup(GENDER_THERAPY_CHOICE_BUTTONS, resize_keyboard=True))
            return MEDICAL_GENDER_THERAPY_MENU
        elif choice == "F64":
            response = FAQ_RESPONSES.get(choice, "Информация отсутствует.")
            keyboard = ReplyKeyboardMarkup([["Запросить консультацию по F64"], [BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(response, parse_mode="HTML", reply_markup=keyboard)
            context.user_data["consultation_type"] = "F64"
            return TYPING
        elif choice == "Операции":
            response = FAQ_RESPONSES.get("Где делают операции?", "Информация отсутствует.")
            keyboard = ReplyKeyboardMarkup(SURGERY_CHOICE_BUTTONS, resize_keyboard=True)
            await update.message.reply_text(response, parse_mode="HTML", reply_markup=keyboard)
            return MEDICAL_SURGERY_MENU
        elif choice == BACK_BUTTON:
            return await help_menu(update, context)
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return MEDICAL_MENU
    except Exception as e:
        logger.error(f"Ошибка в medical_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MEDICAL_MENU

async def medical_gender_therapy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "Мужская ГТ":
            await update.message.reply_text(MASCULINIZING_HRT_INFO, reply_markup=ReplyKeyboardMarkup([["DIY"], ["Консультация"], [BACK_BUTTON]], resize_keyboard=True))
            return MEDICAL_FTM_HRT
        elif choice == "Женская ГТ":
            await update.message.reply_text(FEMINIZING_HRT_INFO, reply_markup=ReplyKeyboardMarkup([["DIY"], ["Консультация"], [BACK_BUTTON]], resize_keyboard=True))
            return MEDICAL_MTF_HRT
        elif choice == BACK_BUTTON:
            return await medical_menu(update, context)
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return MEDICAL_GENDER_THERAPY_MENU
    except Exception as e:
        logger.error(f"Ошибка в medical_gender_therapy_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MEDICAL_GENDER_THERAPY_MENU

async def medical_ftm_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "DIY":
            await update.message.reply_text(DIY_HRT_WARNING, parse_mode="HTML", reply_markup=ReplyKeyboardMarkup([["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]], resize_keyboard=True))
            context.user_data["consultation_type"] = "мужская ГТ (DIY)"
            return TYPING
        elif choice == "Запросить консультацию по мужской ГТ" or choice == "Консультация":
            await update.message.reply_text(TRANS_FRIENDLY_ENDO_CONSULT_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Консультация по мужской ГТ"
            return TYPING
        elif choice == BACK_BUTTON:
            return await medical_gender_therapy_menu(update, context)
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return MEDICAL_FTM_HRT
    except Exception as e:
        logger.error(f"Ошибка в medical_ftm_hrt: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MEDICAL_FTM_HRT

async def medical_mtf_hrt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "DIY":
            await update.message.reply_text(DIY_HRT_WARNING, parse_mode="HTML", reply_markup=ReplyKeyboardMarkup([["Запросить консультацию по женской ГТ"], [BACK_BUTTON]], resize_keyboard=True))
            context.user_data["consultation_type"] = "женская ГТ (DIY)"
            return TYPING
        elif choice == "Запросить консультацию по женской ГТ" or choice == "Консультация":
            await update.message.reply_text(TRANS_FRIENDLY_ENDO_CONSULT_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Консультация по женской ГТ"
            return TYPING
        elif choice == BACK_BUTTON:
            return await medical_gender_therapy_menu(update, context)
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return MEDICAL_MTF_HRT
    except Exception as e:
        logger.error(f"Ошибка в medical_mtf_hrt: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MEDICAL_MTF_HRT

async def medical_surgery_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        choice = update.message.text
        if choice == "ФТМ Операции":
            await update.message.reply_text(FTM_SURGERY_INFO, reply_markup=ReplyKeyboardMarkup([["Запросить консультацию по ФТМ операциям"], [BACK_BUTTON]], resize_keyboard=True))
            context.user_data["consultation_type"] = "ФТМ операции"
            return TYPING
        elif choice == "МТФ Операции":
            await update.message.reply_text(MTF_SURGERY_INFO, reply_markup=ReplyKeyboardMarkup([["Запросить консультацию по МТФ операциям"], [BACK_BUTTON]], resize_keyboard=True))
            context.user_data["consultation_type"] = "МТФ операции"
            return TYPING
        elif choice == "Консультация хирурга":
            await update.message.reply_text(SURGERY_CONSULT_PROMPT, reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Консультация хирурга"
            return TYPING
        elif choice == BACK_BUTTON:
            return await medical_menu(update, context)
        else:
            await update.message.reply_text("Пожалуйста, выберите опцию из меню.")
            return MEDICAL_SURGERY_MENU
    except Exception as e:
        logger.error(f"Ошибка в medical_surgery_menu: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return MEDICAL_SURGERY_MENU

async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message_text = update.message.text
    if message_text == BACK_BUTTON:
        current_state = context.user_data.get("current_state")
        if current_state == FAQ_LEGAL:
            return await faq_legal(update, context)
        elif current_state == MEDICAL_MENU:
            return await medical_menu(update, context)
        elif current_state == LEGAL_FAMILIES_MENU:
            return await legal_families_menu(update, context)
        elif current_state == MEDICAL_GENDER_THERAPY_MENU:
            return await medical_gender_therapy_menu(update, context)
        elif current_state == MEDICAL_FTM_HRT:
            return await medical_ftm_hrt(update, context)
        elif current_state == MEDICAL_MTF_HRT:
            return await medical_mtf_hrt(update, context)
        elif current_state == MEDICAL_SURGERY_MENU:
            return await medical_surgery_menu(update, context)
        else:
            return await main_menu(update, context)

    request_type = context.user_data.get("type", "Сообщение")
    consultation_type = context.user_data.get("consultation_type")
    username = update.message.from_user.username or "нет"
    forward_text = f"📩 {request_type}"
    if consultation_type:
        forward_text += f" ({consultation_type})"
    forward_text += f"\nОт @{username}\n\n{message_text}"
    target_channel_id = ADMIN_CHAT_ID

    if "Срочная помощь" in request_type:
        target_channel_id = CHANNELS["Срочная"]
        admin_notification = f"🚨 НОВЫЙ СРОЧНЫЙ ЗАПРОС!\nОт пользователя: @{username}\nСообщение: {message_text}"
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_notification, parse_mode="HTML")
    elif "Анонимное сообщение" in request_type:
        target_channel_id = CHANNELS["Анонимные сообщения"]
        forward_text = f"🤫 Анонимное сообщение:\n\n{message_text}"
    elif "Предложение ресурса" in request_type:
        target_channel_id = CHANNELS["Предложение ресурса"]
    elif "Психологическая помощь" in request_type:
        target_channel_id = CHANNELS["Психологическая помощь"]
    elif "Жилье/финансы" in request_type:
        pass # Отправляется администратору по умолчанию
    elif "Консультация" in request_type or consultation_type:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=forward_text)
        await update.message.reply_text(MESSAGE_SENT_SUCCESS, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
        return MAIN_MENU
    elif "Сообщение о нарушении" in request_type:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=forward_text)
        await update.message.reply_text(MESSAGE_SENT_SUCCESS, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
        return MAIN_MENU
    else:
        await context.bot.send_message(chat_id=target_channel_id, text=forward_text)
        await update.message.reply_text(MESSAGE_SENT_SUCCESS, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
        return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
        return START
    except Exception as e:
        logger.error(f"Ошибка в cancel: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}", parse_mode="HTML")
        return START

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [CommandHandler("start", start)],
            MAIN_MENU: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, main_menu)],
            HELP_MENU: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, help_menu)],
            FAQ_LEGAL: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, faq_legal)],
            LEGAL_FAMILIES_MENU: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, legal_families_menu)],
            MEDICAL_MENU: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, medical_menu)],
            MEDICAL_GENDER_THERAPY_MENU: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, medical_gender_therapy_menu)],
            MEDICAL_FTM_HRT: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, medical_ftm_hrt)],
            MEDICAL_MTF_HRT: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, medical_mtf_hrt)],
            MEDICAL_SURGERY_MENU: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, medical_surgery_menu)],
            TYPING: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, handle_typing)],
            VOLUNTEER_START: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_start)],
            VOLUNTEER_NAME: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_name)],
            VOLUNTEER_REGION: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_region)],
            VOLUNTEER_HELP_TYPE: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_help_type)],
            VOLUNTEER_CONTACT: [MessageHandler(Filters.TEXT & ~Filters.COMMAND, volunteer_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    # Запуск бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
