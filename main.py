import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Состояния диалога
START, MENU, HELP_TYPE, TYPING, FAQ_LEGAL, FAQ_MED = range(6)

# Полные ответы на FAQ вопросы
FAQ_RESPONSES = {
    # Юридические вопросы
    "Как сейчас сменить документы?": """
В России смена гендерного маркера сейчас возможна только через суд. Это сложный процесс, который редко проходит без хирургических вмешательств — многое зависит от конкретного судьи и региона.

Имя в ЗАГСе могут не позволить сменить, если оно «не соответствует» гендерному маркеру. В редких случаях удаётся выбрать нейтральное имя. Убрать отчество также можно не во всех отделениях — зависит от практики на месте.

Мы можем связать вас с юристами, которые помогут оценить риски и шаги в вашем случае.""",

    "Что такое пропаганда ЛГБТ?": """
Закон о «ЛГБТ-пропаганде» формулируется крайне расплывчато. На практике, под него могут пытаться подвести:
• публикации в соцсетях с описанием своего опыта
• трансфрендли контент (видео, посты, блоги)
• публичное упоминание смены пола или ориентации
• даже поддержка т-персон в медиа

Тем не менее:
• переписка и частные сообщения не подпадают под закон
• личная идентичность и самовыражение — не преступление
• законы не действуют вне юрисдикции РФ

Если у вас есть опасения — мы постараемся подобрать юриста и пояснить, что реально грозит, а что нет.""",

    # Медицинские вопросы
    "Женская ГТ": """
**Женская гормональная терапия**

Феминизирующая терапия включает приём эстрогенов и антиандрогенов. В странах СНГ распространены такие препараты:

*Эстрогены:*
• Эстрадиол валерат (инъекции): часто приобретается через интернет (включая зарубежные аптеки)
• Эстрадиол гель: «Дивигель», «Эстрожель» — можно купить в аптеке (часто без рецепта)
• Таблетки: «Прогинова» (меньше используется из-за риска тромбозов)

*Антиандрогены:*
• Ципротерон ацетат (Андрокур) — часто недоступен без рецепта
• Бикалутамид — (25–50 мг/день)
• Спиронолактон — есть не везде, дозы 100–200 мг/день

*Важно знать:*
• Эндокринологи почти никогда не выписывают женские гормоны т-персонам, особенно без смены документов
• Инъекционные препараты обычно доступны только через интернет
• Самостоятельный приём требует регулярных анализов (гормоны, печень, свёртываемость)""",

    "Мужская ГТ": """
**Мужская гормональная терапия**

Маскулинизирующая терапия — это приём тестостерона для развития мужских признаков.

*Формы и доступность:*
• Андрогель (гель): можно купить в аптеке, иногда без рецепта
• Инъекции (энантат, ципионат, сустанон, небидо): официально — только по рецепту, на практике — приобретаются в интернете, включая стероидные магазины

*Примерные схемы:*
• Гель: 5 г (1 саше) ежедневно
• Инъекции: 50–100 мг еженедельно или по индивидуальной схеме

*Важно:*
• Эндокринологи чаще всего отказываются назначать гормоны т-персонам без смены гендерного маркера
• Анализы (тестостерон, гематокрит и др.) можно сдавать в частных лабораториях""",

    "Диагноз F64": """
F64 — это код в международной классификации болезней (МКБ-10), обозначающий гендерную дисфорию. В странах СНГ чаще всего используют формулировку «расстройство половой идентификации» или «транссексуализм».

*Важно:*
• В РФ эта справка не имеет юридической силы и не даёт доступ к гормонам или смене документов
• Врачам в РФ запрещено назначать гормоны т-персонам без смены гендерного маркера
• Справка F64 чаще всего используется для операций за рубежом — клиники требуют её для допуска

*Как получить:*
У психиатра (государственного или частног��), в редких случаях — у трансфрендли специалистов в других странах.""",

    "Где делают операции?": """
На данный момент в России не проводят официальные операции по смене пола. Гендерно-аффирмативные хирургические вмешательства доступны за рубежом:

*Страны:*
• Таиланд (лидер по количеству операций)
• Турция (оптимальное соотношение цена/качество)
• Армения, Сербия (бюджетные варианты)
• Мексика, Испания (для граждан этих стран)

*Требования:*
1. Диагноз F64 (в большинстве клиник)
2. Гормональная терапия (обычно 12+ месяцев)
3. Консультация с хирургом

*Мы можем:*
- Подсказать проверенные клиники
- Помочь с переводом документов
- Дать контакты людей, уже прошедших операции"""
}

# Клавиатуры
main_kb = ReplyKeyboardMarkup([
    ["Запрос о помощи"],
    ["Предложить ресурс", "Пожертвовать"],
    ["��нонимное сообщение", "Стать волонтёром"],
    ["Назад"]
], resize_keyboard=True)

help_kb = ReplyKeyboardMarkup([
    ["Юридическая", "Медицинская"],
    ["Психологическая", "Жильё и финансы"],
    ["Назад"]
], resize_keyboard=True)

legal_faq_kb = ReplyKeyboardMarkup([
    ["Как сейчас сменить документы?", "Что такое пропаганда ЛГБТ?"],
    ["Консультация юриста", "Назад"]
], resize_keyboard=True)

medical_faq_kb = ReplyKeyboardMarkup([
    ["Женская ГТ", "Мужская ГТ"],
    ["Диагноз F64", "Где делают операции?"],
    ["Консультация врача", "Назад"]
], resize_keyboard=True)

# ID каналов для пересылки
CHANNELS = {
    "Юридическая": -100123456,
    "Психологическая": -100789012,
    "Медицинская": -100345678,
    "Жильё и финансы": -100901234,
    "Анонимное сообщение": -100567890,
    "Ресурсы": -100567890
}

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Действие отменено. Возврат в главное меню.",
        reply_markup=main_kb
    )
    return MENU

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Это бот поддержки проекта 'Переход в неположенном месте'.\n\n"
        "Вы можете:\n"
        "- Запросить помощь (юридическую, медицинскую и др.)\n"
        "- Предложить полезный ресурс\n"
        "- Поддержать проект финансово\n"
        "- Стать волонтёром\n"
        "- Отправить анонимное сообщение",
        reply_markup=main_kb
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == "Запрос о помощи":
        await update.message.reply_text("Выберите категорию помощи:", reply_markup=help_kb)
        return HELP_TYPE
    elif choice == "Предложить ресурс":
        context.user_data["type"] = "Предложение ресурса"
        await update.message.reply_text("Опишите ресурс, котор��й хотите предложить:", reply_markup=ReplyKeyboardRemove())
        return TYPING
    elif choice == "Пожертвовать":
        await update.message.reply_text(
            "Вы можете поддержать проект:\n\n"
            "• Boosty: https://boosty.to/t64/donate\n"
            "• USDT (TRC-20): TLTBoXCSifWGBeuiRkxkPtH9M9mfwSf1sf",
            reply_markup=main_kb,
            disable_web_page_preview=True
        )
        return MENU
    elif choice == "Стать волонтёром":
        await update.message.reply_text(
            "Заполните анкету волонтёра:\n"
            "https://forms.gle/n2mZdRA2fYBeeCUY7",
            reply_markup=main_kb,
            disable_web_page_preview=True
        )
        return MENU
    elif choice == "Анонимное сообщение":
        context.user_data["type"] = "Анонимное сообщение"
        await update.message.reply_text("Напишите ваше сообщение. Оно будет передано без указания отправителя.", reply_markup=ReplyKeyboardRemove())
        return TYPING
    elif choice == "Назад":
        return await start(update, context)
    return MENU

async def help_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = update.message.text
    if category == "Юридическая":
        await update.message.reply_text("Выберите вопрос:", reply_markup=legal_faq_kb)
        return FAQ_LEGAL
    elif category == "Медицинская":
        await update.message.reply_text("Выберите вопрос:", reply_markup=medical_faq_kb)
        return FAQ_MED
    elif category == "Назад":
        return await start(update, context)
    else:
        context.user_data["type"] = f"Запрос - {category}"
        await update.message.reply_text("Опишите вашу ситуацию:", reply_markup=ReplyKeyboardRemove())
        return TYPING

async def handle_legal_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = update.message.text
    if question == "Назад":
        await update.message.reply_text("Выберите категорию:", reply_markup=help_kb)
        return HELP_TYPE
    elif question == "Консультация юриста":
        context.user_data["type"] = "Юридическая - Консультация"
        await update.message.reply_text("Опишите ваш вопрос юристу:", reply_markup=ReplyKeyboardRemove())
        return TYPING
    else:
        response = FAQ_RESPONSES.get(question, "Информация по этому вопросу временно недоступна.")
        await update.message.reply_text(response, reply_markup=legal_faq_kb, parse_mode="Markdown")
        return FAQ_LEGAL

async def handle_medical_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = update.message.text
    if question == "Назад":
        await update.message.reply_text("Выберите категорию:", reply_markup=help_kb)
        return HELP_TYPE
    elif question == "Консультация врача":
        context.user_data["type"] = "Медицинская - Консультация"
        await update.message.reply_text("Опишите ваш медицинский вопрос:", reply_markup=ReplyKeyboardRemove())
        return TYPING
    else:
        response = FAQ_RESPONSES.get(question, "Информация по этому вопросу временно недоступна.")
        await update.message.reply_text(response, reply_markup=medical_faq_kb, parse_mode="Markdown")
        return FAQ_MED

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message.text
    request_type = context.user_data.get("type", "Неизвестный запрос")
    
    # Определение канала для пересылки
    channel_key = request_type.split()[0]
    if "СРОЧНО" in request_type:
        channel_key = "Срочная"
    chat_id = CHANNELS.get(channel_key, ADMIN_CHAT_ID)
    
    # Формирование сообщения для админа
    text = f"📩 *{request_type}*\n"
    if "Анонимное" not in request_type:
        text += f"От: @{update.message.from_user.username or 'нет'} (ID: {update.message.from_user.id})\n\n"
    text += msg
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown"
    )
    await update.message.reply_text("✅ Ваше сообщение отправлено!", reply_markup=main_kb)
    return MENU

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, help_category)],
            FAQ_LEGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_legal_faq)],
            FAQ_MED: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_medical_faq)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
