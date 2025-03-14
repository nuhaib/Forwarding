import os
import asyncio
import logging
import re
from telethon import TelegramClient, events, functions, types
from telethon.errors import ChatAdminRequiredError

# Configure logging (only logs errors to reduce RAM usage)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Load API credentials from environment variables
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

# Ensure credentials are set
if not api_id or not api_hash:
    raise ValueError("Missing API credentials. Set TELEGRAM_API_ID and TELEGRAM_API_HASH as environment variables.")

api_id = int(api_id)  # Convert API ID to integer

# Source & Target Channels
source_channel_id = -1001880177414  # Replace with actual source channel
target_channels = [-1002424739473]  # Target channels

# URL Replacement Settings
custom_url = "https://tc9987.cc/register?invite_code=0788812949052"  # URL to replace with
specific_channels = {-1002094341716}  # Channels where URLs should be removed

# Initialize Telegram client with optimized flood protection
client = TelegramClient('script2_session', api_id, api_hash, flood_sleep_threshold=10)
# Store admin channels to avoid redundant API calls
admin_channels = set()
failed_channels = set()  # Track channels where sending fails

async def get_admin_channels():
    """Fetches all channels where the bot is an admin to prevent unnecessary API calls."""
    global admin_channels
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_channel:
            try:
                permissions = await client(functions.channels.GetParticipantRequest(dialog.id, 'me'))
                if isinstance(permissions.participant, types.ChannelParticipantAdmin):
                    admin_channels.add(dialog.id)
            except Exception:
                pass  # Ignore errors for inaccessible channels

def process_text(text, target_id):
    """Modifies message based on forwarding rules (replaces or removes URLs)."""
    if not text:
        return text
    
    is_specific = target_id in specific_channels
    url_pattern = re.compile(r'https?://\S+')

    if is_specific:
        # Remove URLs completely for specific channels
        text = url_pattern.sub('', text)
    else:
        # Replace URLs with a custom one for general channels
        text = url_pattern.sub(custom_url, text)

    return text.strip()

source_channel_script2 = [-1001880177414]  # Replace with Script 2's source channels

@client.on(events.NewMessage(chats=source_channel_script2))
async def forward_messages(event):
    """Handles new messages and forwards them while keeping formatting, media, buttons, and replacing URLs."""
    global admin_channels

    msg = event.message
    raw_text = msg.raw_text or ""  # Use raw_text to preserve formatting
    media = msg.media if msg.media else None
    entities = msg.entities  # Extract formatting (bold, italics, links, etc.)
    buttons = msg.reply_markup  # Extract inline buttons

    tasks = []
    for channel_id in admin_channels:
        if channel_id in failed_channels:
            continue  # Skip failed channels
        
        processed_text = process_text(raw_text, channel_id)  # Modify text for each channel
        tasks.append(send_message(channel_id, processed_text, media, entities, buttons))

    await asyncio.gather(*tasks)  # Send messages in parallel

async def send_message(channel_id, text, media, entities, buttons):
    """Sends message asynchronously while keeping original formatting, media, and buttons."""
    try:
        await client.send_message(
            entity=channel_id,
            message=text,
            file=media if media else None,
            link_preview=True,  # Keep link previews like in the first script
            buttons=buttons,  # Keep inline buttons
            formatting_entities=entities  # Preserve bold, italics, etc.
        )
    except ChatAdminRequiredError:
        failed_channels.add(channel_id)  # Avoid retrying failed channels
    except Exception as e:
        logger.error(f"Failed to send message to {channel_id}: {e}")

async def main():
    """Startup function to initialize everything."""
    await get_admin_channels()  # Fetch admin channels once at startup
    print("Forwarder is running...")

# Run the bot using an event loop
with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
