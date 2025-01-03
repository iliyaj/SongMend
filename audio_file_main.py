import os
import logging
from config import setup_logging, get_folders
from audio_file_conversion import convert_to_mp3
from audio_file_error_check import detect_corruption

def main():
    setup_logging()
    folders = get_folders()

    # Step 1: Check for corrupted files and move video files
    detect_corruption(
        folders['audio_folder'],
        folders['error_folder'],
        folders['video_folder']
    )

    # Step 2: Convert audio files to MP3
    for filename in os.listdir(folders['audio_folder']):
        file_path = os.path.join(folders['audio_folder'], filename)
        if os.path.isfile(file_path):
            convert_to_mp3(
                file_path,
                folders['processed_folder'],
                folders['error_folder'],
                folders['temp_folder'],
                folders['original_folder']
            )

    logging.info("Audio file processing completed.")

    # Recheck for corrupted files after conversion
    detect_corruption(
        folders['processed_folder'],
        folders['error_folder'],
        folders['video_folder']
    )

if __name__ == "__main__":
    main()
