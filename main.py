import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# ID админа
ADMIN_ID = 1835516062

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это @t64helper_bot — бот для приёма анонимных сообщений и ресурсов для трансгендерного сообщества СНГ.\n\n"
        "Ты можешь:\n"
