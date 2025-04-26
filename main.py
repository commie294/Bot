import asyncio
import hashlib
import logging
from typing import Dict, Any

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import TelegramError

from config import Config
from states import States
from errors import (
    BotError,
    TelegramAPIError,
    ValidationError,
    StateError,
    global_error_handler,
)
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
    FAREWELL_MESSAGE,
    ANONYMOUS_CONFIRMATION,
)
from keyboards import (
    MAIN_MENU_BUTTONS,
    HELP_MENU_BUTTONS,
    LEGAL_MENU_BUTTONS,
    MEDICAL_MENU_BUTTONS,
    GENDER_THERAPY_CHOICE_BUTTONS,
    BACK_BUTTON,
    SURGERY_INFO_KEYBOARD,
    VOLUNTEER_HELP_TYPE_KEYBOARD,
)
from channels import CHANNELS
from models.user_data import UserDataManager
from utils.async_utils import gather_with_concurrency, send_message_safe

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def generate_message_id(user_id: int) -> str:
    """Генерирует хеш для анонимной идентификации сообщений"""
    return hashlib.sha256(f"{Config.HASH_SALT}_{user_id}_{os.urandom(16)}".encode()).hexdigest()[:8]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start"""
    try:
        await update.message.reply_text(
            START_MESSAGE,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
            parse_mode="Markdown",
        )
        return States.MAIN_MENU
    except Exception as e:
        raise TelegramAPIError(e, {"user_id": update.effective_user.id})

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик главного меню"""
    user_data = UserDataManager(context)
    user_choice = update.message.text
    
    try:
        if user_choice == "🆘 Попросить о помощи":
            await update.message.reply_text(
                HELP_MENU_MESSAGE,
                reply_markup=ReplyKeyboardMarkup(HELP_MENU_BUTTONS + [[BACK_BUTTON]], 
                resize_keyboard=True,
                parse_mode="Markdown",
            )
            return States.HELP_MENU
            
        elif user_choice == "➕ Предложить ресурс":
            user_data.request_type = "Ресурс"
            await update.message.reply_text(
                RESOURCE_PROMPT_MESSAGE, 
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )
            return States.TYPING
            
        elif user_choice == "🤝 Стать волонтером":
            await update.message.reply_text(
                VOLUNTEER_MESSAGE,
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )
            return States.VOLUNTEER_START
            
        elif user_choice == "💸 Поддержать проект":
            user_data.request_type = "Донат"
            await update.message.reply_text(
                DONATE_MESSAGE,
                parse_mode="Markdown",
                disable_web_page_preview=True,
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )
            return States.MAIN_MENU
            
        elif user_choice == "✉️ Анонимное сообщение":
            await update.message.reply_text(
                "Пожалуйста, напишите ваше анонимное сообщение:",
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            )
            user_data.request_type = "Анонимное сообщение"
            return States.ANONYMOUS_MSG
            
        elif user_choice == BACK_BUTTON:
            await update.message.reply_text(
                FAREWELL_MESSAGE,
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
            
        else:
            await update.message.reply_text(CHOOSE_FROM_MENU)
            return States.MAIN_MENU
            
    except Exception as e:
        raise TelegramAPIError(e, {
            "user_id": update.effective_user.id,
            "user_choice": user_choice
        })

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик меню помощи"""
    user_data = UserDataManager(context)
    user_choice = update.message.text
    
    try:
        if user_choice == BACK_BUTTON:
            await update.message.reply_text(
                BACK_TO_MAIN_MENU,
                reply_markup=ReplyKeyboardMarkup(MAIN_MENU_BUTTONS, resize_keyboard=True),
            )
            return States.MAIN_MENU
            
        elif user_choice == "🚨 Срочная помощь":
            user_data.request_type = "Срочная помощь"
            await update.message.reply_text(
                EMERGENCY_MESSAGE,
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )
            return States.TYPING
            
        elif user_choice == "🏠 Жилье/финансы":
            user_data.request_type = "Жилье/финансы"
            await update.message.reply_text(
                HOUSING_FINANCE_PROMPT,
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )
            return States.TYPING
            
        elif user_choice == "🧠 Психологическая помощь":
            user_data.request_type = "Психологическая помощь"
            await update.message.reply_text(
                PSYCHOLOGICAL_HELP_PROMPT,
                reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True)
            )
            return States.TYPING
            
        elif user_choice == "🩺 Медицинская помощь":
            await update.message.reply_text(
                "Выберите категорию медицинской помощи:",
                reply_markup=ReplyKeyboardMarkup(MEDICAL_MENU_BUTTONS + [[BACK_BUTTON]], 
                resize_keyboard=True),
            )
            return States.MEDICAL_MENU
            
        elif user_choice == "⚖️ Юридическая помощь":
            await update.message.reply_text(
                "Выберите категорию юридической помощи:",
                reply_markup=ReplyKeyboardMarkup(LEGAL_MENU_BUTTONS + [[BACK_BUTTON]], 
                resize_keyboard=True),
            )
            return States.LEGAL_MENU
            
        else:
            await update.message.reply_text(CHOOSE_HELP_CATEGORY)
            return States.HELP_MENU
            
    except Exception as e:
        raise TelegramAPIError(e, {
            "user_id": update.effective_user.id,
            "user_choice": user_choice
        })

async def handle_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик ввода текста"""
    user_data = UserDataManager(context)
    user_text = update.message.text
    request_type = user_data.request_type or "Сообщение"

    try:
        if user_text and user_text != BACK_BUTTON:
            channel_mapping = {
                "Ресурс": "t64_misc",
                "Срочная помощь": "t64_gen",
                "Помощь - Сообщение о нарушении (юридическое)": "t64_legal",
                # ... остальные маппинги
            }

            channel_name = channel_mapping.get(request_type)
            if channel_name:
                success = await send_message_safe(
                    context.bot,
                    CHANNELS.get(channel_name),
                    f"Запрос от пользователя:\n\n{user_text}"
                )
                
                if success:
                    await update.message.reply_text(
                        MESSAGE_SENT_SUCCESS,
                        reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
                    )
                    return States.MAIN_MENU
                else:
                    raise TelegramAPIError("Failed to send message")
                    
            else:
                raise ValidationError(f"Неизвестный тип запроса: {request_type}")
                
        elif user_text == BACK_BUTTON:
            if request_type in ["Ресурс", "Срочная помощь", "Жилье/финансы", "Психологическая помощь"]:
                return await help_menu(update, context)
            else:
                return await main_menu(update, context)
                
        return States.TYPING
        
    except Exception as e:
        if not isinstance(e, (BotError, TelegramAPIError)):
            e = TelegramAPIError(e)
        raise e

# ... (остальные обработчики аналогично)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик отмены"""
    user_data = UserDataManager(context)
    await update.message.reply_text(
        CANCEL_MESSAGE,
        reply_markup=ReplyKeyboardRemove()
    )
    user_data.clear()
    return ConversationHandler.END

def setup_handlers(application: Application) -> None:
    """Настройка обработчиков"""
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            States.MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            States.HELP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_menu)],
            States.TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing)],
            # ... остальные состояния
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    application.add_error_handler(global_error_handler)

def main() -> None:
    """Запуск бота"""
    try:
        Config.validate()
        
        application = Application.builder() \
            .token(Config.TOKEN) \
            .build()
            
        setup_handlers(application)
        
        logger.info("Бот запущен")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Ошибка запуска бота: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
