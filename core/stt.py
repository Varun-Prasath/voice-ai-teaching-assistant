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
    Transcribes audio to text in a provider-agnostic manner.
    Prioritizes Groq Whisper (whisper-large-v3-turbo) if GROQ_API_KEY is present,
    falls back to OpenAI Whisper (whisper-1) if OPENAI_API_KEY is present.
    
    Args:
        audio_file: Either a file path string, an UploadedFile-like object, or bytes.
        
    Returns:
        str: The transcribed text.
    """
    groq_key = _get_api_key("GROQ_API_KEY")
    openai_key = _get_api_key("OPENAI_API_KEY")
    
    if not groq_key and not openai_key:
        raise ValueError(
            "API Key missing! Please set GROQ_API_KEY or OPENAI_API_KEY "
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
            return response.text
        except Exception as e:
            raise RuntimeError(f"Groq Whisper transcription failed: {str(e)}")
            
    elif openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=(file_name, file_bytes),
                language="hi",
                prompt="Hinglish, Hindi-English code-switching: 'आज हम cell structure padhenge.'"
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"OpenAI Whisper transcription failed: {str(e)}")
            
    return ""
