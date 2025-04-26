from typing import Optional, Any, Dict
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class BotError(Exception):
    """Базовый класс ошибок бота"""
    def __init__(
        self, 
        message: str, 
        user_friendly: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.user_friendly = user_friendly or "Произошла ошибка. Пожалуйста, попробуйте позже."
        self.context = context or {}
        super().__init__(message)

class TelegramAPIError(BotError):
    """Ошибка API Telegram"""
    def __init__(self, original_error: Exception, context: Optional[dict] = None):
        super().__init__(
            f"Telegram API error: {str(original_error)}",
            "Ошибка связи с Telegram. Попробуйте позже.",
            context
        )
        self.original_error = original_error

class ValidationError(BotError):
    """Ошибка валидации данных"""
    pass

class StateError(BotError):
    """Некорректное состояние бота"""
    pass

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Глобальный обработчик ошибок:
    - Логирует ошибки
    - Отправляет уведомления пользователю и админу
    - Восстанавливает работу бота
    """
    error = context.error
    
    # Логирование
    if isinstance(error, BotError):
        logger.warning(f"BotError: {error}", extra=error.context)
    else:
        logger.critical(f"Unhandled error: {error}", exc_info=True)
    
    # Пользовательское уведомление
    if isinstance(update, Update):
        try:
            await update.effective_message.reply_text(
                getattr(error, 'user_friendly', "⚠️ Произошла непредвиденная ошибка")
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
    
    # Уведомление админа
    if Config.ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=Config.ADMIN_CHAT_ID,
                text=(
                    f"🚨 *Critical Error*\n\n"
                    f"```{type(error).__name__}: {error}```\n"
                    f"User: {update.effective_user.id if update else 'None'}"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")
