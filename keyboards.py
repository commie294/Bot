from telegram import InlineKeyboardMarkup, InlineKeyboardButton

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

LEGAL_MENU_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏳️‍🌈 ЛГБТ+ семьи", callback_data="legal_lgbt")],
    [InlineKeyboardButton("📝 Как сменить документы", callback_data="legal_docs")],
    [InlineKeyboardButton("📢 Что такое пропаганда ЛГБТ?", callback_data="legal_propaganda")],
    [InlineKeyboardButton("🗣️ Юридическая консультация", callback_data="legal_consult")],
    [InlineKeyboardButton("🚨 Сообщить о нарушении", callback_data="legal_abuse")],
    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_help")]
])

MEDICAL_MENU_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🗣️ Медицинская консультация", callback_data="medical_consult")],
    [InlineKeyboardButton("💉HRT", callback_data="medical_hrt")],
    [InlineKeyboardButton("❓ F64", callback_data="medical_f64")],
    [InlineKeyboardButton("⚕️ Операции", callback_data="medical_surgery")],
    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_help")]
])

GENDER_THERAPY_CHOICE_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("T♂️", callback_data="hrt_t")],
    [InlineKeyboardButton("E♀️", callback_data="hrt_e")],
    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_medical")]
])

SURGERY_INFO_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("ФТМ Операции", callback_data='ftm_surgery')],
    [InlineKeyboardButton("МТФ Операции", callback_data='mtf_surgery')],
    [InlineKeyboardButton("⬅️ Назад", callback_data='back_to_medical')]
])

VOLUNTEER_START_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("Далее", callback_data="volunteer_start")],
    [InlineKeyboardButton("Отмена", callback_data="back_to_main")]
])

VOLUNTEER_HELP_TYPE_BUTTONS = [
    [InlineKeyboardButton("Юридическая", callback_data="volunteer_help_юридическая")],
    [InlineKeyboardButton("Психологическая", callback_data="volunteer_help_психологическая")],
    [InlineKeyboardButton("Медицинская", callback_data="volunteer_help_медицинская")],
    [InlineKeyboardButton("Финансовая", callback_data="volunteer_help_финансовая")],
    [InlineKeyboardButton("Техническая", callback_data="volunteer_help_техническая")],
    [InlineKeyboardButton("Другая помощь", callback_data="volunteer_help_другая")]
]

VOLUNTEER_HELP_TYPE_KEYBOARD = InlineKeyboardMarkup(VOLUNTEER_HELP_TYPE_BUTTONS)

FINISH_MENU_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton(DONE_BUTTON, callback_data="volunteer_finish")],
    [InlineKeyboardButton(BACK_BUTTON, callback_data="back_to_main")]
])

REGIONS = [
    [InlineKeyboardButton("РФ", callback_data="region_рф"), InlineKeyboardButton("Украина", callback_data="region_украина")],
    [InlineKeyboardButton("Беларусь", callback_data="region_беларусь"), InlineKeyboardButton("Казахстан", callback_data="region_казахстан")],
    [InlineKeyboardButton("Другой регион", callback_data="region_другой")]
]

GENDER_CHOICE_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("ФТМ", callback_data="surgery_type_ftm")],
    [InlineKeyboardButton("МТФ", callback_data="surgery_type_mtf")]
])
