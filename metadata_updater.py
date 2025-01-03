from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TPE2, TCOM, TCON, TYER, TRCK, TPOS, APIC
import requests
import logging

def update_metadata(audio_file_path, metadata):

    # Updates the metadata of an MP3 file.

    try:
        audio = MP3(audio_file_path, ID3=ID3)

        # Remove existing ID3 tags
        audio.delete()
        audio.save()

        # Add new ID3 tags
        audio.tags.add(TIT2(encoding=3, text=metadata.get('title', '')))
        audio.tags.add(TPE1(encoding=3, text=metadata.get('artist', '')))
        audio.tags.add(TALB(encoding=3, text=metadata.get('album', '')))
        audio.tags.add(TPE2(encoding=3, text=metadata.get('album_artist', '')))
        audio.tags.add(TCOM(encoding=3, text=metadata.get('composer', '')))
        audio.tags.add(TCON(encoding=3, text=metadata.get('genre', '')))
        audio.tags.add(TYER(encoding=3, text=metadata.get('year', '')))
        audio.tags.add(TRCK(encoding=3, text=metadata.get('track', '')))
        audio.tags.add(TPOS(encoding=3, text=metadata.get('disc', '')))

        # Add album art if available
        if metadata.get('album_art_url'):
            add_album_art(audio, metadata['album_art_url'])

        audio.save()
        logging.info(f"Updated metadata for {audio_file_path}")
        return True
    except Exception as e:
        logging.error(f"Error updating metadata for {audio_file_path}: {e}")
        return False

def add_album_art(audio, album_art_url):
    """
    Adds album art to the audio file.
    """
    try:
        album_art_data = requests.get(album_art_url).content
        audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=album_art_data))
        logging.info("Added album art")
    except Exception as e:
        logging.error(f"Error adding album art: {e}")

def get_current_metadata(audio_file_path):
    """
    Retrieves the current metadata of an MP3 file.
    """
    try:
        audio = MP3(audio_file_path, ID3=ID3)
        metadata = {
            'title': str(audio.tags.get('TIT2', '')),
            'artist': str(audio.tags.get('TPE1', '')),
            'album': str(audio.tags.get('TALB', '')),
            'album_artist': str(audio.tags.get('TPE2', '')),
            'composer': str(audio.tags.get('TCOM', '')),
            'genre': str(audio.tags.get('TCON', '')),
            'year': str(audio.tags.get('TYER', '')),
            'track': str(audio.tags.get('TRCK', '')),
            'disc': str(audio.tags.get('TPOS', '')),
        }
        return metadata
    except Exception as e:
        logging.error(f"Error getting current metadata for {audio_file_path}: {e}")
        return {}

def compare_metadata(current_metadata, new_metadata):
    """
    Compares current metadata with new metadata and returns a dictionary of changes.
    """
    changes = {}
    for key in new_metadata:
        if new_metadata[key] != current_metadata.get(key):
            changes[key] = (current_metadata.get(key), new_metadata[key])
    return changes
