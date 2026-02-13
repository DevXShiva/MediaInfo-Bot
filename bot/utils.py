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
            # Actual downloaded data dikhayenge
            actual_size = os.path.getsize(file_path)
            text_info += f"📦 **Fetched Data:** `{human_readable_size(actual_size)}` (Partial)\n"
            text_info += f"⏱️ **Total Duration:** `{track.other_duration[0] if track.other_duration else 'N/A'}`\n"
        
        elif track.track_type == "Video":
            text_info += f"\n📺 **Video Settings**\n"
            text_info += f"🔹 **Resolution:** `{track.width}x{track.height}`\n"
            text_info += f"🔹 **Codec:** `{track.format}`\n"
            text_info += f"🔹 **Frame Rate:** `{track.frame_rate} fps`\n"
            text_info += f"🔹 **Bit Depth:** `{track.bit_depth} bits`\n"

        elif track.track_type == "Audio":
            lang = track.other_language[0] if track.other_language else 'Unknown'
            text_info += f"\n🎵 **Audio ({lang})**\n"
            text_info += f"🔸 **Codec:** `{track.format}`\n"
            text_info += f"🔸 **Channels:** `{track.channel_s} ch`\n"
            
    return text_info

def take_screenshot(video_path, output_path):
    """Purana Single Screenshot Logic (Bina delete kiye - Optimized for speed)"""
    try:
        # Partial data ke liye -i pehle aur -ss baad mein faster hai
        command = [
            'ffmpeg', '-i', video_path, 
            '-ss', '00:01:30', # Direct 1.5 min par jump (credits skip)
            '-vframes', '1', '-q:v', '2', 
            output_path, '-y'
        ]
        subprocess.run(command, timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except:
        return False

def take_multiple_screenshots(video_path, folder_path):
    """Credits skip karke actual movie scenes nikalne ke liye"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    screenshots = []
    # Quality scenes ke liye timestamps (Starting ke 1-5 minutes ke beech)
    # Ye 50-70MB ke data mein aaram se mil jayenge
    time_points = ["00:01:30", "00:02:45", "00:04:00", "00:05:15", "00:06:30"]
    
    for i, ts in enumerate(time_points):
        out_file = os.path.join(folder_path, f"ss_{i}.jpg")
        try:
            # -i pehle use karne se partial file read error nahi deti
            command = [
                'ffmpeg',
                '-i', video_path,
                '-ss', ts,
                '-vframes', '1',
                '-q:v', '5', # High quality compression
                out_file, '-y'
            ]
            # 7 seconds ka timeout taaki bot phase na rahe
            subprocess.run(command, timeout=7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Khali files ko check karke skip karna
            if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
                screenshots.append(out_file)
        except:
            continue
            
    return screenshots
