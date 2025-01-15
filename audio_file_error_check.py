import os
import subprocess
import logging
import shutil
import json

# 1. Define project root relative to the script's location
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # This will correctly go up two levels, into song-recover folder
log_folder = os.path.join(project_root, 'logs')
log_file_path = os.path.join(log_folder, 'audio_file_processing_log.txt')

# Ensure log folder exists
os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def move_file(file_path, destination_folder):
    try:
        os.makedirs(destination_folder, exist_ok=True)
        destination_path = os.path.join(destination_folder, os.path.basename(file_path))
        shutil.move(file_path, destination_path)
        logging.info(f"✅ Moved file {file_path} to {destination_path}")
        print(f"✅ Moved file {file_path} to {destination_path}")
    except Exception as e:
        logging.error(f"❌ Failed to move file {file_path} to {destination_folder}: {str(e)}")
        print(f"❌ Failed to move file {file_path} to {destination_folder}: {str(e)}")

def check_audio_file(file_path):
    # First, try to get file info with increased analyzeduration and probesize
    probe_command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        '-analyzeduration', '100M',
        '-probesize', '100M',
        file_path
    ]

    try:
        probe_output = subprocess.check_output(probe_command, stderr=subprocess.STDOUT)
        file_info = json.loads(probe_output)
        
        # Check if we have valid audio stream information
        if 'streams' in file_info:
            for stream in file_info['streams']:
                if stream['codec_type'] == 'audio':
                    if 'channels' in stream and stream['channels'] > 0:
                        logging.info(f"✅ File appears valid: {file_path}")
                        return True
        
        logging.warning(f"⚠️ File seems corrupt (no valid audio stream): {file_path}")
        return False

    except subprocess.CalledProcessError:
        logging.error(f"❌ FFprobe failed to analyze the file: {file_path}")
        return False

    # If FFprobe doesn't give conclusive results, try playing a small portion of the file
    play_command = [
        'ffplay',
        '-v', 'error',
        '-t', '1',  # Try to play only the first second
        '-autoexit',
        '-nodisp',
        file_path
    ]

    try:
        subprocess.run(play_command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        logging.info(f"✅ File played successfully: {file_path}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ File failed to play: {file_path}")
        logging.error(f"❌ Error: {e.stderr.decode('utf-8')}")
        return False

def is_video_file(filename):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    return any(filename.lower().endswith(ext) for ext in video_extensions)

def detect_corruption(input_folder, error_folder, video_folder):
    for filename in os.listdir(input_folder):
        input_file_path = os.path.join(input_folder, filename)
        logging.info(f"ℹ️ Checking file: {input_file_path}")
        print(f"ℹ️ Checking file: {input_file_path}")

        if is_video_file(filename):
            move_file(input_file_path, video_folder)
            continue

        if filename.endswith(('.mp3', '.wma', '.m4a', '.m4p', '.wav')):
            if not check_audio_file(input_file_path):
                move_file(input_file_path, error_folder)
            else:
                logging.info(f"✅ File passed all checks: {input_file_path}")
                print(f"✅ File passed all checks: {input_file_path}")

if __name__ == "__main__":
    # 2. Define paths for testing relative to the project root
    input_folder = os.path.join(project_root, 'input_files', 'audio_files')
    error_folder = os.path.join(project_root, 'input_files', 'error_files')
    video_folder = os.path.join(project_root, 'input_files', 'video_files')
    
    detect_corruption(input_folder, error_folder, video_folder)