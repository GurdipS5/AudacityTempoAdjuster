import os
import subprocess
from mutagen.mp3 import MP3
from mutagen.flac import FLAC

# Function to change tempo for lossless files (WAV, FLAC) using FFmpeg
def change_tempo_lossless_ffmpeg(input_path, output_path, tempo_increase):
    tempo_factor = 1 + tempo_increase / 100
    command = [
        'ffmpeg', '-i', input_path,
        '-filter:a', f"atempo={tempo_factor}",
        '-c:a', 'copy',  # Preserve original audio codec and quality
        output_path # test
    ]
    subprocess.run(command, check=True)
    print(f"Processed {input_path} with {tempo_increase}% tempo increase and saved to {output_path}")

# Function to get the bit rate of an MP3 file
def get_mp3_bitrate(mp3_file):
    audio = MP3(mp3_file)
    return f"{int(audio.info.bitrate / 1000)}k"  # Convert to 'kbps' format

# Function to get the bit rate of a FLAC file
def get_flac_bitrate(flac_file):
    audio = FLAC(flac_file)
    # Calculate bit rate: (sample_rate * bits_per_sample * channels) / 1000 (to get kbps)
    bit_rate = (audio.info.sample_rate * audio.info.bits_per_sample * audio.info.channels) / 1000
    return f"{int(bit_rate)}k"

# Function to change tempo for lossy files (MP3) using FFmpeg
def change_tempo_lossy_ffmpeg(input_path, output_path, tempo_increase):
    tempo_factor = 1 + tempo_increase / 100

    # Get the original bit rate dynamically
    bit_rate = get_mp3_bitrate(input_path)

    command = [
        'ffmpeg', '-i', input_path,
        '-filter:a', f"atempo={tempo_factor}",
        '-b:a', bit_rate,  # Dynamically set the bit rate to the original value
        output_path
    ]
    subprocess.run(command, check=True)
    print(f"Processed {input_path} with {tempo_increase}% tempo increase and saved to {output_path}")

# Directories
input_directory = 'G:\\Input'
output_directory = 'G:\\Input\\Out'

# Tempo increase percentage
tempo_increase = 12  # Increase tempo by 12%

# Process each file in the directory
for filename in os.listdir(input_directory):
    input_path = os.path.join(input_directory, filename)
    output_path = os.path.join(output_directory, filename)

    if filename.endswith('.wav'):
        # Process WAV files with FFmpeg
        change_tempo_lossless_ffmpeg(input_path, output_path, tempo_increase)

    elif filename.endswith('.flac'):
        # Get and print the bit rate of the FLAC file
        flac_bitrate = get_flac_bitrate(input_path)
        print(f"Bit rate for {filename}: {flac_bitrate}")

        # Process FLAC files with FFmpeg
        change_tempo_lossless_ffmpeg(input_path, output_path, tempo_increase)

    elif filename.endswith('.mp3'):
        # Process MP3 files with FFmpeg, using dynamic bit rate retrieval
        change_tempo_lossy_ffmpeg(input_path, output_path, tempo_increase)
