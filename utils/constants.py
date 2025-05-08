import os
from enum import IntEnum
from typing import Dict, Tuple
from telegram import ReplyKeyboardMarkup
from keyboards import MAIN_MENU_BUTTONS, HELP_MENU_BUTTONS, BACK_BUTTON, LEGAL_MENU_BUTTONS, MEDICAL_MENU_BUTTONS, GENDER_THERAPY_CHOICE_BUTTONS, VOLUNTEER_START_KEYBOARD

class BotState(IntEnum):
    START = 0
    MAIN_MENU = 1
    HELP_MENU = 2
    TYPING = 3
    FAQ_LEGAL = 4
    MEDICAL_MENU = 5
    VOLUNTEER_CONFIRM_START = 6
    VOLUNTEER_NAME = 7
    VOLUNTEER_REGION = 8
    VOLUNTEER_HELP_TYPE = 9
    VOLUNTEER_CONTACT = 10
    VOLUNTEER_FINISH = 11
    ANONYMOUS_MESSAGE = 12
    MEDICAL_GENDER_THERAPY_MENU = 13
    MEDICAL_FTM_HRT = 14
    MEDICAL_MTF_HRT = 15
    MEDICAL_SURGERY_PLANNING = 16
    DONE_STATE = 17
    RESOURCE_PROPOSAL = 18 # Упрощенное состояние для предложения ресурса

REQUEST_TYPES = {
    "resource": "Ресурс",
    "emergency": "Срочная помощь",
    "housing": "Жилье/финансы",
    "psych": "Психологическая помощь",
    "legal_consult": "Помощь - Юридическая консультация",
    "legal_abuse": "Помощь - Сообщение о нарушении (юридическое)",
    "medical_consult": "Помощь - Медицинская консультация",
    "ftm_hrt": "Помощь - Консультация по мужской ГТ",
    "mtf_hrt": "Помощь - Консультация по женской ГТ",
    "surgery": "Помощь - Планирование операции",
    "anonymous": "Анонимное сообщение",
}

MAIN_MENU_ACTIONS: Dict[str, Tuple[ReplyKeyboardMarkup, str, int]] = {
    "🆘 Попросить о помощи": (
        HELP_MENU_BUTTONS,
        "Выберите категорию помощи:",
        BotState.HELP_MENU
    ),
    "➕ Предложить ресурс": (
        ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
        "Пожалуйста, напишите описание или ссылку на ресурс:",
        BotState.RESOURCE_PROPOSAL # Теперь ведет сразу к предложению ресурса
    ),
}

def check_env_vars():
    required_vars = ["BOT_TOKEN", "ADMIN_CHAT_ID", "HASH_SALT", "DIY_HRT_GUIDE_PATH"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Отсутствуют переменные окружения: {', '.join(missing_vars)}")
