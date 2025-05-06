class BotState:
    MAIN_MENU = 0
    HELP_MENU = 1
    TYPING = 2
    FAQ_LEGAL = 3
    MEDICAL_MENU = 4
    MEDICAL_GENDER_THERAPY_MENU = 5
    MEDICAL_FTM_HRT = 6
    MEDICAL_MTF_HRT = 7
    MEDICAL_SURGERY_PLANNING = 8
    VOLUNTEER_CONFIRM_START = 9
    VOLUNTEER_NAME = 10
    VOLUNTEER_REGION = 11
    VOLUNTEER_HELP_TYPE = 12
    VOLUNTEER_CONTACT = 13
    ANONYMOUS_MESSAGE = 14
    DONE_STATE = 15
    SET_REMINDER = 16  # Новое состояние для установки напоминаний

REQUEST_TYPES = {
    "resource": "resource_request",
    "emergency": "emergency_request",
    "legal_abuse": "legal_abuse_request",
    "legal_consult": "legal_consult_request",
    "medical_consult": "medical_consult_request",
    "ftm_hrt": "ftm_hrt_request",
    "mtf_hrt": "mtf_hrt_request",
    "surgery": "surgery_request",
    "psych": "psych_request",
    "housing": "housing_request",
}

def check_env_vars():
    required_vars = ["BOT_TOKEN", "ADMIN_CHAT_ID", "HASH_SALT"]
    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"Переменная окружения {var} не установлена")
