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
    options: List[str] = Field(description="List of exactly 4 options. Every option MUST strictly follow the 'Hindi term (English translation)' format, e.g. 'Dharti (Earth)' or 'Suraj (Sun)'. This is strictly mandatory.")
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

def _generate_with_fallback(client, contents: str, system_instruction: str, response_schema, temperature: float) -> str:
    """
    Attempts to generate content using the configured GEMINI_MODEL or fallback chain.
    """
    from google.genai import types

    # Check if a specific model was overridden in the environment
    env_model = os.getenv("GEMINI_MODEL", "")
    if env_model:
        models_to_try = [env_model]
    else:
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

    last_err = None
    for model_name in models_to_try:
        try:
            print(f"[GEMINI CALL] Trying model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    system_instruction=system_instruction,
                    temperature=temperature
                )
            )
            return response.text
        except Exception as e:
            last_err = e
            print(f"[FALLBACK] Model {model_name} failed: {str(last_err)}. Trying next fallback...")
            continue
            
    raise last_err

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
        client = genai.Client(api_key=api_key)
        
        response_text = _generate_with_fallback(
            client=client,
            contents=f"Simplify this concept: {transcript}",
            system_instruction=CONCEPT_SYSTEM_PROMPT,
            response_schema=ConceptExplanation,
            temperature=0.2
        )
        return json.loads(response_text)
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
        client = genai.Client(api_key=api_key)
        
        contents_prompt = (
            f"Generate a quiz on this topic: {topic}. "
            "Every option in the 'options' list MUST strictly follow the 'Hindi term (English translation)' format "
            "(e.g., 'Dharti (Earth)', 'Suraj (Sun)'). It is forbidden to output options without the parenthesized English translation."
        )
        
        response_text = _generate_with_fallback(
            client=client,
            contents=contents_prompt,
            system_instruction=QUIZ_SYSTEM_PROMPT,
            response_schema=Quiz,
            temperature=0.4
        )
        return json.loads(response_text)
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {str(e)}")
