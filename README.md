# Voice-Enabled AI Teaching Assistant

A hands-free classroom co-pilot designed for teachers in Haryana government schools, optimized for smart boards and supporting Hinglish (Hindi-English code-switched) interactions.

## Features
1. **Live Concept Simplification**: Simplifies complex terms on command, displaying high-contrast concept cards and reading the outputs aloud using TTS.
2. **Voice-Triggered Quizzing**: Generates a 3-5 question multiple-choice quiz on any topic, complete with custom CSS buttons, timers, and scoring.

## Tech Stack
- **Frontend**: Streamlit
- **Speech-to-Text (STT)**: OpenAI Whisper API
- **Large Language Model (LLM)**: Claude 3.5 Sonnet
- **Text-to-Speech (TTS)**: gTTS (Hindi & English speech routing)

## Project Structure
- `app.py`: Entrypoint.
- `core/`: Audio transcription, speech synthesis, Claude interaction, and prompts.
- `ui/`: Streamlit views for concept simplification and interactive quiz cards.
