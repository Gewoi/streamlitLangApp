from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from pathlib import Path

input_dir = Path("/Users/giulianomartinelli/Documents/conv_to_wav/voicelines_input")
output_dir = Path("/Users/giulianomartinelli/Documents/conv_to_wav/output")

# Silence detection settings — tweak these if trimming is too aggressive or not enough
SILENCE_THRESH = -40    # dBFS, anything quieter than this is considered silence
MIN_SILENCE_MS = 100    # minimum duration to count as silence
PADDING_MS = 1000       # 1 second of padding to keep before/after sound

for opus_file in input_dir.glob("*.opus"):
    try:
        audio = AudioSegment.from_file(opus_file)

        # --- Normalize (Ableton-style peak normalization to 0 dBFS) ---
        peak_normalized = audio.apply_gain(-audio.max_dBFS)

        # --- Trim silence with 1s padding ---
        nonsilent_ranges = detect_nonsilent(
            peak_normalized,
            min_silence_len=MIN_SILENCE_MS,
            silence_thresh=SILENCE_THRESH
        )

        if nonsilent_ranges:
            start_ms = max(0, nonsilent_ranges[0][0] - PADDING_MS)
            end_ms = min(len(peak_normalized), nonsilent_ranges[-1][1] + PADDING_MS)
            trimmed = peak_normalized[start_ms:end_ms]
        else:
            print(f"Warning: no sound detected in {opus_file.name}, skipping trim")
            trimmed = peak_normalized

        # --- Export ---
        output_path = output_dir / opus_file.with_suffix(".mp3").name
        trimmed.export(output_path, format="mp3")
        print(f"Converted: {opus_file.name} -> {output_path.name}")

    except Exception as e:
        print(f"Failed: {opus_file.name} — {e}")