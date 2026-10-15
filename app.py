import base64
import io
import os
import tempfile
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Request
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
from gtts import gTTS

app = FastAPI(title="DramaDub demo backend")

@lru_cache(maxsize=1)
def model():
    # CPU-safe starter. For a GPU server, configure device/compute_type appropriately.
    return WhisperModel(os.getenv("WHISPER_MODEL", "small"), device="cpu", compute_type="int8")

@app.get("/health")
def health():
    return {"ok": True, "stt": "faster-whisper", "translation": "deep-translator", "tts": "gTTS"}

@app.post("/process-audio")
async def process_audio(request: Request):
    pcm = await request.body()
    if len(pcm) < 4000:
        raise HTTPException(400, "Audio chunk too short")
    if len(pcm) > 2_000_000:
        raise HTTPException(413, "Audio chunk too large")
    # Android sends raw 16-bit little-endian mono PCM at 16 kHz.
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name
    try:
        import wave
        with wave.open(wav_path, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(int(request.headers.get("X-Audio-Sample-Rate", "16000")))
            wav.writeframes(pcm)
        segments, _ = model().transcribe(wav_path, language="tr", vad_filter=True, beam_size=1)
        turkish = " ".join(s.text.strip() for s in segments).strip()
        if not turkish:
            return {"turkish": "", "urdu": "", "audio_base64": ""}
        urdu = GoogleTranslator(source="tr", target="ur").translate(turkish)
        audio = io.BytesIO()
        # gTTS supports Urdu language code, but voice/accent is not guaranteed Pakistani.
        gTTS(text=urdu, lang="ur", slow=False).write_to_fp(audio)
        return {
            "turkish": turkish,
            "urdu": urdu,
            "audio_base64": base64.b64encode(audio.getvalue()).decode("ascii")
        }
    except Exception as exc:
        raise HTTPException(502, f"Processing failed: {type(exc).__name__}: {exc}")
    finally:
        try: os.unlink(wav_path)
        except OSError: pass
