import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from bot.utils import get_mediainfo, take_screenshot, take_multiple_screenshots

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
        "👋 **Hello!**\n\nMujhe koi bhi Video ya Document file bhejo.\n\n"
        "⚡ **Main Kya Karunga:**\n"
        "1. Start ke 20MB download karke fast info nikalunga.\n"
        "2. Video se 5 alag-alag screenshots generate karunga.\n"
        "3. Bina kisi external link ke direct Album bhejunga."
    )

@app.on_message(filters.video | filters.document)
async def process_video(client, message: Message):
    # Sirf video files ya video documents handle karne ke liye check
    if message.document and not message.document.mime_type.startswith("video/"):
        return

    status_msg = await message.reply_text("⚡ **Fast Processing...**", quote=True)
    
    # Download path setup
    file_name = f"vid_{message.id}"
    file_path = os.path.join("downloads", file_name)
    ss_folder = os.path.join("downloads", f"ss_{message.id}")
    
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    try:
        # 1. PARTIAL DOWNLOAD (Sirf 25MB chunks tak download karega)
        await status_msg.edit_text("📥 **Partial Downloading (Fast)...**")
        count = 0
        async for chunk in client.stream_media(message):
            with open(file_path, "ab") as f:
                f.write(chunk)
            count += 1
            if count > 25: # Lagbhag 25MB data (enough for start screenshots & info)
                break
        
        # 2. Media Info nikalna
        await status_msg.edit_text("⚙️ **Extracting Media Info...**")
        info_text = get_mediainfo(file_path)
        
        # 3. Multiple Screenshots nikalna
        await status_msg.edit_text("📸 **Generating 5 Screenshots...**")
        screenshots = take_multiple_screenshots(file_path, ss_folder)
        
        if screenshots:
            # Media Group (Album) taiyar karna
            media_group = []
            for i, ss_path in enumerate(screenshots):
                media_group.append(
                    InputMediaPhoto(
                        media=ss_path, 
                        caption=info_text if i == 0 else "" # Pehle photo par info dikhegi
                    )
                )
            
            # 4. Direct Telegram Album bhejna
            await message.reply_media_group(media=media_group, quote=True)
            
            # Cleanup Screenshots
            for s in screenshots:
                if os.path.exists(s): os.remove(s)
            if os.path.exists(ss_folder): os.rmdir(ss_folder)
            
        else:
            # Agar multiple fail ho jaye toh purana single screenshot try karna (Fallback)
            screenshot_path = f"{file_path}.jpg"
            if take_screenshot(file_path, screenshot_path):
                await message.reply_photo(photo=screenshot_path, caption=info_text, quote=True)
                os.remove(screenshot_path)
            else:
                await message.reply_text(info_text, quote=True)
            
    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")
    
    finally:
        # 5. Cleanup: Downloaded partial file delete karna
        if os.path.exists(file_path):
            os.remove(file_path)
        await status_msg.delete()

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
