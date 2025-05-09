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
