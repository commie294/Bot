import pytest
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes
from handlers.main_menu import main_menu
from utils.constants import BotState

@pytest.mark.asyncio
async def test_main_menu_help_choice():
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            chat=Chat(id=123, type="private"),
            from_user=User(id=123, is_bot=False, first_name="Test"),
            text="🆘 Попросить о помощи"
        )
    )
    context = ContextTypes.DEFAULT_TYPE()
    result = await main_menu(update, context)
    assert result == BotState.HELP_MENU
