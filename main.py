import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

CHOOSING, TYPING = range(2)
user_state = {}

main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Запрос о помощи")],
        [KeyboardButton("Предложить ресурс"), KeyboardButton("Сообщить о нарушении")],
        [KeyboardButton("Стать волонтёром")]
    ],
    resize_keyboard=True
)

help_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Срочная"), KeyboardButton("Юридическая")],
        [KeyboardButton("Психологическая"), KeyboardButton("Другая")]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Это бот @t64helper_bot.\nЧто вы хотите отправить?",
        reply_markup=main_keyboard
    )
    return CHOOSING

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "Запрос о помощи":
        user_state[user_id] = {"type": "help"}
        await update.message.reply_text("Пожалуйста, выберите вид помощи:", reply_markup=help_keyboard)
    elif text == "Предложить ресурс":
        user_state[user_id] = {"type": "resource"}
        await update.message.reply_text("Опишите, какой ресурс вы хотите предложить:")
    elif text == "Сообщить о нарушении":
        user_state[user_id] = {"type": "report"}
        await update.message.reply_text("Опишите ситуацию, о которой вы хотите сообщить:")
    elif text == "Стать волонтёром":
        user_state[user_id] = {"type": "volunteer"}
        await update.message.reply_text("Расскажите, как вы могли бы помочь:")
    else:
        await update.message.reply_text("Пожалуйста, выберите одну из доступных опций.")
        return CHOOSING

    return TYPING

async def help_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_state and user_state[user_id]["type"] == "help":
        user_state[user_id]["subtype"] = update.message.text
        await update.message.reply_text("Опишите вашу ситуацию, и мы передадим её модераторам.")
        return TYPING
    return CHOOSING

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or f"id:{user_id}"
    text = update.message.text

    if user_id not in user_state:
        await update.message.reply_text("Пожалуйста, выберите, что вы хотите отправить.", reply_markup=main_keyboard)
        return CHOOSING

    entry = user_state.pop(user_id)
    entry["text"] = text

    kind = entry["type"]
    message = f"Новое сообщение от @{username} (анонимно):\n"

    if kind == "help":
        subtype = entry.get("subtype", "не указано")
        message += f"Тип помощи: {subtype}\nСообщение:\n{text}"
    elif kind == "resource":
        message += f"Предложенный ресурс:\n{text}"
    elif kind == "report":
        message += f"Репорт о нарушении:\n{text}"
    elif kind == "volunteer":
        message += f"Желание стать волонтёром:\n{text}"

    await context.bot.send_message(chat_id=int(ADMIN_ID), text=message)
    await update.message.reply_text("Спасибо! Ваше сообщение отправлено модерации.", reply_markup=main_keyboard)

    return CHOOSING

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(Запрос о помощи|Предложить ресурс|Сообщить о нарушении|Стать волонтёром)$"), handle_choice),
                MessageHandler(filters.Regex("^(Срочная|Юридическая|Психологическая|Другая)$"), help_type_selected),
            ],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main
