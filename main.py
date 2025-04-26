from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes
import logging
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
    FTM_SURGERY_INFO,
    MTF_SURGERY_INFO,
    GENDER_THERAPY_CHOICE_MESSAGE,
    SURGERY_INFO_MESSAGE,
    DOCUMENTS_MESSAGE,
    PROPAGANDA_MESSAGE,
    F64_MESSAGE,
    DIY_HRT_GUIDE_LINK,
    DIY_HRT_GUIDE_NAME,
    SURGERY_PLANNING_PROMPT,
)
from keyboards import (
    MAIN_MENU_BUTTONS,
    HELP_MENU_BUTTONS,
    LEGAL_MENU_BUTTONS,
    MEDICAL_MENU_BUTTONS,
    GENDER_THERAPY_CHOICE_BUTTONS,
    SURGERY_CHOICE_BUTTONS,
    BACK_BUTTON,
)

# Включите логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем состояния разговора
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
    LEGAL_DOCUMENTS_CONSULT,
    LEGAL_PROPAGANDA_CONSULT,
    LEGAL_CONSULT,
    LEGAL_REPORT_ABUSE,
    MEDICAL_MENU,
    MEDICAL_GENDER_THERAPY_MENU,
    MEDICAL_FTM_HRT,
    MEDICAL_MTF_HRT,
    MEDICAL_SURGERY_MENU,
    MEDICAL_SURGERY_FTM_CONSULT,
    MEDICAL_SURGERY_MTF_CONSULT,
    MEDICAL_SURGEON_PLANNING,
) = range(24)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает разговор и выводит приветственное сообщение с главным меню."""
    await update.message.reply_text(START_MESSAGE, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор пользователя в главном меню."""
    user_choice = update.message.text
    if user_choice == "Попросить о помощи":
        await update.message.reply_text(HELP_MENU_MESSAGE, reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
        return HELP_MENU
    elif user_choice == "Предложить ресурс":
        await update.message.reply_text(RESOURCE_PROMPT_MESSAGE)
        context.user_data["type"] = "Предложение ресурса"
        return TYPING
    elif user_choice == "Стать волонтером":
        await update.message.reply_text(VOLUNTEER_MESSAGE)
        return await volunteer_start(update, context)
    elif user_choice == "Поддержать проект":
        await update.message.reply_text(DONATE_MESSAGE, parse_mode="Markdown", disable_web_page_preview=True)
        context.user_data["type"] = "Поддержка проекта"
        return TYPING
    elif user_choice == "Анонимное сообщение":
        await update.message.reply_text("Пожалуйста, напишите ваше анонимное сообщение:")
        context.user_data["type"] = "Анонимное сообщение"
        return TYPING
    else:
        await update.message.reply_text(CHOOSE_FROM_MENU)
        return MAIN_MENU

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор пользователя в меню помощи."""
    user_choice = update.message.text
    if user_choice == "🆘 Срочная помощь":
        await update.message.reply_text(EMERGENCY_MESSAGE, parse_mode="Markdown")
        context.user_data["type"] = "Срочная помощь"
        return TYPING
    elif user_choice == "💼 Юридическая помощь":
        await update.message.reply_text("Выберите интересующий вас юридический вопрос:", reply_markup=ReplyKeyboardMarkup(LEGAL_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
        return FAQ_LEGAL
    elif user_choice == "🏥 Медицинская помощь":
        await update.message.reply_text("Выберите интересующий вас медицинский вопрос:", reply_markup=ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS, resize_keyboard=True), parse_mode="Markdown")
        return MEDICAL_MENU
    elif user_choice == "🏠 Жилье/финансы":
        await update.message.reply_text(HOUSING_FINANCE_PROMPT)
        context.user_data["type"] = "Жилье/финансы"
        return TYPING
    elif user_choice == "🧠 Психологическая помощь":
        await update.message.reply_text(PSYCHOLOGICAL_HELP_PROMPT)
        context.user_data["type"] = "Психологическая помощь"
        return TYPING
    elif user_choice == BACK_BUTTON:
        await update.message.reply_text(BACK_TO_MAIN_MENU, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
        return MAIN_MENU
    else:
        await update.message.reply_text(CHOOSE_HELP_CATEGORY)
        return HELP_MENU

async def faq_legal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает вопросы в разделе юридической помощи."""
    try:
        choice = update.message.text
        if choice == "ЛГБТ+ семьи":
            await update.message.reply_text(LGBT_FAMILIES_INFO, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            return HELP_MENU
        elif choice == "Как сменить документы":
            response = DOCUMENTS_MESSAGE
            keyboard = ReplyKeyboardMarkup([["Запросить консультацию по смене документов"], [BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)
            context.user_data["consultation_type"] = "смена документов"
            return TYPING
        elif choice == "Что такое пропаганда ЛГБТ?":
            response = PROPAGANDA_MESSAGE
            keyboard = ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)
            return HELP_MENU
        elif choice == "Консультация":
            await update.message.reply_text(CONSULTATION_PROMPT, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Юридическая консультация"
            return TYPING
        elif choice == "Сообщить о нарушении":
            await update.message.reply_text(REPORT_ABUSE_MESSAGE, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
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

async def medical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор пользователя в медицинском меню."""
    try:
        choice = update.message.text
        if choice == "ГТ":
            await update.message.reply_text(GENDER_THERAPY_MESSAGE, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(GENDER_THERAPY_CHOICE_BUTTONS, resize_keyboard=True))
            return MEDICAL_GENDER_THERAPY_MENU
        elif choice == "F64":
            await update.message.reply_text(F64_MESSAGE, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            return MEDICAL_MENU
        elif choice == "Операции":
            await update.message.reply_text(SURGERY_INFO_MESSAGE, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(SURGERY_CHOICE_BUTTONS, resize_keyboard=True))
            return MEDICAL_SURGERY_MENU
        elif choice == "Спланировать операцию":
            await update.message.reply_text(SURGERY_PLANNING_PROMPT)
            context.user_data["type"] = "Планирование операции"
            return TYPING
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
    """Обрабатывает выбор направления гормональной терапии."""
    try:
        choice = update.message.text
        if choice == "Мужская ГТ":
            await update.message.reply_text(MASCULINIZING_HRT_INFO, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([["DIY"], ["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]], resize_keyboard=True))
            return MEDICAL_FTM_HRT
        elif choice == "Женская ГТ":
            await update.message.reply_text(FEMINIZING_HRT_INFO, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([["DIY"], ["Запросить консультацию по женской ГТ"], [BACK_BUTTON]], resize_keyboard=True))
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
    """Обрабатывает вопросы по маскулинизирующей ГТ."""
    try:
        choice = update.message.text
        if choice == "DIY":
            keyboard = ReplyKeyboardMarkup([["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(DIY_HRT_WARNING, parse_mode="Markdown", reply_markup=keyboard)
            return  # Остаемся в этом состоянии до выбора
        elif choice == "Запросить консультацию по мужской ГТ" or choice == "Консультация":
            await update.message.reply_text(CONSULTATION_PROMPT, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Консультация по мужской ГТ"
            return TYPING
        elif choice == "Я понимаю риски, скачать гайд":
            link = DIY_HRT_GUIDE_LINK
            file_name = DIY_HRT_GUIDE_NAME
            await update.message.reply_text(
                f"Вы можете скачать гайд по DIY ГТ: [{file_name}]({link})",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([["Запросить консультацию по мужской ГТ"], [BACK_BUTTON]], resize_keyboard=True),
                disable_web_page_preview=True
            )
            return  # Возвращаемся в это состояние
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
    """Обрабатывает вопросы по феминизирующей ГТ."""
    try:
        choice = update.message.text
        if choice == "DIY":
            keyboard = ReplyKeyboardMarkup([["Я понимаю риски, скачать гайд"], [BACK_BUTTON]], resize_keyboard=True)
            await update.message.reply_text(DIY_HRT_WARNING, parse_mode="Markdown", reply_markup=keyboard)
            return  # Остаемся в этом состоянии до выбора
        elif choice == "Запросить консультацию по женской ГТ" or choice == "Консультация":
            await update.message.reply_text(CONSULTATION_PROMPT, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Консультация по женской ГТ"
            return TYPING
        elif choice == "Я понимаю риски, скачать гайд":
            link = DIY_HRT_GUIDE_LINK
            file_name = DIY_HRT_GUIDE_NAME
            await update.message.reply_text(
                f"Вы можете скачать гайд по DIY ГТ: [{file_name}]({link})",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([["Запросить консультацию по женской ГТ"], [BACK_BUTTON]], resize_keyboard=True),
                disable_web_page_preview=True
            )
            return  # Возвращаемся в это состояние
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
    """Обрабатывает выбор типа хирургического вмешательства."""
    try:
        choice = update.message.text
        if choice == "ФТМ Операции":
            await update.message.reply_text(FTM_SURGERY_INFO, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([["Запросить консультацию по ФТМ операциям"], [BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Консультация по ФТМ операциям"
            return TYPING
        elif choice == "МТФ Операции":
            await update.message.
            reply_text(MTF_SURGERY_INFO, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([["Запросить консультацию по МТФ операциям"], [BACK_BUTTON]], resize_keyboard=True))
            context.user_data["type"] = "Консультация по МТФ операциям"
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

async def volunteer_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало сбора информации о волонтере."""
    await update.message.reply_text("Как вас зовут?")
    return VOLUNTEER_NAME

async def volunteer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает имя волонтера."""
    context.user_data["volunteer_name"] = update.message.text
    await update.message.reply_text("Из какого вы региона?")
    return VOLUNTEER_REGION

async def volunteer_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает регион волонтера."""
    context.user_data["volunteer_region"] = update.message.text
    await update.message.reply_text("Какая помощь вам интересна (например, юридическая, психологическая, техническая)?")
    return VOLUNTEER_HELP_TYPE

async def volunteer_help_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает тип помощи, которую может оказать волонтер."""
    context.user_data["volunteer_help_type"] = update.message.text
    await update.message.reply_text("Как с вами можно связаться (Telegram, email)?")
    return VOLUNTEER_CONTACT

async def volunteer_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает контактные данные волонтера и завершает сбор."""
    context.user_data["volunteer_contact"] = update.message.text
    volunteer_info = f"""Новый волонтер!
Имя: {context.user_data.get('volunteer_name', 'не указано')}
Регион: {context.user_data.get('volunteer_region', 'не указано')}
Тип помощи: {context.user_data.get('volunteer_help_type', 'не указано')}
Контакт: {context.user_data.get('volunteer_contact', 'не указано')}"""
    await context.bot.send_message(chat_id=YOUR_ADMIN_CHAT_ID, text=volunteer_info)
    await update.message.reply_text("Спасибо за вашу готовность помочь! Мы свяжемся с вами в ближайшее время.", reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    return MAIN_MENU

async def anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает и пересылает анонимное сообщение."""
    message = update.message.text
    await context.bot.send_message(chat_id=YOUR_ADMIN_CHAT_ID, text=f"Анонимное сообщение: {message}")
    await update.message.reply_text("Ваше анонимное сообщение отправлено администраторам.", reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    return MAIN_MENU

async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает ввод текста пользователя для различных запросов."""
    user_text = update.message.text
    message_type = context.user_data.get("type", "Сообщение")
    consultation_type = context.user_data.get("consultation_type")
    report = f"Новое сообщение от пользователя:\nТип: {message_type}"
    if consultation_type:
        report += f"\nТип консультации: {consultation_type}"
    report += f"\nТекст: {user_text}"
    await context.bot.send_message(chat_id=YOUR_ADMIN_CHAT_ID, text=report)
    await update.message.reply_text(MESSAGE_SENT_SUCCESS, reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True))
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет текущий разговор."""
    await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
    return START

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(YOUR_BOT_TOKEN).build()

    # Обработчик разговоров
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_menu)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, faq_legal)],
            FAQ_MED: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_menu)],
            MEDICAL_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_menu)],
            MEDICAL_GENDER_THERAPY_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_gender_therapy_menu)],
            MEDICAL_FTM_HRT: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_ftm_hrt)],
            MEDICAL_MTF_HRT: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_mtf_hrt)],
            MEDICAL_SURGERY_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, medical_surgery_menu)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing)],
            VOLUNTEER_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_name)],
            VOLUNTEER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_region)],
            VOLUNTEER_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_help_type)],
            VOLUNTEER_HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, volunteer_contact)],
            VOLUNTEER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            ANONYMOUS_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, anonymous_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
