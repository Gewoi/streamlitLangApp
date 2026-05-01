from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from pathlib import Path
import os

input_dir = Path("data/assets/audio")
output_dir = Path("data/assets/audio")

# Silence detection settings — tweak these if trimming is too aggressive or not enough
SILENCE_THRESH = -40    # dBFS, anything quieter than this is considered silence
MIN_SILENCE_MS = 100    # minimum duration to count as silence
PADDING_MS = 1000       # 1 second of padding to keep before/after sound

for wav_file in input_dir.glob("*.wav"):
    audio = AudioSegment.from_file(wav_file, format="wav")
    output_path = output_dir / wav_file.with_suffix(".mp3").name
    audio.export(output_path, format="mp3")
    print(wav_file, " replaced")
    os.remove(wav_file)
    