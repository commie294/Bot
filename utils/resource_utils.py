import json
import re
from datetime import datetime
from telegram import Bot
import logging

logger = logging.getLogger(__name__)

def load_resources():
    try:
        with open("data/resources.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_resource(title, description, link, category):
    resources = load_resources()
    resource = {
        "id": len(resources) + 1,
        "title": title,
        "description": description,
        "link": link,
        "category": category,
        "added_date": datetime.now().isoformat()
    }
    resources.append(resource)
    with open("data/resources.json", "w") as f:
        json.dump(resources, f, indent=2)
    return resource

async def fetch_resources_from_post(bot: Bot, channel: str, message_id: int):
    try:
        chat = await bot.get_chat(channel)
        message = await bot.forward_message(
            chat_id=chat.id,
            from_chat_id=chat.id,
            message_id=message_id
        )
        text = message.text or message.caption or ""
        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, text)
        resources = []
        for url in urls:
            resources.append({
                "id": len(resources) + 1,
                "title": url.split("/")[-1],
                "description": text[:100] + "..." if len(text) > 100 else text,
                "link": url,
                "category": "General",
                "added_date": datetime.now().isoformat()
            })
        return resources
    except Exception as e:
        logger.error(f"Ошибка при получении поста: {e}")
        return []

async def update_telegram_post(bot: Bot, channel: str, message_id: int):
    resources = load_resources()
    post_text = "*Список ресурсов:*\n\n"
    for res in resources:
        post_text += f"📚 *{res['title']}*\n{res['description']}\n🔗 {res['link']}\n\n"
    try:
        await bot.edit_message_text(
            chat_id=channel,
            message_id=message_id,
            text=post_text,
            parse_mode="MarkdownV2"
        )
        logger.info("Пост с ресурсами обновлён.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении поста: {e}")

async def approve_resource(resource_id: int):
    with open("data/pending_resources.json", "r") as f:
        pending = [json.loads(line) for line in f if line.strip()]
    resource = next((r for r in pending if r["id"] == resource_id), None)
    if resource:
        save_resource(
            resource["title"],
            resource["description"],
            resource["link"],
            resource["category"]
        )
        pending = [r for r in pending if r["id"] != resource_id]
        with open("data/pending_resources.json", "w") as f:
            for r in pending:
                json.dump(r, f)
                f.write("\n")
        return resource
    return None
