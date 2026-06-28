# 🎓 Voice-Enabled AI Teaching Assistant

A hands-free classroom co-pilot built for teachers in Haryana government schools — designed for smart board use, supporting natural Hinglish (Hindi-English code-switched) voice interaction.

**Live demo:** [voice-ai-teaching-assistant.streamlit.app](https://voice-ai-teaching-assistant-e7iakcr7khpexk9twuxh3b.streamlit.app/)

---

## 📌 The Problem

A teacher in a government classroom is juggling a smart board, a room full of students, and a curriculum to get through — there's no time to type, search, or fumble with a keyboard mid-lesson. Students speak in Hinglish, not textbook English or formal Hindi. This project is a voice-first co-pilot that lets a teacher simply *speak* a question or quiz request, and get back a classroom-ready visual and spoken response, in the language students actually use.

## ✨ Features

### 1. Live Concept Simplification
Teacher asks a concept question by voice (or types it as a fallback) → the app transcribes it, generates a short, conversational Hinglish explanation, displays it as a high-contrast "concept card" with key points and an optional process diagram, and reads it aloud via TTS.

### 2. Voice-Triggered Quizzing
Teacher requests a quiz topic by voice (or types it) → the app generates a 3-question multiple-choice quiz, displays each question with a timer and color-coded answer options, reads questions aloud, and shows a final score with an encouraging message.

---

## 🛠️ Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Streamlit** | Fast to build, built-in audio widgets, no separate frontend needed |
| Speech-to-Text | **Groq Whisper Large v3** | Free tier with generous, predictable rate limits — no card required |
| LLM | **Google Gemini (2.5 Flash, with fallback chain)** | Free tier, structured JSON output support, strong Hinglish generation quality |
| Text-to-Speech | **gTTS** | Free, supports Hindi (`hi`) and English (`en`) language routing |
| State management | **Streamlit `session_state`** | No database needed for a prototype |
| Deployment | **Streamlit Community Cloud** | Free hosting, direct GitHub integration |

### A note on provider choices

This project initially used Claude for the LLM layer and OpenAI Whisper for STT. Both were swapped for free-tier alternatives (Gemini and Groq Whisper respectively) to keep the prototype fully cost-free for the evaluation period, while testing confirmed acceptable Hinglish output quality and JSON-schema reliability on the free alternatives. Groq's Llama 3.3 70B was also evaluated as a backup LLM option — it produced reliable, schema-compliant output but noticeably stiffer, less conversational Hinglish than Gemini, so Gemini was kept as the primary LLM.

---

## 📁 Project Structure

```
voice-ai-teaching-assistant/
├── app.py                  # Main entrypoint, global styling, tab routing
├── requirements.txt
├── README.md
├── core/
│   ├── stt.py               # Groq Whisper transcription
│   ├── tts.py                # gTTS speech synthesis with Hindi/English routing
│   ├── llm.py                # Gemini API calls, structured output parsing
│   └── prompts.py             # System prompts for concept explanation & quiz generation
├── ui/
│   ├── concept_view.py       # Concept Simplification tab
│   └── quiz_view.py           # Voice-Triggered Quizzing tab
├── assets/
├── sample_audio/              # Pre-recorded Hinglish test clips
├── .env.example
└── .gitignore
```

---

## 🧠 Prompt Design

Both `CONCEPT_SYSTEM_PROMPT` and `QUIZ_SYSTEM_PROMPT` (in `core/prompts.py`) were iterated on through several rounds of testing against real spoken Hinglish input, with the following deliberate design choices:

- **Strict JSON schema enforcement.** Both prompts require a single valid JSON object with no markdown fencing or preamble, parsed against Pydantic models (`ConceptExplanation`, `Quiz`) for reliability.
- **TTS-readability constraint.** Question and explanation text is explicitly required to "sound normal when read aloud," since this is a voice-first app — text that reads fine on screen doesn't always sound natural when spoken by TTS.
- **Bilingual quiz-option formatting rule.** Every quiz answer option must follow a strict `"Hindi term (English translation)"` format (e.g., "Suraj (Sun)") so options are unambiguous for both visual display and TTS read-aloud — while the question text itself stays translation-free for natural spoken flow. An explicit exception was added for proper nouns and English-origin terms already used as-is in spoken Hindi (e.g., "Mumbai," "Oxygen," "Protein"), since forcing a redundant parenthetical on these ("Mumbai (Mumbai)") produced absurd duplicate output during testing.
- **Word and step limits.** The concept explanation is capped at 45 words to keep it skimmable on a smart board at a glance, rather than a dense paragraph. Diagram hints, when generated, are capped at exactly 3 steps.
- **Conditional diagram generation.** The LLM is instructed to only generate a process diagram for genuinely sequential concepts (e.g., water cycle, photosynthesis) and return `null` for non-sequential ones (e.g., gravity, definitions), rather than inventing an artificial sequence for every topic.
- **Grade-level anchoring.** Both prompts anchor output difficulty to 6th–10th grade comprehension level, with an explicit fallback rule for the rare case where a teacher asks about a topic well outside that range (e.g., advanced physics) — the model still attempts a simplified analogy rather than refusing.

---

## 🌐 Localization Approach

Hinglish here is treated as a first-class language, not a translation target — prompts explicitly forbid parenthesized English glosses inside explanations (e.g., no "Suraj (Sun) ka grah") since real classroom speech doesn't talk that way. The one deliberate exception is quiz *options specifically*, where unambiguous bilingual labels matter more than conversational flow, since a misread option could cost a student the right answer.

STT was tested across a range of phrasing styles — short imperative requests ("Gravity ka quiz banao") were found to transcribe more reliably than longer, more casual sentence structures, which is noted as a usage tip below.

---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/Varun-Prasath/voice-ai-teaching-assistant.git
cd voice-ai-teaching-assistant
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`) with:
```
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

Run locally:
```bash
streamlit run app.py
```

For Streamlit Community Cloud deployment, add the same two keys under **App settings → Secrets** instead of `.env`.

> 🎤 **Don't have a mic handy?** Try `Topic_Exp_1.mpeg` or `Quiz_Sample_Audio.mpeg` through the "Upload an audio file instead" fallback on either tab to test the app without recording your own voice.
---

## ⚠️ Known Limitations

- **STT reliability varies with phrasing.** Short, direct spoken requests transcribe more reliably than long or grammatically casual sentences. A manual text-entry fallback is provided on both tabs for cases where voice transcription doesn't capture intent correctly.
- **Free-tier rate limits.** Both Gemini and Groq are used on free-tier API keys, which carry rate limits lower than a paid production deployment would have. Under heavy concurrent testing, requests may occasionally fail; the app shows a friendly retry message rather than crashing in this case.
- **Silent/empty input handling.** Whisper-family STT models can occasionally hallucinate plausible-sounding text from silence or background noise. The app includes validation to catch and reject empty, too-short, or known-hallucination-pattern transcripts before they reach the LLM, but this filter may not catch every edge case.
- **Quiz length is fixed at 3 questions** per session, chosen for a focused, quick-to-complete classroom activity rather than a long-form assessment.
- **No persistence.** All state (scores, history) resets per session — there is no database, by design, for this prototype stage.

---

## 🎥 Demo Video

[Watch the 3-minute demo](https://drive.google.com/file/d/1Os0xvZgc1v-Uf-T1-0J2D9IbyVBkG5VD/view?usp=sharing)

---

Built for the Connecting Dreams Foundation Round 2 Technical Assignment.
