from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from utils.message_utils import load_channels
from utils.resource_utils import load_resources
from utils.constants import BotState
from bot_responses import MESSAGE_SENT_SUCCESS, BACK_TO_MAIN_MENU
from keyboards import MAIN_MENU_BUTTONS, BACK_BUTTON, FINISH_MENU_KEYBOARD
import json
import logging

logger = logging.getLogger(__name__)

async def resource_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    step = context.user_data.get("resource_step")
    user_text = update.message.text
    if user_text == BACK_BUTTON:
        context.user_data.clear()
        await update.message.reply_text(
            BACK_TO_MAIN_MENU,
            reply_markup=MAIN_MENU_BUTTONS,
            parse_mode="MarkdownV2"
        )
        return BotState.MAIN_MENU
    if step == "title":
        context.user_data["resource_title"] = user_text
        context.user_data["resource_step"] = "description"
        await update.message.reply_text(
            escape_markdown("Введите описание ресурса:", version=2),
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            parse_mode="MarkdownV2"
        )
        return BotState.RESOURCE_PROPOSAL
    elif step == "description":
        context.user_data["resource_description"] = user_text
        context.user_data["resource_step"] = "link"
        await update.message.reply_text(
            escape_markdown("Введите ссылку на ресурс:", version=2),
            reply_markup=ReplyKeyboardMarkup([[BACK_BUTTON]], resize_keyboard=True),
            parse_mode="MarkdownV2"
        )
        return BotState.RESOURCE_PROPOSAL
    elif step == "link":
        resource = {
            "id": len(load_resources()) + 1,
            "title": context.user_data["resource_title"],
            "description": context.user_data["resource_description"],
            "link": user_text,
            "category": "General",
            "user_id": update.effective_user.id
        }
        pending_resources = []
        try:
            with open("data/pending_resources.json", "r") as f:
                for line in f:
                    if line.strip():  # Проверка на пустую строку
                        pending_resources.append(json.loads(line.strip()))
        except FileNotFoundError:
            pass
        pending_resources.append(resource)
        try:
            with open("data/pending_resources.json", "w") as f:
                for res in pending_resources:
                    json.dump(res, f)
                    f.write("\n")
            channels = load_channels()
            # Экранируем пользовательский ввод
            title = escape_markdown(resource["title"], version=2)
            description = escape_markdown(resource["description"], version=2)
            link = escape_markdown(resource["link"], version=2)
            await context.bot.send_message(
                chat_id=channels["t64_admin"],
                text=f"*Новый ресурс на модерацию:*\n\n*Название:* {title}\n*Описание:* {description}\n*Ссылка:* {link}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_resource_{resource['id']}")],
                    [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_resource_{resource['id']}")]
                ]),
                parse_mode="MarkdownV2"
            )
            await update.message.reply_text(
                MESSAGE_SENT_SUCCESS,
                reply_markup=FINISH_MENU_KEYBOARD,
                parse_mode="MarkdownV2"
            )
            context.user_data.clear()
            return BotState.MAIN_MENU
        except Exception as e:
            logger.error(f"Ошибка при записи в pending_resources.json или отправке уведомления: {e}", exc_info=True)
            await update.message.reply_text(
                escape_markdown("Произошла ошибка при обработке вашего ресурса. Пожалуйста, попробуйте позже.", version=2),
                reply_markup=MAIN_MENU_BUTTONS,
                parse_mode="MarkdownV2"
            )
            return BotState.MAIN_MENU
    return BotState.RESOURCE_PROPOSAL

async def list_resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    resources = load_resources()
    if not resources:
        await update.message.reply_text(
            escape_markdown("Ресурсы не найдены.", version=2),
            reply_markup=MAIN_MENU_BUTTONS,
            parse_mode="MarkdownV2"
        )
        return BotState.MAIN_MENU
    message = "*Доступные ресурсы:*\n\n"
    for res in resources:
        title = escape_markdown(res["title"], version=2)
        description = escape_markdown(res["description"], version=2)
        link = escape_markdown(res["link"], version=2)
        message += f"📚 *{title}*\n{description}\n🔗 {link}\n\n"
    await update.message.reply_text(
        message,
        reply_markup=MAIN_MENU_BUTTONS,
        parse_mode="MarkdownV2"
    )
    return BotState.MAIN_MENU
