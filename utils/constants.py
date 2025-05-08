import os
from enum import IntEnum
from typing import Dict, Tuple
from telegram import InlineKeyboardMarkup
from keyboards import MAIN_MENU_BUTTONS, HELP_MENU_BUTTONS, BACK_BUTTON, LEGAL_MENU_BUTTONS, MEDICAL_MENU_BUTTONS
from keyboards import VOLUNTEER_START_KEYBOARD

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
    MEDICAL_GENDER_THERAPY_INLINE = 13
    MEDICAL_FTM_HRT = 14
    MEDICAL_MTF_HRT = 15
    MEDICAL_SURGERY_PLANNING = 16
    DONE_STATE = 17
    RESOURCE_PROPOSAL = 18
    DONATE_INFO = 19
    SURGERY_START = 20
    SURGERY_CHOICE = 21
    SURGERY_BUDGET = 22
    SURGERY_RESULT = 23
    FAREWELL = 24

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

MAIN_MENU_ACTIONS: Dict[str, Tuple[InlineKeyboardMarkup, str, int]] = {
    "🆘 Попросить о помощи": (
        HELP_MENU_BUTTONS,
        "Выберите категорию помощи:",
        BotState.HELP_MENU
    ),
    "➕ Предложить ресурс": (
        InlineKeyboardMarkup([[BACK_BUTTON]]),
        "Пожалуйста, напишите описание или ссылку на ресурс:",
        BotState.RESOURCE_PROPOSAL
    ),
    "🤝 Стать волонтёром": (
        VOLUNTEER_START_KEYBOARD,
        "Стать волонтёром?",
        BotState.VOLUNTEER_CONFIRM_START
    ),
    "💸 Поддержать проект": (
        InlineKeyboardMarkup([[BACK_BUTTON]]),
        "Информация о способах поддержки проекта:",
        BotState.DONATE_INFO
    ),
    "✉️ Анонимное сообщение": (
        InlineKeyboardMarkup([[BACK_BUTTON]]),
        "Пожалуйста, напишите ваше анонимное сообщение:",
        BotState.ANONYMOUS_MESSAGE
    ),
}

def check_env_vars():
    required_vars = ["BOT_TOKEN", "ADMIN_CHAT_ID", "HASH_SALT", "DIY_HRT_GUIDE_PATH"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Отсутствуют переменные окружения: {', '.join(missing_vars)}")
