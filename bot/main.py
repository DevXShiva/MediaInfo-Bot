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
        "1. Credits skip karke quality screenshots nikalunga.\n"
        "2. 20-30 seconds mein processing complete hogi.\n"
        "3. Screenshots milte hi फालतू download stop kar dunga."
    )

@app.on_message(filters.video | filters.document)
async def process_video(client, message: Message):
    if message.document and not message.document.mime_type.startswith("video/"):
        return

    status_msg = await message.reply_text("⚡ **Analyzing Quality...**", quote=True)
    
    file_name = f"vid_{message.id}"
    file_path = os.path.join("downloads", file_name)
    ss_folder = os.path.join("downloads", f"ss_{message.id}")
    
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    screenshots = []
    try:
        # 1. SMART DYNAMIC DOWNLOAD
        await status_msg.edit_text("📥 **Fetching Quality Data...**")
        chunk_count = 0
        
        async for chunk in client.stream_media(message):
            with open(file_path, "ab") as f:
                f.write(chunk)
            chunk_count += 1
            
            # Skip first 35MB (Credits) and then start checking every 15MB
            if chunk_count > 35 and chunk_count % 15 == 0:
                await status_msg.edit_text(f"📸 **Generating Screenshots ({chunk_count}MB)...**")
                # Utils mein time points 2 min+ hone chahiye
                screenshots = take_multiple_screenshots(file_path, ss_folder)
                
                # Agar 4-5 screenshots mil gaye, toh bas!
                if len(screenshots) >= 4:
                    break
            
            # Max safety limit for very high bitrate files
            if chunk_count > 150: 
                break
        
        # 2. Final Info (Optional, faster result ke liye short rakha hai)
        await status_msg.edit_text("⚙️ **Finalizing...**")
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
            
            # Cleanup
            for s in screenshots:
                if os.path.exists(s): os.remove(s)
            if os.path.exists(ss_folder): os.rmdir(ss_folder)
            
        else:
            # Fallback
            screenshot_path = f"{file_path}.jpg"
            if take_screenshot(file_path, screenshot_path):
                await message.reply_photo(photo=screenshot_path, caption=info_text, quote=True)
                os.remove(screenshot_path)
            else:
                await message.reply_text("❌ Screenshot failed (Data missing).", quote=True)
            
    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        await status_msg.delete()

if __name__ == "__main__":
    app.run()
