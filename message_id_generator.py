import hashlib
import os

def generate_message_id(user_id: int, hash_salt: str = None) -> str:
    """Генерирует хеш для анонимной идентификации сообщений"""
    if hash_salt is None:
        hash_salt = os.getenv("HASH_SALT")
        if hash_salt is None:
            raise ValueError("Переменная окружения HASH_SALT не найдена.")
    return hashlib.sha256(f"{hash_salt}_{user_id}_{os.urandom(16)}".encode()).hexdigest()[:8]
