import subprocess
import os
import shutil

def check_video(file_path):
    # Command to check the video file using FFmpeg
    command = ['ffmpeg', '-v', 'error', '-i', file_path, '-f', 'null', '-']
    # Execute the command and capture the output
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    return result.stderr

def move_corrupted_files(source_folder, error_folder):
    # Create the error folder if it doesn't exist
    os.makedirs(error_folder, exist_ok=True)
    
    # Loop through all files in the source folder
    for filename in os.listdir(source_folder):
        if filename.endswith('.mp4'):
            full_path = os.path.join(source_folder, filename)
            # Check if the video file has errors
            error = check_video(full_path)
            if error:
                print(f"Error detected in {filename}:")
                print(error)
                # Move file to error folder
                shutil.move(full_path, os.path.join(error_folder, filename))
            else:
                print(f"No errors detected in {filename}")

# Set the paths
source_folder = r'C:\ShazamProject\input_files\video_files'
error_folder = r'C:\ShazamProject\input_files\error_files'

# Process the files
move_corrupted_files(source_folder, error_folder)
