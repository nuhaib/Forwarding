import os
import asyncio
import logging
import re
from telethon import TelegramClient, events, functions, types
from telethon.errors import ChatAdminRequiredError

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Load API credentials
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

# Ensure credentials are set
if not api_id or not api_hash:
    raise ValueError("Missing API credentials. Set TELEGRAM_API_ID and TELEGRAM_API_HASH as environment variables.")

api_id = int(api_id)  # Convert API ID to integer

# Source & Target Channels (Script 2)
source_channel_script2 = [-1001880177414]  # Replace with actual source channel(s) for Script 2
target_channels_script2 = [-1002424739473]  # Replace with actual target channels

# URL Replacement Setting (applies to all messages)
custom_url = "https://tc9987.cc/register?invite_code=0788812949052"  # Replace with desired URL

# Initialize Telegram client
client = TelegramClient('script2_session', api_id, api_hash, flood_sleep_threshold=10)

def replace_urls(text):
    """Replaces any URL in the text with a custom URL."""
    if not text:
        return text
    url_pattern = re.compile(r'https?://\S+')
    return url_pattern.sub(custom_url, text)

@client.on(events.NewMessage(chats=source_channel_script2))
async def forward_messages(event):
    """Forward messages only to Script 2's assigned target channels, with URL replacement."""
    msg = event.message
    raw_text = msg.raw_text or ""
    processed_text = replace_urls(raw_text)  # Replace URLs in text
    media = msg.media if msg.media else None
    entities = msg.entities  # Preserve formatting
    buttons = msg.reply_markup  # Preserve buttons

    tasks = []
    for channel_id in target_channels_script2:
        tasks.append(send_message(channel_id, processed_text, media, entities, buttons))

    await asyncio.gather(*tasks)

async def send_message(channel_id, text, media, entities, buttons):
    """Send messages while keeping formatting, media, and buttons intact."""
    try:
        await client.send_message(
            entity=channel_id,
            message=text,
            file=media if media else None,
            link_preview=True,
            buttons=buttons,
            formatting_entities=entities
        )
    except ChatAdminRequiredError:
        logger.error(f"Bot is not an admin in {channel_id}")
    except Exception as e:
        logger.error(f"Failed to send message to {channel_id}: {e}")

async def main():
    """Start the Telegram client."""
    print("Script 2 Forwarder is running...")
    await client.start()
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
