import requests
import base64
import json
import logging
import io
from pydub import AudioSegment

# You might want to move this to config.py if it's used elsewhere
SHAZAM_API_URL = "https://shazam.p.rapidapi.com"

def convert_audio_to_shazam_format(input_file_path, start_time=20, duration=5):
    audio = AudioSegment.from_file(input_file_path)
    audio = audio.set_frame_rate(44100).set_channels(1).set_sample_width(2)
    start_ms = start_time * 1000
    end_ms = start_ms + (duration * 1000)
    audio_segment = audio[start_ms:end_ms]
    raw_data = io.BytesIO()
    audio_segment.export(raw_data, format="raw")
    return raw_data.getvalue()

def extract_song_id(detection_result):
    try:
        return detection_result['track']['hub']['actions'][0]['id']
    except (KeyError, IndexError):
        logging.warning("Could not extract song ID from detection result")
        return None

def detect_song(raw_data, api_key):
    encoded_data = base64.b64encode(raw_data).decode('utf-8')
    url = f"{SHAZAM_API_URL}/songs/v2/detect"
    querystring = {"timezone": "America/Chicago", "locale": "en-US"}
    payload = encoded_data
    headers = {
        "content-type": "text/plain",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "shazam.p.rapidapi.com"
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers, params=querystring)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        result = response.json()
        if 'track' in result:
            return result
        else:
            logging.warning("No track information found in Shazam response")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error detecting song: {e}")
        return None
    except json.JSONDecodeError:
        logging.error("Error decoding JSON response from Shazam API")
        return None

def get_song_details(song_id, api_key):
    url = f"{SHAZAM_API_URL}/songs/v2/get-details"
    querystring = {"id": song_id, "l": "en-US"}
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "shazam.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting song details: {e}")
        return None
    except json.JSONDecodeError:
        logging.error("Error decoding JSON response from Shazam API")
        return None
