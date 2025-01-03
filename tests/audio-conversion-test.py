import os
from config import setup_logging, load_config
from audio_conversion import convert_to_mp3
import logging

def test_audio_conversion():
    config = load_config()
    audio_folder = config.get('audio_folder')
    processed_folder = config.get('processed_folder')
    error_folder = config.get('error_folder')
    temp_folder = config.get('temp_folder')

    # Ensure all necessary folders exist
    for folder in [audio_folder, processed_folder, error_folder, temp_folder]:
        if not folder:
            logging.error(f"Folder path not specified in config: {folder}")
            return
        if not os.path.exists(folder):
            os.makedirs(folder)

    for filename in os.listdir(audio_folder):
        input_file = os.path.join(audio_folder, filename)
        if os.path.isfile(input_file):
            try:
                result_file = convert_to_mp3(input_file, processed_folder, error_folder, temp_folder)
                logging.info(f"Conversion result for {filename}: {result_file}")
                
                if os.path.exists(result_file):
                    logging.info(f"Output file created: {result_file}")
                else:
                    logging.error(f"Output file not created for {filename}")
            except Exception as e:
                logging.error(f"Conversion failed for {filename}: {e}")

if __name__ == "__main__":
    setup_logging()
    test_audio_conversion()
