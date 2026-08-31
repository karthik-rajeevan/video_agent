import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url :str) ->str:
    # YouTube intermittently 403s media downloads depending on client + IP.
    # Try several player clients in order until one succeeds.
    clients = ["android", "ios", "tv"]
    last_err = None

    for client in clients:
        try:
            return _download_with_client(url, client)
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"  → client '{client}' failed: {e}")
            continue

    raise RuntimeError(f"Failed to download YouTube audio: {last_err}")


def _download_with_client(url :str, client :str) ->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        # Explicitly use a webm audio-only format so the final container is
        # deterministic (avoids the intermediate .mp4/.m4a path mapping bug).
        "format": "251/bestaudio/best",
        "outtmpl": output_path,
        # Varies the player client to bypass YouTube's 403 bot-detection.
        "extractor_args": {
            "youtube": {
                "player_client": [client],
            }
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # The FFmpeg postprocessor converts to WAV, so point back at the .wav
        # that actually exists on disk (interim container is webm here).
        base = os.path.splitext(ydl.prepare_filename(info))[0]
        filename = base + ".wav"
    return filename



def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path



def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
