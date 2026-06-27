import os
import streamlit as st
from dotenv import load_dotenv

# Load env file if it exists (local development)
load_dotenv()

def _get_api_key(key_name: str) -> str:
    """
    Retrieves API key from Streamlit secrets or environment variables.
    """
    # 1. Try streamlit secrets
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    
    # 2. Try environment variables
    return os.getenv(key_name, "")

def transcribe_audio(audio_file) -> str:
    """
    Transcribes audio to text using Groq Whisper (whisper-large-v3-turbo).
    
    Args:
        audio_file: Either a file path string, an UploadedFile-like object, or bytes.
        
    Returns:
        str: The transcribed text.
    """
    groq_key = _get_api_key("GROQ_API_KEY")
    
    if not groq_key:
        raise ValueError(
            "API Key missing! Please set GROQ_API_KEY "
            "in your environment variables or Streamlit secrets."
        )

    # Determine file object name and bytes
    file_name = "audio.wav"
    file_bytes = None
    
    if isinstance(audio_file, str):
        file_name = os.path.basename(audio_file)
        with open(audio_file, "rb") as f:
            file_bytes = f.read()
    elif hasattr(audio_file, "read"):
        if hasattr(audio_file, "name") and audio_file.name:
            file_name = audio_file.name
        audio_file.seek(0)
        file_bytes = audio_file.read()
    elif isinstance(audio_file, bytes):
        file_bytes = audio_file
    else:
        raise ValueError("Unsupported audio file format. Must be file path, file-like object, or bytes.")

    # 1. Analyze audio bytes for duration and silence (if WAV)
    is_silent = False
    duration = None
    try:
        import wave
        import io
        import struct
        with wave.open(io.BytesIO(file_bytes), 'rb') as wav:
            params = wav.getparams()
            nchannels, sampwidth, framerate, nframes = params[:4]
            if framerate > 0:
                duration = nframes / float(framerate)
            
            if nframes > 0 and sampwidth in (1, 2):
                raw_frames = wav.readframes(nframes)
                if sampwidth == 2:
                    num_samples = len(raw_frames) // 2
                    if num_samples > 0:
                        samples = struct.unpack(f"<{num_samples}h", raw_frames)
                        max_amp = max(abs(s) for s in samples)
                        # If max amplitude is extremely low, it is silence/near-silence
                        if max_amp < 400:
                            is_silent = True
                elif sampwidth == 1:
                    num_samples = len(raw_frames)
                    if num_samples > 0:
                        samples = struct.unpack(f"<{num_samples}B", raw_frames)
                        max_amp = max(abs(s - 128) for s in samples)
                        if max_amp < 3:
                            is_silent = True
    except Exception:
        pass

    # Early reject very short or silent WAV clips
    if duration is not None:
        if duration < 0.8 or is_silent:
            print(f"DEBUG STT Filter: Early reject audio clip. Duration: {duration:.2f}s, Silent: {is_silent}")
            return ""

    raw_transcript = ""

    # Call the appropriate API
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            # Use whisper-large-v3-turbo for fast response times
            response = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=(file_name, file_bytes),
                language="hi",  # Guide model for Hinglish speech
                prompt="Hinglish transcription, Hindi-English code-switching in classroom smart board. For example: 'आज हम photo-synthesis study karenge.'"
            )
            raw_transcript = response.text
        except Exception as e:
            raise RuntimeError(f"Groq Whisper transcription failed: {str(e)}")
    # Perform validation on raw_transcript
    if not raw_transcript or not raw_transcript.strip() or len(raw_transcript.strip()) < 2:
        print(f"DEBUG STT Filter: Rejected short/empty transcript '{raw_transcript}'")
        return ""
        
    normalized = raw_transcript.strip().lower().rstrip(".?!,")
    hallucination_denylist = {
        "thank you", "thank you for watching", "subscribe", "subscribe to my channel",
        "subtitles by", "subtitles by representation", "you", "bye", "bye bye", "oh", "ah",
        "okay", "ok", "hello", "please rate this video", "please like and subscribe",
        "like and subscribe", "english subtitles", "subtitles", "youtube", "subbed"
    }
    
    if normalized in hallucination_denylist:
        print(f"DEBUG STT Filter: Rejected hallucination transcript '{raw_transcript}'")
        return ""
        
    # Check for repeating word patterns
    words = raw_transcript.strip().split()
    if len(words) >= 3:
        unique_words = set(w.lower().rstrip(".?!,") for w in words)
        if len(unique_words) <= 2 and (len(words) / len(unique_words)) >= 3:
            print(f"DEBUG STT Filter: Rejected repeating word pattern transcript '{raw_transcript}'")
            return ""

    return raw_transcript
