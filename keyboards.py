from telegram import ReplyKeyboardMarkup

BACK_BUTTON = "⬅️ Назад"

MAIN_MENU_BUTTONS = [
    ["🆘 Попросить о помощи"],
    ["➕ Предложить ресурс"],
    ["🤝 Стать волонтером"],
    ["💸 Поддержать проект"],
    ["✉️ Анонимное сообщение"],
    ["✅ Готово"],
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

SURGERY_INFO_KEYBOARD = ReplyKeyboardMarkup([["🗓️ Спланировать операцию"]

# keyboards.py
from telegram import ReplyKeyboardMarkup

VOLUNTEER_HELP_TYPE_BUTTONS = [
    ["Юридическая"],
    ["Психологическая"],
    ["Медицинская"],
    ["Финансовая"],
    ["Техническая"],
    ["Другая помощь"]  # На всякий случай
]

VOLUNTEER_HELP_TYPE_KEYBOARD = ReplyKeyboardMarkup(VOLUNTEER_HELP_TYPE_BUTTONS, resize_keyboard=True)


