from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

BACK_BUTTON = "⬅️ Назад"
DONE_BUTTON = "✅ Готово"

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
]

LEGAL_MENU_BUTTONS = [
    ["🏳️‍🌈 ЛГБТ+ семьи"],
    ["📝 Как сменить документы"],
    ["📢 Что такое пропаганда ЛГБТ?"],
    ["🗣️ Юридическая консультация"],
    ["🚨 Сообщить о нарушении"],
]

MEDICAL_MENU_BUTTONS = [
    ["🗣️ Медицинская консультация"],
    ["💉HRT"],
    ["❓ F64"],
    ["⚕️ Операции"],
]

GENDER_THERAPY_CHOICE_BUTTONS = [
    ["T"],
    ["E"],
]

SURGERY_INFO_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🗓️ Спланировать операцию", callback_data='plan_surgery')],
    [InlineKeyboardButton("ФТМ Операции", callback_data='ftm_surgery')],
    [InlineKeyboardButton("МТФ Операции", callback_data='mtf_surgery')]
])

VOLUNTEER_START_KEYBOARD = ReplyKeyboardMarkup([["Далее", "Отмена"]], resize_keyboard=True)

VOLUNTEER_HELP_TYPE_BUTTONS = [
    ["Юридическая"],
    ["Психологическая"],
    ["Медицинская"],
    ["Финансовая"],
    ["Техническая"],
    ["Другая помощь"]
]

VOLUNTEER_HELP_TYPE_KEYBOARD = ReplyKeyboardMarkup(VOLUNTEER_HELP_TYPE_BUTTONS, resize_keyboard=True)

FINISH_MENU_KEYBOARD = ReplyKeyboardMarkup([[DONE_BUTTON, BACK_BUTTON]], resize_keyboard=True)

REGIONS = [
    ["РФ", "Украина"],
    ["Беларусь", "Казахстан"],
    ["Другой регион"]
]
