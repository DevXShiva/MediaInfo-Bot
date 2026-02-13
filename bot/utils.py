import os
import subprocess
import math
from pymediainfo import MediaInfo

def human_readable_size(size, decimal_places=2):
    """Bytes ko MB/GB mein convert karne ke liye"""
    if not size:
        return "N/A"
    size = float(size)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

def get_mediainfo(file_path):
    """File ki detailed technical details nikalne ke liye"""
    info = MediaInfo.parse(file_path)
    text_info = "📊 **DETAILED MEDIA INFORMATION**\n\n"
    
    for track in info.tracks:
        if track.track_type == "General":
            text_info += f"📁 **File Name:** `{os.path.basename(file_path)}`\n"
            actual_size = os.path.getsize(file_path)
            text_info += f"📦 **Fetched Data:** `{human_readable_size(actual_size)}` (Partial)\n"
            text_info += f"⏱️ **Total Duration:** `{track.other_duration[0] if track.other_duration else 'N/A'}`\n"
        
        elif track.track_type == "Video":
            text_info += f"\n📺 **Video Settings**\n"
            text_info += f"🔹 **Resolution:** `{track.width}x{track.height}`\n"
            text_info += f"🔹 **Codec:** `{track.format}`\n"
            text_info += f"🔹 **Frame Rate:** `{track.frame_rate} fps`\n"

        elif track.track_type == "Audio":
            lang = track.other_language[0] if track.other_language else 'Unknown'
            text_info += f"\n🎵 **Audio ({lang})**\n"
            text_info += f"🔸 **Codec:** `{track.format}`\n"
            text_info += f"🔸 **Channels:** `{track.channel_s} ch`\n"
            
    return text_info

def take_screenshot(video_path, output_path):
    """Fallback Single Screenshot"""
    try:
        # Fast Seek (-ss before -i) is safer for partial files
        command = [
            'ffmpeg', '-ss', '60', 
            '-err_detect', 'ignore_err',
            '-i', video_path, 
            '-vframes', '1', '-q:v', '2', 
            output_path, '-y'
        ]
        subprocess.run(command, timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except:
        return False

def take_multiple_screenshots(video_path, folder_path):
    """Robust Screenshot Extraction for Partial Files"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    screenshots = []
    # Seconds mein timestamps (Best for Fast Seek)
    # 90s, 180s, 270s, 360s, 450s (1.5 min se 7.5 min tak)
    time_points = ["90", "180", "270", "360", "450"]
    
    for i, ts in enumerate(time_points):
        out_file = os.path.join(folder_path, f"ss_{i}.jpg")
        try:
            # -ss before -i (Fast Seek): Ye index dhoondne mein time waste nahi karta
            # -err_detect ignore_err: Ye partial file ke errors ignore karwa deta hai
            command = [
                'ffmpeg',
                '-ss', ts,
                '-err_detect', 'ignore_err',
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '5', 
                out_file, '-y'
            ]
            subprocess.run(command, timeout=8, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
                screenshots.append(out_file)
        except:
            continue
            
    return screenshots
