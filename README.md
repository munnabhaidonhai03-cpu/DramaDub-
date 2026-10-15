# DramaDub Android — prototype

A native Android starter for Turkish → Urdu drama dubbing. This is a prototype, not a production-ready real-time dubbing system.

## Included
- Android Kotlin app with a start/stop screen.
- Android `MediaProjection` + `AudioPlaybackCapture` PCM capture path.
- Foreground service that sends short PCM chunks to a backend.
- Python FastAPI backend using faster-whisper for Turkish speech recognition, deep-translator for Turkish → Urdu translation, and gTTS for Urdu speech audio.
- Urdu speech audio playback in the Android app.

## Critical limitations
1. **YouTube capture is not guaranteed.** Android playback capture only works when the source app permits capture and the audio usage/policy is compatible. If YouTube audio cannot be captured, use microphone capture as a separately implemented fallback or a permitted source.
2. This starter sends 4-second chunks to a server, so it is *chunked near-real-time*, not word-level streaming. Expect several seconds of delay and possible clipped sentences.
3. It plays Urdu audio on top of the source. It does not reliably mute/replace YouTube's original audio. Android does not give a normal app general control over another app's audio track. Use YouTube's own volume controls where possible or use a playback source you control.
4. The demo backend uses third-party translation and TTS libraries. For a real deployment, replace them with authenticated, low-latency services that explicitly support Turkish STT, Urdu translation and a natural Pakistani Urdu voice.
5. The backend has no authentication, rate limiting, TLS termination or privacy controls. Do not expose it publicly as-is. Add HTTPS, authentication, quotas and clear consent before production.
6. The Android service uses an app-private MediaProjection capture session. Android may stop capture if the user revokes permission, the device locks, or the source excludes playback capture.

## Requirements
- Android Studio (recent stable)
- JDK 17
- Android SDK 35
- Python 3.10+
- For internal playback capture, Android 10 / API 29+; physical-device behavior varies by source app.

## Run the backend
```bash
cd backend
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
The first Whisper model load downloads model weights. For testing on a physical phone, set `BACKEND_URL` in `app/build.gradle.kts` to the computer's LAN IP, e.g. `http://192.168.1.10:8000/`. The phone and computer must share a network. `10.0.2.2` is the Android emulator's host alias, but a physical phone cannot use it.

**HTTP cleartext is enabled only for local development.** Use HTTPS in production.

## Run the Android app
1. Open this folder in Android Studio and sync Gradle.
2. Change `BACKEND_URL` to your reachable backend address.
3. Install on an Android 10+ device.
4. Tap **Start capture** and accept Android's screen/audio-capture prompt.
5. Start the drama in YouTube and test. If YouTube prevents capture, the app will receive silence or no useful speech; that is a platform/source restriction, not a translation bug.
6. Tap **Stop** to stop capture.

## Production architecture
- Capture: `MediaProjection` + `AudioPlaybackCapture` when allowed; optional microphone mode with echo cancellation and headphones.
- Streaming STT: WebSocket or gRPC streaming recognizer configured for `tr-TR`; do not send independent tiny clips in the production version.
- Translation: context-aware Turkish → Urdu API, batching complete utterances and preserving character names/terms.
- Voice: neural TTS explicitly offering Urdu (`ur-PK` or a Pakistani Urdu voice). The sample gTTS voice is not guaranteed to sound Pakistani.
- Playback: timestamped utterance queue, barge-in/cancellation, latency budget, adaptive buffering and audio ducking only where allowed.
- Security: backend authentication, HTTPS, secrets on server, consent, retention controls and abuse limits.
