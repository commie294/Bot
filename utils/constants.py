from enum import IntEnum
from typing import Dict

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
    MEDICAL_SURGERY_INFO = 16
    DONE_STATE = 17
    RESOURCE_PROPOSAL = 18
    DONATE_INFO = 19
    FAREWELL = 20

REQUEST_TYPES = {
    "resource": "Ресурс",
    "emergency": "Срочная помощь",
    "housing": "Жилье/финансы",
    "psych": "Психологическая помощь",
    "legal_consult": "Юридическая консультация",
    "legal_abuse": "Сообщение о нарушении",
    "medical_consult": "Медицинская консультация",
    "ftm_hrt": "Консультация по мужской ГТ",
    "mtf_hrt": "Консультация по женской ГТ", 
    "ftm_surgery": "Консультация по ФТМ операциям",
    "mtf_surgery": "Консультация по МТФ операциям",
    "anonymous": "Анонимное сообщение"
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
