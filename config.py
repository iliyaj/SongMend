import os
import json
import logging

# Get the directory of the current file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def load_config():
    # Use BASE_DIR to construct the path to config.json
    config_path = os.path.join(BASE_DIR, 'config', 'config.json')
    try:
        with open(config_path) as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in configuration file: {config_path}")
        raise

def get_log_file_path():
    config = load_config()
    return config.get('log_file_path', os.path.join(BASE_DIR, 'logs', 'processing_log.txt'))

def setup_logging():
    log_file_path = get_log_file_path()
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        encoding='utf-8')

def get_api_key():
    config = load_config()
    return config.get('api_key')

def get_folders():
    config = load_config()
    # Dynamically build paths based on BASE_DIR
    return {
        'audio_folder':     config.get('audio_folder',      os.path.join(BASE_DIR, 'input_files', 'audio_files')),
        'error_folder':     config.get('error_folder',      os.path.join(BASE_DIR, 'input_files', 'error_files')),
        'video_folder':     config.get('video_folder',      os.path.join(BASE_DIR, 'input_files', 'video_files')),
        'processed_folder': config.get('processed_folder',  os.path.join(BASE_DIR, 'input_files', 'processed_files')),
        'original_folder':  config.get('original_folder',   os.path.join(BASE_DIR, 'input_files', 'original_files')),
        
        'success_folder':   config.get('success_folder',    os.path.join(BASE_DIR, 'output_files', 'song_detection', 'success')),
        'failed_folder':    config.get('failed_folder',     os.path.join(BASE_DIR, 'output_files', 'song_detection', 'failed')),
        
        'temp_folder':      config.get('temp_folder',       os.path.join(BASE_DIR, 'temp_files'))
    }