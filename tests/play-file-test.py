import subprocess
import os

def play_audio(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found - {file_path}")
        return

    try:
        # Using FFplay to play the audio file
        command = ['ffplay', '-nodisp', '-autoexit', file_path]
        
        print(f"Playing: {file_path}")
        subprocess.run(command, check=True)
        print("Playback finished.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while playing the file: {e}")
    except FileNotFoundError:
        print("Error: FFplay not found. Make sure FFmpeg is installed and added to your system PATH.")

# File path
audio_file = r"C:/ShazamProject/input_files/processed_files/#VON_0.mp3"

# Play the audio
play_audio(audio_file)