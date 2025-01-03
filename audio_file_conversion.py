import subprocess
import json
import logging
import os
import shutil

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

def convert_to_mp3(input_file_path, processed_folder, error_folder, temp_folder, original_folder):
    filename = os.path.basename(input_file_path)
    temp_output_path = os.path.join(temp_folder, f"{os.path.splitext(filename)[0]}.mp3")
    final_output_path = os.path.join(processed_folder, f"{os.path.splitext(filename)[0]}.mp3")

    # List of supported input formats
    supported_formats = ['.wav', '.m4a', '.m4p', '.aac', '.flac', '.ogg', '.wma']

    # Check if the input file is already an MP3
    if input_file_path.lower().endswith('.mp3'):
        logging.info(f"File {filename} is already an MP3. Moving to processed folder.")
        shutil.move(input_file_path, final_output_path)
        return final_output_path

    # Check if the input file is a supported format
    if not any(input_file_path.lower().endswith(fmt) for fmt in supported_formats):
        logging.warning(f"Unsupported file format: {filename}. Moving to error folder.")
        shutil.move(input_file_path, os.path.join(error_folder, filename))
        return None

    try:
        bitrate = get_bitrate(input_file_path)
        
        # For .m4p files, we need to remove DRM protection first
        if input_file_path.lower().endswith('.m4p'):
            temp_m4a = os.path.join(temp_folder, f"{os.path.splitext(filename)[0]}.m4a")
            subprocess.run(['ffmpeg', '-i', input_file_path, '-acodec', 'copy', temp_m4a], check=True, timeout=300)
            conversion_input = temp_m4a
        else:
            conversion_input = input_file_path

        # Convert to MP3
        subprocess.run(['ffmpeg', '-i', conversion_input, '-acodec', 'libmp3lame', '-b:a', f'{bitrate}k', 
                        '-map', '0:a', temp_output_path], check=True, timeout=300)
        
        # Move the converted file to the processed folder
        shutil.move(temp_output_path, final_output_path)
        
        # Move the original file to the original_files folder
        original_in_original_files = os.path.join(original_folder, filename)
        shutil.move(input_file_path, original_in_original_files)
        logging.info(f"Moved original file to {original_in_original_files}")
        
        logging.info(f"✅ Successfully converted {filename} to MP3 and moved original to original_files folder.")
        return final_output_path
    except Exception as e:
        logging.error(f"Conversion failed for {filename}: {e}. Moving to error folder.")
        shutil.move(input_file_path, os.path.join(error_folder, filename))
    finally:
        # Clean up temp files if they exist
        for temp_file in [temp_output_path, temp_m4a if 'temp_m4a' in locals() else None]:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
    
    return None
