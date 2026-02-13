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
    """Fallback Single Screenshot (Fastest position)"""
    try:
        # Bahut shuruat ka time (30s) taaki kam data mein bhi mil jaye
        command = [
            'ffmpeg', '-ss', '30', 
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
    """Adaptive Screenshot Extraction (Optimized for 1080p Partial Files)"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    screenshots = []
    # Timestamps ko pass rakha hai (30s, 60s, 90s, 120s, 150s)
    # 2.47GB file ka 60-80MB download hone par itna video data mil jata hai
    time_points = ["30", "60", "90", "120", "150"]
    
    for i, ts in enumerate(time_points):
        out_file = os.path.join(folder_path, f"ss_{i}.jpg")
        
        # Agar SS pehle se hai toh dobara mat nikalo (Efficiency)
        if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
            screenshots.append(out_file)
            continue

        try:
            # IMPORTANT: -ss before -i is 'Input Seeking' (Instant & works on partial files)
            command = [
                'ffmpeg',
                '-ss', ts,
                '-err_detect', 'ignore_err',
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '4', # Thodi better quality
                out_file, '-y'
            ]
            # Fast processing ke liye timeout chota rakha hai
            subprocess.run(command, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
                screenshots.append(out_file)
        except:
            continue
            
    return screenshots
