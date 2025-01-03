import subprocess

def get_audio_bitrate(input_file_path):
    command = ['ffmpeg', '-i', input_file_path]
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    lines = result.stderr.split('\n')
    for line in lines:
        if "Audio:" in line and "kb/s" in line:
            parts = line.split(',')
            for part in parts:
                if "kb/s" in part:
                    bitrate = part.strip().split(' ')[0]
                    return bitrate + 'k'
    return '192k'  # Default fallback bitrate if not detected

# Example usage
file_path = 'C:/ShazamProject/input_files/audio_files/#ASV.m4a'
print("Audio bitrate is:", get_audio_bitrate(file_path))