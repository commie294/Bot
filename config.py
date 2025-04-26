import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    # Основные настройки
    TOKEN: str = os.getenv("BOT_TOKEN")
    ADMIN_CHAT_ID: Optional[str] = os.getenv("ADMIN_CHAT_ID")
    HASH_SALT: str = os.getenv("HASH_SALT", "default_salt")
    
    # Время ожидания (секунды)
    TIMEOUTS = {
        "message_send": 10,
        "volunteer_processing": 30
    }

    @classmethod
    def validate(cls):
        """Проверка обязательных настроек"""
        if not cls.TOKEN:
            raise ValueError("Токен бота не указан в .env файле")
        if not all(cls.CHANNELS.values()):
            logger.warning("Не все ID каналов указаны в конфигурации")
