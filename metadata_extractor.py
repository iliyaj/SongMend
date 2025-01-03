import logging

def extract_metadata(detection_result, song_details):
    metadata = {
        'title': '',
        'artist': '',
        'album': '',
        'album_artist': '',
        'composer': '',
        'genre': '',
        'year': '',
        'track': '1',
        'disc': '1',
        'album_art_url': '',
    }

    try:
        # Extract data from detection result
        if 'track' in detection_result:
            track = detection_result['track']
            metadata['title'] = track.get('title', '')
            metadata['artist'] = track.get('subtitle', '')
            metadata['album_art_url'] = track['images'].get('coverart', '')
            metadata['genre'] = track.get('genres', {}).get('primary', '')
            metadata['track'] = str(track.get('trackNumber', '1'))

            # Extract additional data from sections
            if 'sections' in track:
                song_section = next((section for section in track['sections'] if section['type'] == 'SONG'), {})
                if song_section:
                    metadata['album'] = next((item['text'] for item in song_section.get('metadata', []) if item['title'] == 'Album'), '')
                    metadata['year'] = next((item['text'] for item in song_section.get('metadata', []) if item['title'] == 'Released'), '')

            metadata['album_artist'] = metadata['artist']

        # Extract data from song details
        if song_details and 'data' in song_details and len(song_details['data']) > 0:
            attributes = song_details['data'][0].get('attributes', {})
            metadata['composer'] = attributes.get('composerName', metadata['composer'])
            metadata['album'] = attributes.get('albumName', metadata['album'])
            metadata['year'] = attributes.get('releaseDate', metadata['year']).split('-')[0]
            metadata['track'] = str(attributes.get('trackNumber', metadata['track']))
            metadata['disc'] = str(attributes.get('discNumber', metadata['disc']))
            if 'artwork' in attributes:
                metadata['album_art_url'] = attributes['artwork']['url'].format(w=2400, h=2400)

    except Exception as e:
        logging.error(f"Error extracting metadata: {e}")

    return metadata

def clean_metadata(metadata):
    """
    Cleans up the metadata by removing any empty fields and sanitizing values.
    """
    cleaned_metadata = {}
    for key, value in metadata.items():
        if value:
            # Remove any leading/trailing whitespace
            if isinstance(value, str):
                value = value.strip()
            # Sanitize filename-unfriendly characters
            if key in ['title', 'artist', 'album', 'album_artist', 'composer']:
                value = value.replace('/', '_').replace('\\', '_')
            cleaned_metadata[key] = value
    return cleaned_metadata

def validate_metadata(metadata):
    """
    Validates the metadata to ensure all required fields are present.
    Returns True if valid, False otherwise.
    """
    required_fields = ['title', 'artist']
    for field in required_fields:
        if not metadata.get(field):
            logging.warning(f"Missing required metadata field: {field}")
            return False
    return True
