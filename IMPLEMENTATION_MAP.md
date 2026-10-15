# Feature map: what is implemented vs what needs production services

| Layer | Prototype implementation | Production upgrade |
|---|---|---|
| Native capture | `CaptureService.kt`: Android MediaProjection + AudioPlaybackCapture, 16 kHz PCM chunks | Handle source-specific capture restrictions; microphone fallback with echo cancellation; lifecycle and device testing |
| Turkish STT | `backend/app.py`: faster-whisper processes 4-second chunks | Low-latency streaming STT WebSocket/gRPC, partial hypotheses, sentence boundaries, timestamps |
| Turkish → Urdu | `GoogleTranslator(source="tr", target="ur")` | Authenticated translation API with Urdu quality evaluation, context window and glossary |
| Urdu speech | `gTTS(lang="ur")` | Neural TTS provider that explicitly offers natural Pakistani Urdu; stream audio chunks |
| Playback | `UrduPlayer.kt` plays returned MP3 over source | Jitter buffer, timestamp alignment, cancel stale utterances, optional ducking only where permitted |
| Security | Local prototype only | HTTPS, API authentication, secrets management, rate limiting, privacy/retention controls |
| YouTube | Open YouTube separately | Capture works only if YouTube/device policy permits it; app cannot force direct capture or mute YouTube audio |

## Backend API contract

`POST /process-audio`
- Request: raw signed 16-bit little-endian PCM, mono, 16 kHz.
- Header: `X-Audio-Sample-Rate: 16000`
- Response JSON: `{ "turkish": "...", "urdu": "...", "audio_base64": "<mp3 base64>" }`

The sample is chunk-based, and the audio chunks can split sentences. For a truly live experience, change the contract to a persistent WebSocket that sends PCM frames and emits partial transcript, completed translated utterance and TTS audio events with sequence numbers/timestamps.
