import io
from gtts import gTTS

def synthesize_speech(text: str) -> bytes:
    """
    Synthesizes Hinglish speech using gTTS and returns the audio bytes in-memory.
    Routes text through lang='hi' for natural Hinglish pronunciation.
    
    Args:
        text (str): The Hinglish text to convert to speech.
        
    Returns:
        bytes: The synthesized MP3 audio bytes.
    """
    if not text or not text.strip():
        return b""
        
    try:
        # Route to Hindi ('hi') to naturally read Latin-based Hinglish text
        # and pronounce standard English science terms with an Indian accent.
        tts = gTTS(text=text, lang="hi")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        raise RuntimeError(f"gTTS speech synthesis failed: {str(e)}")
