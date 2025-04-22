import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

HELP_CATEGORIES = {
    "urgent": "Срочная помощь",
    "legal": "Юридическая помощь",
    "psych": "Психологическая поддержка",
    "medical": "Медицинская помощь",
    "basic": "Финансовая помощь и жильё",
    "other": "Другое"
}

HELP_RESPONSES = {
    "urgent": "*Срочная помощь*\n\nЕсли вы находитесь в опасной или кризисной ситуации — не оставайтесь в этом одни. "
              "Вы можете описать, что происходит, даже если не уверены, что именно вам нужно.\n\n"
              "Мы постараемся найти инициативу, человека или организацию, которые смогут отреагировать быстро. "
              "Всё, что вы напишете, будет обработано с вниманием.",
    "legal": "*Юридическая помощь*\n\nЕсли вы столкнулись с дискриминацией, угрозами, отказом в услугах, "
             "проблемами с документами — опишите ситуацию.\n\n"
             "*Важно:* юридическая помощь не проводится анонимно — ID будет учтён. "
             "Анонимно можно задать общий вопрос.",
    "psych": "*Психологическая поддержка*\n\nВы можете:\n"
             "— просто *выговориться* и оставить анонимное сообщение,\n"
             "— или *запросить помощь психолога*.\n\n"
             "Опишите, что вам нужно. Всё — по вашему желанию.",
    "medical": "*Медицинская помощь*\n\nЕсли вам нужна информация о гормональной терапии, т-френдли врачах, операциях "
               "или безопасном доступе к медицине — напишите, что вас интересует.",
    "basic": "*Финансовая помощь и жильё*\n\nЕсли вы без дохода, жилья, под угрозой выселения или переезда — "
             "опишите ситуацию. Мы постараемся найти ресурсы или инициативы.",
    "other": "*Другое*\n\nЕсли ваш запрос не относится к основным категориям — просто опишите, с чем вы столкнулись."
}

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=key)] for key, name in HELP_CATEGORIES.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Здравствуйте. Выберите категорию, по которой хотите обратиться за помощью:",
        reply_markup=reply_markup
    )

async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    user_states[query.from_user.id] = category

    text = HELP_RESPONSES.get(category, "Опишите, чем мы можем помочь.")
    keyboard = [[InlineKeyboardButton("↩️ Вернуться в меню", callback_data="restart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return await start(query, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    category = user_states.get(user_id, "не выбрана")
    username = update.message.from_user.username or "без username"

    admin_message = (
        f"Новое сообщение от @{username} (ID: {user_id})\n"
        f"Категория: {HELP_CATEGORIES.get(category, 'не указана')}\n\n{text}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)

    await update.message.reply_text(
        "Спасибо! Ваше сообщение передано. Чтобы обратиться снова — введите /start."
    )
    user_states.pop(user_id, None)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_category_selection))
    app.add_handler(CallbackQueryHandler(handle_restart, pattern="^restart$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
