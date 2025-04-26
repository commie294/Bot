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
        self.user_friendly = user_friendly or "Произошла ошибка
