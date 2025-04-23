import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

CHOOSING, TYPING, MED_HORMONE_TYPE, FAQ_JUR, FAQ_MED = range(5)

main_keyboard = [
    ["Запрос о помощи", "Предложить ресурс"],
    ["Анонимное сообщение", "Стать волонтёром"],
    ["Пожертвовать", "Назад"]
]
main_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

help_keyboard = [
    ["Срочная", "Юридическая"],
    ["Психологическая", "Медицинская"],
    ["Жильё и финансы", "Назад"]
]
help_markup = ReplyKeyboardMarkup(help_keyboard, resize_keyboard=True)

faq_jur_keyboard = [
    ["Как сейчас сменить документы?"],
    ["Браки и смена пола"],
    ["Что такое ЛГБТ-пропаганда?"],
    ["Миграция и убежище"],
    ["Задать свой вопрос"]
]
faq_jur_markup = ReplyKeyboardMarkup(faq_jur_keyboard, resize_keyboard=True)

faq_med_keyboard = [
    ["Что такое F64?"],
    ["Как начать гормональную терапию?"],
    ["Где делают операции?"],
    ["Задать свой вопрос"]
]
faq_med_markup = ReplyKeyboardMarkup(faq_med_keyboard, resize_keyboard=True)

med_hormone_keyboard = [["Женская гормональная терапия", "Мужская гормональная терапия"]]
med_hormone_markup = ReplyKeyboardMarkup(med_hormone_keyboard, resize_keyboard=True)

CHANNELS = {
    "Медицинская": -1002051399111,
    "Юридическая": -1002092079550,
    "Психологическая": -1002085456901,
    "Жильё и финансы": -1002089296069,
    "Анонимное сообщение": -1002107093300,
    "Предложение ресурса": -1002107093300
}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это бот поддержки проекта «Переход в неположенном месте».\n"
        "Вы можете запросить помощь, оставить сообщение, предложить ресурс или поддержать нас.",
        reply_markup=main_markup
    )
    return CHOOSING

async def help_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите категорию запроса:", reply_markup=help_markup)
    return CHOOSING

async def help_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text
    context.user_data["type"] = f"Запрос о помощи ({category})"

    if category == "Юридическая":
        await update.message.reply_text("Вы можете выбрать один из популярных вопросов или сразу задать свой.",
                                        reply_markup=faq_jur_markup)
        return FAQ_JUR

    elif category == "Медицинская":
        await update.message.reply_text("Выберите один из популярных вопросов или задайте свой:",
                                        reply_markup=faq_med_markup)
        return FAQ_MED

    responses = {
        "Срочная": "Опишите вашу ситуацию, и мы постараемся помочь как можно быстрее.",
        "Психологическая": "Опишите, что вас беспокоит. Вы можете указать предпочтения к специалисту.",
        "Жильё и финансы": "Опишите свою ситуацию, и мы попробуем найти поддержку.",
        "Назад": "Вы вернулись в главное меню."
    }

    if category == "Назад":
        return await start(update, context)

    await update.message.reply_text(responses.get(category, "Опишите ваш запрос:"), reply_markup=main_markup)
    return TYPING
    async def handle_faq_jur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Как сейчас сменить документы?":
        await update.message.reply_text(
            "В РФ смена гендерного маркера возможна только через суд. Это сложно и часто требует операций. "
            "Имя меняют не всегда, особенно если оно не соответствует маркеру. Отчество можно убрать не во всех ЗАГСах."
        )
    elif text == "Браки и смена пола":
        await update.message.reply_text(
            "После смены пола брак автоматически расторгается. Новый можно заключить только с партнёром противоположного гендерного маркера. "
            "Подробности зависят от страны и документов."
        )
    elif text == "Что такое ЛГБТ-пропаганда?":
        await update.message.reply_text(
            "Под неё могут подпадать:\n— Публичные высказывания\n— Посты о своём опыте\n— Поддержка т-персон\n\n"
            "Переписка и личные сообщения не подпадают. Паниковать не стоит — мы поможем оценить риски."
        )
    elif text == "Миграция и убежище":
        await update.message.reply_text(
            "Опишите страну, где вы находитесь, и вашу ситуацию. Мы поможем с консультацией или поиском юриста."
        )
    else:
        await update.message.reply_text("Опишите ваш вопрос. Мы передадим его юристу.", reply_markup=main_markup)
        return TYPING
    await update.message.reply_text("Хотите задать свой вопрос?", reply_markup=main_markup)
    return TYPING

async def handle_faq_med(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Что такое F64?":
        await update.message.reply_text(
            "Это диагноз из МКБ-10, обозначающий гендерную дисфорию. В РФ он не даёт доступ к терапии или документам, "
            "но может быть нужен для операций за границей."
        )
    elif text == "Где делают операции?":
        await update.message.reply_text(
            "В РФ операции не проводятся. За границей их делают в Таиланде, Турции, Корее, Армении, Сербии и др. "
            "Обычно требуют F64 и курс ГТ от 6 месяцев."
        )
    elif text == "Как начать гормональную терапию?":
        await update.message.reply_text("Какую терапию вы ищете?", reply_markup=med_hormone_markup)
        return MED_HORMONE_TYPE
    else:
        await update.message.reply_text("Опишите ваш медицинский вопрос.", reply_markup=main_markup)
        return TYPING
