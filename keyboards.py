from telegram import ReplyKeyboardMarkup

BACK_BUTTON = "⬅️ Назад"

MAIN_MENU_BUTTONS = [
    ["🆘 Попросить о помощи"],
    ["➕ Предложить ресурс"],
    ["🤝 Стать волонтером"],
    ["💸 Поддержать проект"],
    ["✉️ Анонимное сообщение"],
]

HELP_MENU_BUTTONS = [
    ["🚨 Срочная помощь"],
    ["⚖️ Юридическая помощь"],
    ["🩺 Медицинская помощь"],
    ["🏠 Жилье/финансы"],
    ["🧠 Психологическая помощь"],
    [BACK_BUTTON],
]

LEGAL_MENU_BUTTONS = [
    ["🏳️‍🌈 ЛГБТ+ семьи"],
    ["📝 Как сменить документы"],
    ["📢 Что такое пропаганда ЛГБТ?"],
    ["🗣️ Юридическая консультация"],
    ["🚨 Сообщить о нарушении"],
    [BACK_BUTTON],
]

MEDICAL_MENU_BUTTONS = [
    ["🗣️ Медицинская консультация"],
    ["💉HRT"],
    ["❓ F64"],
    ["⚕️ Операции"],
    [BACK_BUTTON],
]

GENDER_THERAPY_CHOICE_BUTTONS = [
    ["T"],
    ["E"],
    [BACK_BUTTON],
]

SURGERY_INFO_KEYBOARD = ReplyKeyboardMarkup([["🗓️ Спланировать операцию"], [BACK_BUTTON]], resize_keyboard=True)
