import streamlit as st
import textwrap
from core.stt import transcribe_audio
from core.llm import generate_quiz
from core.tts import synthesize_speech

def render_quiz_view():
    # Inject high-contrast custom CSS for quiz layout on smart boards
    st.markdown("""
    <style>
        /* Base button overrides for options to make them large color cards */
        .opt-container button {
            width: 100% !important;
            min-height: 110px !important;
            font-size: 24px !important;
            font-weight: bold !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 20px !important;
            margin-bottom: 15px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            transition: all 0.15s ease-in-out !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            white-space: normal !important;
            text-align: center !important;
        }
        
        /* Option letter styling */
        .opt-letter {
            font-size: 32px !important;
            font-weight: 800 !important;
            margin-right: 15px !important;
            opacity: 0.9 !important;
        }

        /* Default option card background colors */
        .opt-a button { background-color: #2563EB !important; } /* Strong Blue */
        .opt-b button { background-color: #4F46E5 !important; } /* Indigo */
        .opt-c button { background-color: #0F766E !important; } /* Teal */
        .opt-d button { background-color: #D97706 !important; } /* Amber */
        
        .opt-container button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
            opacity: 0.95 !important;
        }
        
        /* Question Card display */
        .quiz-q-card {
            background-color: #1E3A8A;
            color: white;
            padding: 35px 25px;
            border-radius: 12px;
            font-size: 30px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            border: 3px solid #1D4ED8;
            line-height: 1.4;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize state machine variables
    if "quiz_active" not in st.session_state:
        st.session_state.quiz_active = False
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "quiz_current_idx" not in st.session_state:
        st.session_state.quiz_current_idx = 0
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_selected_idx" not in st.session_state:
        st.session_state.quiz_selected_idx = None
    if "quiz_answered" not in st.session_state:
        st.session_state.quiz_answered = False
    if "quiz_finished" not in st.session_state:
        st.session_state.quiz_finished = False
    if "quiz_audio_bytes" not in st.session_state:
        st.session_state.quiz_audio_bytes = None
    if "quiz_topic" not in st.session_state:
        st.session_state.quiz_topic = ""

    # Helper function to trigger option selection
    def select_option(idx, correct_idx):
        st.session_state.quiz_selected_idx = idx
        st.session_state.quiz_answered = True
        if idx == correct_idx:
            st.session_state.quiz_score += 1
        st.rerun()

    # View 1: Quiz setup / launch screen
    if not st.session_state.quiz_active and not st.session_state.quiz_finished:
        st.markdown('<div style="font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 10px;">❓ Start a Classroom Quiz</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 18px; color: #475569; margin-bottom: 20px;">Use your voice to request a topic (e.g. "Create a quiz on photosynthesis"), or enter it manually.</div>', unsafe_allow_html=True)

        audio_file = st.audio_input("Record quiz topic command")
        text_topic = st.text_input("Or enter the topic manually (e.g. Gravity, Fractions, Photosynthesis)")

        if st.button("Generate Quiz Show", key="generate_quiz_btn"):
            topic = ""
            
            # 1. Process voice transcription
            if audio_file is not None:
                with st.spinner("Step 1/2: Listening to your command (STT)..."):
                    try:
                        topic = transcribe_audio(audio_file)
                        st.info(f"Command detected: '{topic}'")
                    except Exception as e:
                        st.error(f"Speech transcription failed: {str(e)}. Falling back to manual text input.")
                        topic = ""

            # 2. Process text input fallback
            if not topic and text_topic:
                topic = text_topic.strip()

            # 3. Call Gemini to generate the quiz
            if topic:
                with st.spinner("Step 2/2: Generating quiz questions with Gemini LLM..."):
                    try:
                        quiz_data = generate_quiz(topic)
                        questions = quiz_data.get("questions", [])
                        if questions:
                            st.session_state.quiz_questions = questions
                            st.session_state.quiz_active = True
                            st.session_state.quiz_current_idx = 0
                            st.session_state.quiz_score = 0
                            st.session_state.quiz_selected_idx = None
                            st.session_state.quiz_answered = False
                            st.session_state.quiz_finished = False
                            st.session_state.quiz_audio_bytes = None
                            st.session_state.quiz_topic = topic
                            st.rerun()
                        else:
                            st.error("No questions were generated. Try a simpler topic or check your key.")
                    except Exception as e:
                        st.error(f"Quiz Generation Error: {str(e)}")
            else:
                st.warning("Please record your voice or enter a topic manually to start.")

    # View 2: Active quiz gameplay screen
    elif st.session_state.quiz_active:
        q_idx = st.session_state.quiz_current_idx
        questions = st.session_state.quiz_questions
        total_q = len(questions)
        q_data = questions[q_idx]

        question_text = q_data.get("question", "")
        options = q_data.get("options", [])
        correct_index = q_data.get("correct_index", 0)

        # Question header
        st.markdown(f'<div style="font-size: 20px; font-weight: bold; color: #475569; margin-bottom: 5px;">QUESTION {q_idx + 1} OF {total_q}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="quiz-q-card">{question_text}</div>', unsafe_allow_html=True)

        # Stage 3: In-Memory TTS audio generation (runs once per question)
        if not st.session_state.quiz_audio_bytes and not st.session_state.quiz_answered:
            with st.spinner("Synthesizing question audio (TTS)..."):
                try:
                    st.session_state.quiz_audio_bytes = synthesize_speech(question_text)
                    st.rerun()
                except Exception as e:
                    st.error(f"TTS Speech Error: {str(e)}")
                    st.session_state.quiz_audio_bytes = b""
                    st.rerun()

        # Render question voice playback
        if st.session_state.quiz_audio_bytes:
            st.audio(st.session_state.quiz_audio_bytes, format="audio/mp3", autoplay=True)

        # CSS-only client-side visual timer (prevents server sleep-loop rerun lags)
        if not st.session_state.quiz_answered:
            st.markdown(textwrap.dedent(f"""
            <div style="background-color: #E2E8F0; width: 100%; height: 12px; border-radius: 6px; margin-bottom: 25px; overflow: hidden; border: 1px solid #CBD5E1;">
                <div style="background-color: #EF4444; height: 100%; width: 100%; animation: quiz-timer 15s linear forwards;"></div>
            </div>
            <style>
                @keyframes quiz-timer {{
                    from {{ width: 100%; }}
                    to {{ width: 0%; }}
                }}
            </style>
            """).strip(), unsafe_allow_html=True)

        # Dynamic CSS Injection to highlight option button states (Green/Red feedback)
        if st.session_state.quiz_answered:
            letters = ['a', 'b', 'c', 'd']
            correct_letter = letters[correct_index]
            selected_letter = letters[st.session_state.quiz_selected_idx] if st.session_state.quiz_selected_idx is not None else None
            
            style_overrides = "<style>"
            # Fade all buttons by default
            style_overrides += ".opt-container button { opacity: 0.3 !important; pointer-events: none !important; }"
            # Highlight correct answer (Green)
            style_overrides += f".opt-{correct_letter} button {{ background-color: #10B981 !important; border: 4px solid #064E3B !important; opacity: 1.0 !important; }}"
            # If wrong answer selected, highlight it (Red)
            if selected_letter and selected_letter != correct_letter:
                style_overrides += f".opt-{selected_letter} button {{ background-color: #EF4444 !important; border: 4px solid #7F1D1D !important; opacity: 1.0 !important; }}"
            style_overrides += "</style>"
            st.markdown(style_overrides, unsafe_allow_html=True)

        # Grid view layout (2x2 columns)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="opt-container opt-a">', unsafe_allow_html=True)
            if st.button(options[0], key="quiz_btn_a"):
                select_option(0, correct_index)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="opt-container opt-c">', unsafe_allow_html=True)
            if st.button(options[2], key="quiz_btn_c"):
                select_option(2, correct_index)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="opt-container opt-b">', unsafe_allow_html=True)
            if st.button(options[1], key="quiz_btn_b"):
                select_option(1, correct_index)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="opt-container opt-d">', unsafe_allow_html=True)
            if st.button(options[3], key="quiz_btn_d"):
                select_option(3, correct_index)
            st.markdown('</div>', unsafe_allow_html=True)

        # After question answered state
        if st.session_state.quiz_answered:
            is_correct = (st.session_state.quiz_selected_idx == correct_index)
            if is_correct:
                st.success("🎉 **Shabash! Correct Answer!**")
            else:
                correct_desc = options[correct_index]
                st.error(f"❌ **Oops! Wrong Answer.** Correct option was: **{correct_desc}**")

            # Navigation buttons
            if q_idx + 1 < total_q:
                if st.button("Next Question ➡️", key="next_q_btn"):
                    st.session_state.quiz_current_idx += 1
                    st.session_state.quiz_selected_idx = None
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_audio_bytes = None
                    st.rerun()
            else:
                if st.button("Finish Quiz 🏁", key="finish_q_btn"):
                    st.session_state.quiz_active = False
                    st.session_state.quiz_finished = True
                    st.rerun()

    # View 3: Final quiz score report screen
    elif st.session_state.quiz_finished:
        score = st.session_state.quiz_score
        total = len(st.session_state.quiz_questions)
        topic = st.session_state.quiz_topic

        st.markdown('<div style="font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 10px;">🏆 Quiz Complete!</div>', unsafe_allow_html=True)

        # Evaluate score and choose warm Hinglish feedback
        feedback = ""
        if score == total:
            feedback = "Kamaal kar diya bacho! Perfect score. Sabhi answers sahi hain! 🌟"
        elif score >= total / 2:
            feedback = "Bahut badhiya prayas! Aapne bahut achha kiya. Agli baar aur badhiya karenge! 👍"
        else:
            feedback = "Koi baat nahi bacho! Seekhte rahenge. Ek baar fir se try karte hain! 💪"

        st.markdown(textwrap.dedent(f"""
        <div style="background-color: #FFFFFF; border: 3px solid #1E3A8A; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 25px;">
            <div style="font-size: 28px; font-weight: bold; color: #1E3A8A; margin-bottom: 15px;">
                Topic: {topic}
            </div>
            <div style="font-size: 52px; font-weight: 800; color: #2563EB; margin-bottom: 15px;">
                🎯 Score: {score} / {total}
            </div>
            <div style="font-size: 24px; font-weight: bold; color: #1E293B; line-height: 1.4;">
                {feedback}
            </div>
        </div>
        """).strip(), unsafe_allow_html=True)

        if st.button("Take Another Quiz 🔄", key="reset_quiz_btn"):
            st.session_state.quiz_active = False
            st.session_state.quiz_finished = False
            st.session_state.quiz_questions = []
            st.session_state.quiz_score = 0
            st.session_state.quiz_current_idx = 0
            st.session_state.quiz_selected_idx = None
            st.session_state.quiz_answered = False
            st.session_state.quiz_audio_bytes = None
            st.session_state.quiz_topic = ""
            st.rerun()
