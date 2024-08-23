import os
import subprocess
import json
import ffmpeg
from mutagen.mp3 import MP3
from mutagen.flac import FLAC

def get_audio_properties(input_file):
    """
    Use ffprobe to extract audio properties from the input FLAC file.
    """
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'stream=sample_rate,channels,bit_rate,sample_fmt',
             '-of', 'json', input_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Parse the result
        probe_data = json.loads(result.stdout)
        # Check if 'streams' is present in the result
        if 'streams' in probe_data and len(probe_data['streams']) > 0:
            return probe_data['streams'][0]
        else:
            raise ValueError("No audio streams found in the file.")
    except json.JSONDecodeError:
        raise ValueError("Failed to parse the ffprobe output.")
    except Exception as e:
        raise RuntimeError(f"ffprobe encountered an error: {e}")


def change_tempo_lossless(input_file, output_file, tempo_factor):
    """
    Change the tempo of a FLAC audio file while keeping the pitch, bitrate, sample depth the same, and keeping it lossless.

    :param input_file: Path to the input FLAC file.
    :param output_file: Path to the output FLAC file.
    :param tempo_factor: Factor by which to change the tempo. Greater than 1 speeds up, less than 1 slows down.
    """
    # Get audio properties using ffprobe
    audio_properties = get_audio_properties(input_file)

    sample_rate = audio_properties.get('sample_rate')
    channels = audio_properties.get('channels')
    bit_rate = audio_properties.get('bit_rate')
    sample_format = audio_properties.get('sample_fmt')

    # Apply the atempo filter to change the tempo
    ffmpeg.input(input_file).output(
        output_file,
        af=f'atempo={tempo_factor}',
        acodec='flac',  # Use FLAC codec for lossless encoding
        ar=sample_rate,  # Keep the original sample rate
        ac=channels  # Maintain the original number of channels
    ).run()


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
input_directory = 'G:\\Phone\\'
output_directory = 'G:\\Phone\\Out'

# Tempo increase percentage
tempo_increase = 12  # Increase tempo by 12%

# Process each file in the directory
for filename in os.listdir(input_directory):
    input_path = os.path.join(input_directory, filename)
    output_path = os.path.join(output_directory, filename)

    if filename.endswith('.wav'):
        # Process WAV files with FFmpeg
        change_tempo_lossless(input_path, output_path, tempo_increase)

    elif filename.endswith('.flac'):
        # Get and print the bit rate of the FLAC file
        flac_bitrate = get_flac_bitrate(input_path)
        print(f"Bit rate for {filename}: {flac_bitrate}")

        # Process FLAC files with FFmpeg
        change_tempo_lossless(input_path, output_path, 1.12)

    elif filename.endswith('.mp3'):
        # Process MP3 files with FFmpeg, using dynamic bit rate retrieval
        change_tempo_lossy_ffmpeg(input_path, output_path, tempo_increase)
