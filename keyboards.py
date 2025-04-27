from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

BACK_BUTTON = "⬅️ Назад"
DONE_BUTTON = "✅ Готово"
NEXT_BUTTON = "➡️ Далее"
SKIP_BUTTON = "⏭ Пропустить"
CANCEL_BUTTON = "❌ Отменить"

MAIN_MENU = ReplyKeyboardMarkup(
    [["🆘 Попросить о помощи", "➕ Предложить ресурс"], ["🤝 Стать волонтером", "💸 Поддержать проект"]],
    resize_keyboard=True)

HELP_INLINE_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🚨 Срочная помощь", callback_data="help_emergency")],
    [InlineKeyboardButton("⚖️ Юридическая помощь", callback_data="help_legal")],
    [InlineKeyboardButton("🧠 Медицинская помощь", callback_data="help_medical")],
    [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")],
])

LEGAL_INLINE_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏳️‍🌈 ЛГБТ+ семьи", callback_data="legal_families")],
    [InlineKeyboardButton("📝 Смена документов", callback_data="legal_docs")],
    [InlineKeyboardButton("📢 Пропаганда ЛГБТ", callback_data="legal_propaganda")],
    [InlineKeyboardButton("🗣️ Консультация", callback_data="legal_consult")],
    [InlineKeyboardButton("🚨 Нарушения", callback_data="legal_abuse")],
    [InlineKeyboardButton("⬅️ Назад", callback_data="back_help")]
])

MEDICAL_INLINE_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("💊 Консультация", callback_data="med_consult")],
    [InlineKeyboardButton("💉 HRT", callback_data="med_hrt")],
    [InlineKeyboardButton("⚕️ Операции", callback_data="med_surgery")],
    [InlineKeyboardButton("❓ F64", callback_data="med_f64")],
    [InlineKeyboardButton("⬅️ Назад", callback_data="back_help")]
])

HRT_INLINE_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔹 Мужская ГТ (T)", callback_data="hrt_male")],
    [InlineKeyboardButton("🔸 Женская ГТ (E)", callback_data="hrt_female")],
    [InlineKeyboardButton("⬅️ Назад", callback_data="back_medical")]
])

SURGERY_INLINE_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔹 ФТМ операции", callback_data="surgery_ftm")],
    [InlineKeyboardButton("🔸 МТФ операции", callback_data="surgery_mtf")],
    [InlineKeyboardButton("🗓️ Планирование", callback_data="surgery_plan")],
    [InlineKeyboardButton("⬅️ Назад", callback_data="back_medical")]
])

VOLUNTEER_KEYBOARD = ReplyKeyboardMarkup([
    [NEXT_BUTTON],
    [CANCEL_BUTTON]
], resize_keyboard=True)

VOLUNTEER_TYPES = ReplyKeyboardMarkup([
    ["Юридическая", "Психологическая"],
    ["Медицинская", "Финансовая"],
    ["Информационная", "Другая"],
    [DONE_BUTTON]
], resize_keyboard=True)

CONFIRM_KEYBOARD = ReplyKeyboardMarkup([
    ["✅ Подтвердить"],
    [BACK_BUTTON]
], resize_keyboard=True)

BASIC_NAVIGATION = ReplyKeyboardMarkup(
    [["➡️ Далее", "⬅️ Назад"]],
    resize_keyboard=True)

ANONYMOUS_KEYBOARD = ReplyKeyboardMarkup(
    [["❌ Отмена"]],
    resize_keyboard=True)
