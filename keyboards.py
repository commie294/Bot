from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

BACK_BUTTON = "⬅️ Назад"
DONE_BUTTON = "✅ Готово"

MAIN_MENU_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🆘 Попросить о помощи", callback_data="main_help")],
    [InlineKeyboardButton("➕ Предложить ресурс", callback_data="main_resource")],
    [InlineKeyboardButton("🤝 Стать волонтёром", callback_data="main_volunteer")],
    [InlineKeyboardButton("💸 Поддержать проект", callback_data="main_donate")],
    [InlineKeyboardButton("✉️ Анонимное сообщение", callback_data="main_anonymous")]
])

HELP_MENU_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🚨 Срочная помощь", callback_data="help_emergency")],
    [InlineKeyboardButton("⚖️ Юридическая помощь", callback_data="help_legal")],
    [InlineKeyboardButton("🩺 Медицинская помощь", callback_data="help_medical")],
    [InlineKeyboardButton("🏠 Жилье/финансы", callback_data="help_housing")],
    [InlineKeyboardButton("🧠 Психологическая помощь", callback_data="help_psych")],
    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
])

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
