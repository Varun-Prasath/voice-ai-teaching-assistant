import os
import json
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from core.prompts import CONCEPT_SYSTEM_PROMPT, QUIZ_SYSTEM_PROMPT

# Load env file if it exists (local development)
load_dotenv()

# Define Pydantic response schemas for Gemini structured outputs
class ConceptExplanation(BaseModel):
    explanation: str = Field(description="A short, conversational explanation (2-3 sentences) in natural Hinglish.")
    key_points: List[str] = Field(description="List of 3 key bullet points, each with a relevant emoji prefix (keep under 12 words per point).")
    diagram_hint: Optional[str] = Field(description="A string describing a simple step-by-step process/flow diagram, or null/None if a diagram is not helpful.")

class QuizQuestion(BaseModel):
    question: str = Field(description="A clear Hinglish question suitable for classroom display (max 15 words).")
    options: List[str] = Field(description="List of exactly 4 option choices. Each option MUST be in Hinglish with its English translation in parentheses (e.g. 'Dharti (Earth)').")
    correct_index: int = Field(description="0-indexed integer (0-3) indicating the correct option (0 for A, 1 for B, 2 for C, 3 for D).")

class Quiz(BaseModel):
    questions: List[QuizQuestion] = Field(description="A list of 3-5 quiz questions on the topic.")

def _get_api_key(key_name: str) -> str:
    """
    Retrieves API key from Streamlit secrets or environment variables.
    """
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name, "")

def explain_concept(transcript: str) -> dict:
    """
    Calls Gemini API to explain the transcribed concept in Hinglish.
    Returns:
        dict: {"explanation": str, "key_points": list[str], "diagram_hint": str|None}
    """
    api_key = _get_api_key("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API key is missing. Please set GEMINI_API_KEY in your env or Streamlit secrets.")

    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        response = client.models.generate_content(
            model=model_name,
            contents=f"Simplify this concept: {transcript}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ConceptExplanation,
                system_instruction=CONCEPT_SYSTEM_PROMPT,
                temperature=0.2
            )
        )
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {str(e)}")

def generate_quiz(topic: str) -> dict:
    """
    Calls Gemini API to generate MCQs for a given topic in Hinglish.
    Returns:
        dict: {"questions": [{"question": str, "options": list[str], "correct_index": int}]}
    """
    api_key = _get_api_key("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API key is missing. Please set GEMINI_API_KEY in your env or Streamlit secrets.")

    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        response = client.models.generate_content(
            model=model_name,
            contents=f"Generate a quiz on this topic: {topic}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Quiz,
                system_instruction=QUIZ_SYSTEM_PROMPT,
                temperature=0.4
            )
        )
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {str(e)}")
