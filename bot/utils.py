import os
import subprocess
import math
from pymediainfo import MediaInfo

def human_readable_size(size, decimal_places=2):
    """Bytes ko MB/GB mein convert karne ke liye"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

def get_mediainfo(file_path):
    """File ki technical details nikalne ke liye"""
    info = MediaInfo.parse(file_path)
    text_info = "📊 **Media Information**\n\n"
    
    for track in info.tracks:
        if track.track_type == "General":
            text_info += f"📁 **File Name:** `{os.path.basename(file_path)}`\n"
            text_info += f"📦 **Size:** `{human_readable_size(track.file_size)}`\n"
            text_info += f"⏱️ **Duration:** `{track.other_duration[0] if track.other_duration else 'N/A'}`\n"
        
        elif track.track_type == "Video":
            text_info += f"\n📺 **Video Settings**\n"
            text_info += f"🔹 **Resolution:** `{track.width}x{track.height}`\n"
            text_info += f"🔹 **Codec:** `{track.format}`\n"
            text_info += f"🔹 **Bitrate:** `{track.other_overall_bit_rate[0] if track.other_overall_bit_rate else 'N/A'}`\n"
            text_info += f"🔹 **Frame Rate:** `{track.frame_rate} fps`\n"

        elif track.track_type == "Audio":
            text_info += f"\n🎵 **Audio Settings**\n"
            text_info += f"🔸 **Language:** `{track.other_language[0] if track.other_language else 'N/A'}`\n"
            text_info += f"🔸 **Codec:** `{track.format}`\n"
            text_info += f"🔸 **Channels:** `{track.channel_s}`\n"
            
    return text_info

def take_screenshot(video_path, output_path):
    """FFmpeg use karke video ke center se ek screenshot lena"""
    # Video ki duration nikalna
    info = MediaInfo.parse(video_path)
    duration = 0
    for track in info.tracks:
        if track.track_type == "General":
            duration = float(track.duration) / 1000  # seconds mein
            break
    
    # Video ke beech (mid-point) se screenshot lena
    time_to_capture = duration / 2
    
    try:
        command = [
            'ffmpeg', '-ss', str(time_to_capture),
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '2',
            output_path,
            '-y' # Purani file overwrite karne ke liye
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return False
