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
        "👋 **Welcome!**\n\nMujhe koi bhi Video bhejo, main uske 5 screenshots aur media info nikal dunga.\n\n"
        "✅ **Feature:** 480p ho ya 1080p, ye adaptive downloading use karta hai."
    )

@app.on_message(filters.video | filters.document)
async def process_video(client, message: Message):
    if message.document and not message.document.mime_type.startswith("video/"):
        return

    status_msg = await message.reply_text("⚡ **Initializing Adaptive Scan...**", quote=True)
    
    file_name = f"vid_{message.id}"
    file_path = os.path.join("downloads", file_name)
    ss_folder = os.path.join("downloads", f"ss_{message.id}")
    
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    screenshots = []
    try:
        # 1. SMART DYNAMIC DOWNLOAD
        chunk_count = 0
        async for chunk in client.stream_media(message):
            with open(file_path, "ab") as f:
                f.write(chunk)
            chunk_count += 1
            
            if chunk_count % 15 == 0:
                # ERROR FIX: Try-Except block for MESSAGE_NOT_MODIFIED
                try:
                    await status_msg.edit_text(f"📥 **Scanning segments... ({chunk_count}MB)**")
                except Exception:
                    # Agar same text hai toh ignore karo aur aage badho
                    pass
                
                screenshots = take_multiple_screenshots(file_path, ss_folder)
                
                if len(screenshots) >= 5:
                    break
            
            if chunk_count > 150: # Max safety limit
                break
        
        # 2. Finalizing
        try:
            await status_msg.edit_text("⚙️ **Generating Final Report...**")
        except Exception:
            pass

        info_text = get_mediainfo(file_path)
        
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
            await message.reply_text(f"❌ **Error:** Screenshots not found.\n\n{info_text}", quote=True)
            
    except Exception as e:
        # Check if error is not just a Telegram UI error
        if "MESSAGE_NOT_MODIFIED" not in str(e):
            await message.reply_text(f"❌ **System Error:** `{e}`")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        try:
            await status_msg.delete()
        except Exception:
            pass

if __name__ == "__main__":
    app.run()

