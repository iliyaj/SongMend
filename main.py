import os
import logging
from pydub import AudioSegment
from metadata_shazam_api import detect_song, get_song_details, extract_song_id, convert_audio_to_shazam_format
from metadata_extractor import extract_metadata, clean_metadata, validate_metadata
from metadata_updater import update_metadata, get_current_metadata, compare_metadata
from file_operations import move_file, rename_file, is_audio_file
from config import setup_logging, load_config, get_api_key, get_folders

# Setup logging
setup_logging()

def process_audio_file(file_path, api_key, success_folder, failed_folder):
    try:
        # Convert audio to Shazam format
        raw_data = convert_audio_to_shazam_format(file_path)

        # Detect song using Shazam API
        detection_result = detect_song(raw_data, api_key)
        if not detection_result:
            logging.warning(f"Song detection failed for {file_path}")
            move_file(file_path, failed_folder)
            return False

        # Extract song ID
        song_id = extract_song_id(detection_result)
        if not song_id:
            logging.warning(f"Failed to extract song ID for {file_path}")
            move_file(file_path, failed_folder)
            return False

        # Get detailed song information
        song_details = get_song_details(song_id, api_key)
        if not song_details:
            logging.warning(f"Failed to get song details for {file_path}")
            move_file(file_path, failed_folder)
            return False

        # Extract metadata
        metadata = extract_metadata(detection_result, song_details)
        metadata = clean_metadata(metadata)

        if not validate_metadata(metadata):
            logging.warning(f"Invalid metadata for {file_path}")
            move_file(file_path, failed_folder)
            return False

        # Get current metadata
        current_metadata = get_current_metadata(file_path)

        # Compare and update metadata
        changes = compare_metadata(current_metadata, metadata)
        if changes:
            logging.info(f"Metadata changes for {file_path}: {changes}")
            if update_metadata(file_path, metadata):
                logging.info(f"Successfully updated metadata for {file_path}")

                # Rename file based on new metadata
                new_file_path = rename_file(file_path, metadata)

                # Move the file to the success folder
                move_file(new_file_path, success_folder)
                return True
            else:
                logging.error(f"Failed to update metadata for {file_path}")
                move_file(file_path, failed_folder)
                return False
        else:
            logging.info(f"No metadata changes needed for {file_path}")
            move_file(file_path, success_folder)
            return True

    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        move_file(file_path, failed_folder)
        return False


def main():
    config = load_config()
    api_key = get_api_key()
    folders = get_folders()

    input_folder = folders['audio_folder']
    success_folder = folders['success_folder']
    failed_folder = folders['failed_folder']

    # Ensure necessary folders exist
    for folder in [input_folder, success_folder, failed_folder]:
        os.makedirs(folder, exist_ok=True)

    # Get list of files first
    audio_files = [f for f in os.listdir(input_folder) if is_audio_file(f)]
    total_files = len(audio_files)

    print(f"Found {total_files} audio files to process")

    # Use tqdm to create a progress bar
    from tqdm import tqdm
    for filename in tqdm(audio_files, desc="Processing audio files", unit="file"):
        if is_audio_file(filename):
            file_path = os.path.join(input_folder, filename)
def main():
    config = load_config()
    api_key = get_api_key()
    folders = get_folders()

    input_folder = folders['audio_folder']
    success_folder = folders['success_folder']
    failed_folder = folders['failed_folder']

    # Ensure necessary folders exist
    for folder in [input_folder, success_folder, failed_folder]:
        os.makedirs(folder, exist_ok=True)

    # Get list of files and create full paths first
    audio_files = []
    for filename in os.listdir(input_folder):
        if is_audio_file(filename):
            file_path = os.path.join(input_folder, filename)
            # Only add files that actually exist and are accessible
            if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                audio_files.append(file_path)

    total_files = len(audio_files)
    print(f"Found {total_files} audio files to process")

    # Process files with progress bar
    from tqdm import tqdm
    for file_path in tqdm(audio_files, desc="Processing audio files", unit="file"):
        try:
            # Verify file still exists and is accessible before processing
            if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                process_audio_file(file_path, api_key, success_folder, failed_folder)
            else:
                logging.warning(f"File no longer accessible: {file_path}")
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            continue

if __name__ == "__main__":
    main()

