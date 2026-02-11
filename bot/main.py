import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from bot.utils import get_mediainfo, take_screenshot

# Configuration (Render environment variables se lega)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Bot initialize karna
app = Client(
    "MediaInfoBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text(
        "👋 **Hello!**\n\nMujhe koi bhi Video ya Document file bhejo, "
        "main aapko uski **MediaInfo** aur ek **Screenshot** direct bhej dunga."
    )

@app.on_message(filters.video | filters.document)
async def process_video(client, message: Message):
    # Sirf video files ya video documents handle karne ke liye check
    if message.document and not message.document.mime_type.startswith("video/"):
        return

    status_msg = await message.reply_text("📥 **Downloading...**", quote=True)
    
    # Download path setup
    file_path = await message.download()
    
    try:
        await status_msg.edit_text("⚙️ **Processing Media Info...**")
        # 1. Media Info nikalna
        info_text = get_mediainfo(file_path)
        
        await status_msg.edit_text("📸 **Generating Screenshot...**")
        # 2. Screenshot nikalna
        screenshot_path = f"{file_path}.jpg"
        success = take_screenshot(file_path, screenshot_path)
        
        if success:
            # 3. Screenshot aur Info bhejna
            await message.reply_photo(
                photo=screenshot_path,
                caption=info_text,
                quote=True
            )
            os.remove(screenshot_path) # Screenshot delete karna
        else:
            # Agar screenshot fail ho jaye toh sirf text bhejna
            await message.reply_text(info_text, quote=True)
            
    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")
    
    finally:
        # 4. Cleanup: Downloaded file ko server se delete karna
        if os.path.exists(file_path):
            os.remove(file_path)
        await status_msg.delete()

# ... baaki code ...

app = Client(
    "MediaInfoBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Niche wala if block hata sakte hain ya rehne de sakte hain
if __name__ == "__main__":
    app.run()
