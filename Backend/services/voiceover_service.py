import base64
import os
import tempfile
from gtts import gTTS

def generate_voiceover(script_text: str):
    tts = gTTS(text=script_text, lang="en", slow=False)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tmp_path = f.name
    
    tts.save(tmp_path)
    
    with open(tmp_path, "rb") as f:
        audio_bytes = f.read()
    
    os.unlink(tmp_path)
    
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    return {
        "audio_base64": audio_b64,
        "format": "mp3",
        "char_count": len(script_text),
        "voice": "Google TTS"
    }