import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if
    # the message to the user fails.
    logger.error(f"Exception while handling an update:", exc_info=context.error)

    # Optionally, send a message to the user or the developer about the error.
    # For example:
    # await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

    # Optionally, you could also send the error details to a developer chat:
    # error_message = f"Произошла ошибка в боте:\n{context.error}"
    # await context.bot.send_message(chat_id=YOUR_DEVELOPER_CHAT_ID, text=error_message)
