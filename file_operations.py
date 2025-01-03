import os
import shutil
import subprocess
import json
import logging

def get_bitrate(input_file_path):
    try:
        result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', input_file_path], 
                                capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        for stream in data['streams']:
            if stream['codec_type'] == 'audio':
                return min(int(stream.get('bit_rate', '320000')) // 1000, 320)  # Convert to kbps and cap at 320
    except Exception as e:
        logging.warning(f"Failed to get bitrate for {input_file_path}: {e}")
    return 320  # Default to 320 kbps if unable to determine

def convert_to_mp3(input_file_path, output_file_path):
    try:
        bitrate = get_bitrate(input_file_path)
        subprocess.run(['ffmpeg', '-i', input_file_path, '-acodec', 'libmp3lame', '-b:a', f'{bitrate}k', 
                        '-map', '0:a', output_file_path], check=True, timeout=300)
    except subprocess.TimeoutExpired:
        logging.error(f"Conversion timed out for {input_file_path}")
        raise
    except subprocess.CalledProcessError as e:
        logging.error(f"Conversion failed for {input_file_path}: {e}")
        raise

def move_file(file_path, target_folder):
    os.makedirs(target_folder, exist_ok=True)
    target_path = os.path.join(target_folder, os.path.basename(file_path))
    if os.path.exists(target_path):
        existing_bitrate = get_bitrate(target_path)
        new_bitrate = get_bitrate(file_path)
        if new_bitrate > existing_bitrate:
            os.remove(target_path)
            shutil.move(file_path, target_path)
            logging.info(f"Replaced duplicate file {os.path.basename(file_path)} with higher bitrate version.")
        else:
            os.remove(file_path)
            logging.info(f"Duplicate file {os.path.basename(file_path)} discarded, existing file has higher or equal bitrate.")
    else:
        shutil.move(file_path, target_path)

def rename_file(file_path, metadata):
    track_number = metadata.get('track', 'Unknown').zfill(2)  # Ensure track number has leading zeros
    song_title = metadata.get('title', 'Unknown').replace('/', '_')  # Replace any invalid characters
    new_name = f"{track_number} - {song_title}.mp3"
    new_path = os.path.join(os.path.dirname(file_path), new_name)
    os.rename(file_path, new_path)
    return new_path

def is_audio_file(filename):
    return filename.endswith(('.wav', '.mp3', '.m4a', 'm4p', '.wma', '.flac', '.aac'))
