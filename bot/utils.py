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
            text_info += f"📦 **Size:** `{human_readable_size(track.file_size)}`\n"
            text_info += f"⏱️ **Duration:** `{track.other_duration[0] if track.other_duration else 'N/A'}`\n"
            text_info += f"🎞️ **Format:** `{track.format}`\n"
        
        elif track.track_type == "Video":
            text_info += f"\n📺 **Video Settings**\n"
            text_info += f"🔹 **Resolution:** `{track.width}x{track.height}`\n"
            text_info += f"🔹 **Codec:** `{track.format} ({track.codec_id})`\n"
            text_info += f"🔹 **Bitrate:** `{track.other_overall_bit_rate[0] if track.other_overall_bit_rate else 'N/A'}`\n"
            text_info += f"🔹 **Frame Rate:** `{track.frame_rate} fps`\n"
            text_info += f"🔹 **Bit Depth:** `{track.bit_depth} bits`\n"

        elif track.track_type == "Audio":
            lang = track.other_language[0] if track.other_language else 'Unknown'
            text_info += f"\n🎵 **Audio ({lang})**\n"
            text_info += f"🔸 **Codec:** `{track.format}`\n"
            text_info += f"🔸 **Channels:** `{track.channel_s} ch`\n"
            text_info += f"🔸 **Bitrate:** `{track.other_bit_rate[0] if track.other_bit_rate else 'N/A'}`\n"
            
    return text_info

def take_screenshot(video_path, output_path):
    """Purana Single Screenshot Logic (Bina delete kiye)"""
    info = MediaInfo.parse(video_path)
    duration = 0
    for track in info.tracks:
        if track.track_type == "General":
            duration = float(track.duration) / 1000 if track.duration else 0
            break
    
    time_to_capture = duration / 2
    try:
        command = [
            'ffmpeg', '-ss', str(time_to_capture),
            '-i', video_path, '-vframes', '1', '-q:v', '2', output_path, '-y'
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def take_multiple_screenshots(video_path, folder_path):
    """Fast Processing ke liye multiple screenshots logic (Naya Feature)"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    screenshots = []
    # Hum 10s, 2m, 4m, 6m, aur 8m par screenshots lenge (Partial download ke liye best)
    time_points = ["00:00:10", "00:02:00", "00:04:00", "00:06:00", "00:08:00"]
    
    for i, ts in enumerate(time_points):
        out_file = os.path.join(folder_path, f"ss_{i}.jpg")
        try:
            # -timeout use kiya hai taki agar data na ho to FFmpeg atak na jaye
            command = [
                'ffmpeg', '-ss', ts,
                '-i', video_path,
                '-vframes', '1', '-q:v', '4', 
                out_file, '-y'
            ]
            # 5 seconds ka timeout har screenshot ke liye
            subprocess.run(command, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(out_file):
                screenshots.append(out_file)
        except Exception as e:
            print(f"Error at {ts}: {e}")
            continue
            
    return screenshots
