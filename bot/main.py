import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from bot.utils import get_mediainfo, take_screenshot, take_multiple_screenshots

# Configuration
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

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
        "1. Dynamic downloading se fast media info nikalunga.\n"
        "2. Screenshots milte hi download stop kar dunga (Time-Saving).\n"
        "3. Bina kisi external link ke direct Album bhejunga."
    )

@app.on_message(filters.video | filters.document)
async def process_video(client, message: Message):
    if message.document and not message.document.mime_type.startswith("video/"):
        return

    status_msg = await message.reply_text("⚡ **Analyzing Media...**", quote=True)
    
    file_name = f"vid_{message.id}"
    file_path = os.path.join("downloads", file_name)
    ss_folder = os.path.join("downloads", f"ss_{message.id}")
    
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    screenshots = []
    try:
        # 1. DYNAMIC CHUNK DOWNLOAD
        await status_msg.edit_text("📥 **Smart Fetching (0MB)...**")
        chunk_count = 0
        
        async for chunk in client.stream_media(message):
            with open(file_path, "ab") as f:
                f.write(chunk)
            chunk_count += 1
            
            # Har 15 chunks (~15-20MB) par check karo ki screenshots nikal rahe hain ya nahi
            if chunk_count % 15 == 0:
                await status_msg.edit_text(f"📸 **Checking for Screenshots ({chunk_count}MB)...**")
                screenshots = take_multiple_screenshots(file_path, ss_folder)
                
                # Agar 5 screenshots mil gaye, toh aage download karne ki zaroorat nahi
                if len(screenshots) >= 5:
                    break
            
            # Max safety limit (120MB) taaki Render crash na ho agar file bahut hi heavy ho
            if chunk_count > 120:
                break
        
        # 2. Final Media Info
        await status_msg.edit_text("⚙️ **Finalizing Media Info...**")
        info_text = get_mediainfo(file_path)
        
        # 3. Agar loop ke andar screenshots nahi mile (bahut heavy file), toh ek last try
        if not screenshots:
            screenshots = take_multiple_screenshots(file_path, ss_folder)
        
        if screenshots:
            media_group = []
            for i, ss_path in enumerate(screenshots):
                media_group.append(
                    InputMediaPhoto(
                        media=ss_path, 
                        caption=info_text if i == 0 else ""
                    )
                )
            
            await message.reply_media_group(media=media_group, quote=True)
            
            # Cleanup Screenshots
            for s in screenshots:
                if os.path.exists(s): os.remove(s)
            if os.path.exists(ss_folder): os.rmdir(ss_folder)
            
        else:
            # Fallback to single screenshot if multiple fails
            screenshot_path = f"{file_path}.jpg"
            if take_screenshot(file_path, screenshot_path):
                await message.reply_photo(photo=screenshot_path, caption=info_text, quote=True)
                os.remove(screenshot_path)
            else:
                await message.reply_text(info_text, quote=True)
            
    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        await status_msg.delete()

if __name__ == "__main__":
    app.run()
