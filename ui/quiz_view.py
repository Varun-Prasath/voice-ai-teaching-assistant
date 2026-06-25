import streamlit as st
import textwrap
from core.stt import transcribe_audio
from core.llm import generate_quiz, get_friendly_error_message
from core.tts import synthesize_speech

def render_quiz_view():
    # Inject high-contrast custom CSS for quiz layout on smart boards
    st.markdown("""
    <style>
        /* Base button overrides for options to make them large color cards */
        div[data-testid="column"] button {
            width: 100% !important;
            min-height: 110px !important;
            font-size: 24px !important;
            font-weight: bold !important;
            color: #1E40AF !important; /* Primary Blue text */
            background-color: #FFFFFF !important; /* Card Background */
            border-radius: 12px !important;
            border: 2px solid #E2E8F0 !important;
            padding: 20px !important;
            margin-bottom: 15px !important;
            box-shadow: 0 4px 6px rgba(30, 64, 175, 0.05) !important;
            transition: all 0.15s ease-in-out !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            white-space: normal !important;
            text-align: center !important;
        }
        
        div[data-testid="column"] button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 6px 12px rgba(30, 64, 175, 0.1) !important;
            border-color: #2563EB !important; /* Secondary Blue hover border */
            background-color: #F8FAFC !important;
        }
        
        /* Question Card display */
        .quiz-q-card {
            background-color: #1E40AF; /* Primary Blue */
            color: white;
            padding: 35px 25px;
            border-radius: 12px;
            font-size: 30px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 10px 15px -3px rgba(30, 64, 175, 0.15);
            border: 3px solid #2563EB; /* Secondary Blue */
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
    if "last_active_quiz_audio" not in st.session_state:
        st.session_state.last_active_quiz_audio = None

    # Helper function to trigger option selection
    def select_option(idx, correct_idx):
        st.session_state.quiz_selected_idx = idx
        st.session_state.quiz_answered = True
        if idx == correct_idx:
            st.session_state.quiz_score += 1
        st.rerun()

    # View 1: Quiz setup / launch screen
    if not st.session_state.quiz_active and not st.session_state.quiz_finished:
        st.markdown('<div style="font-size: 26px; font-weight: bold; color: #1E40AF; margin-bottom: 10px;">❓ Start a Classroom Quiz</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 18px; color: #475569; margin-bottom: 20px;">Use your voice to request a topic (e.g. "Create a quiz on photosynthesis"), or enter it manually.</div>', unsafe_allow_html=True)

        # Primary Action Card for Voice Input (Merged into unified container card)
        with st.container(key="quiz_voice_card"):
            st.markdown('<div style="font-size: 20px; font-weight: 700; color: #1E40AF; margin-bottom: 5px;">🎙️ Speak Quiz Topic (Primary Action)</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 15px; color: #475569; margin-bottom: 12px;">Tap the record button below to state the quiz topic.</div>', unsafe_allow_html=True)
            audio_file = st.audio_input("Speak Quiz Topic", label_visibility="collapsed", key="quiz_mic_input")

        # Secondary manual text input
        st.markdown('<div style="margin-top: 15px; margin-bottom: 10px;">', unsafe_allow_html=True)
        text_topic = st.text_input("✏️ Option: Enter the topic manually (e.g. Gravity, Fractions, Photosynthesis)", key="quiz_text_input")
        st.markdown('</div>', unsafe_allow_html=True)

        # Fallback File Uploader Expander
        st.markdown('<div style="margin-top: 5px; margin-bottom: 25px;">', unsafe_allow_html=True)
        with st.expander("📁 Fallback: Upload a voice command audio file instead", key="quiz_fallback_expander"):
            uploaded_file = st.file_uploader("Upload wav/mp3/m4a audio file", type=["wav", "mp3", "m4a"], key="quiz_file_upload")
        st.markdown('</div>', unsafe_allow_html=True)

        active_audio = audio_file if audio_file is not None else uploaded_file

        if st.button("🎯 Generate Quiz", key="generate_quiz_btn"):
            topic = ""
            
            # 1. Process voice transcription
            if active_audio is not None:
                with st.spinner("🎙️ Listening... thinking... preparing your answer..."):
                    try:
                        topic = transcribe_audio(active_audio)
                    except Exception as e:
                        st.error(get_friendly_error_message(e))
                        topic = ""

            # 2. Process text input fallback
            if not topic and text_topic:
                topic = text_topic.strip()

            # 3. Call generator
            if topic:
                st.markdown(f"<div style='font-size: 20px; font-weight: bold; color: #1E40AF; margin-bottom: 15px;'>🎤 Heard: '{topic}'</div>", unsafe_allow_html=True)
                with st.spinner("🎙️ Listening... thinking... preparing your answer..."):
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
                            st.error("⚠️ Something unexpected happened. Please try again.")
                    except Exception as e:
                        st.error(get_friendly_error_message(e))
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

        # Stage 3: Audio generation (runs once per question)
        if not st.session_state.quiz_audio_bytes and not st.session_state.quiz_answered:
            with st.spinner("🎙️ Listening... thinking... preparing your answer..."):
                try:
                    st.session_state.quiz_audio_bytes = synthesize_speech(question_text)
                    st.rerun()
                except Exception as e:
                    st.error(get_friendly_error_message(e))
                    st.session_state.quiz_audio_bytes = b""
                    st.rerun()

        # Render question voice playback
        if st.session_state.quiz_audio_bytes:
            st.audio(st.session_state.quiz_audio_bytes, format="audio/mp3", autoplay=True)

        # CSS-only client-side visual timer (prevents server sleep-loop rerun lags)
        if not st.session_state.quiz_answered:
            timer_html = f"""<div style="background-color: #E2E8F0; width: 100%; height: 12px; border-radius: 6px; margin-bottom: 25px; overflow: hidden; border: 1px solid #E2E8F0;">
<div style="background-color: #DC2626; height: 100%; width: 100%; animation: quiz-timer 15s linear forwards;"></div>
</div>
<style>
@keyframes quiz-timer {{
from {{ width: 100%; }}
to {{ width: 0%; }}
}}
</style>"""
            st.markdown(timer_html, unsafe_allow_html=True)

        # Dynamic CSS Injection to highlight option button states (Green/Red feedback)
        if st.session_state.quiz_answered:
            selectors = [
                'div[data-testid="column"]:nth-of-type(1) div.stButton:nth-of-type(1) button', # A
                'div[data-testid="column"]:nth-of-type(2) div.stButton:nth-of-type(1) button', # B
                'div[data-testid="column"]:nth-of-type(1) div.stButton:nth-of-type(2) button', # C
                'div[data-testid="column"]:nth-of-type(2) div.stButton:nth-of-type(2) button'  # D
            ]
            
            correct_selector = selectors[correct_index]
            selected_selector = selectors[st.session_state.quiz_selected_idx] if st.session_state.quiz_selected_idx is not None else None
            
            style_overrides = "<style>"
            # Fade all column buttons
            style_overrides += "div[data-testid=\"column\"] button { opacity: 0.3 !important; pointer-events: none !important; color: #475569 !important; border-color: #E2E8F0 !important; }"
            
            # Highlight selected option (Secondary Blue: #2563EB)
            if selected_selector:
                style_overrides += f"{selected_selector} {{ background-color: #2563EB !important; border: 3px solid #1E40AF !important; color: white !important; opacity: 1.0 !important; }}"
            
            # Highlight correct option (Success Green: #16A34A)
            style_overrides += f"{correct_selector} {{ background-color: #16A34A !important; border: 3px solid #15803D !important; color: white !important; opacity: 1.0 !important; }}"
            
            # If incorrect selection, override highlight selected option with Incorrect Red (#DC2626)
            if selected_selector and selected_selector != correct_selector:
                style_overrides += f"{selected_selector} {{ background-color: #DC2626 !important; border: 3px solid #991B1B !important; color: white !important; opacity: 1.0 !important; }}"
            
            style_overrides += "</style>"
            st.markdown(style_overrides, unsafe_allow_html=True)

        # Grid view layout (2x2 columns)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(options[0], key="quiz_btn_a"):
                select_option(0, correct_index)
            if st.button(options[2], key="quiz_btn_c"):
                select_option(2, correct_index)

        with col2:
            if st.button(options[1], key="quiz_btn_b"):
                select_option(1, correct_index)
            if st.button(options[3], key="quiz_btn_d"):
                select_option(3, correct_index)

        # After question answered state
        if st.session_state.quiz_answered:
            is_correct = (st.session_state.quiz_selected_idx == correct_index)
            if is_correct:
                st.success("🎉 Shabash! Correct Answer!")
            else:
                correct_desc = options[correct_index]
                st.error(f"❌ Oops! Wrong Answer. Correct option was: {correct_desc}")

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
        incorrect = total - score
        accuracy = int((score / total) * 100) if total > 0 else 0

        # Evaluate score and choose warm Hinglish feedback
        feedback = ""
        if score == total:
            feedback = "Kamaal kar diya bacho! Perfect score. Sabhi answers sahi hain! 🌟"
        elif score >= total / 2:
            feedback = "Bahut badhiya prayas! Aapne bahut achha kiya. Agli baar aur badhiya karenge! 👍"
        else:
            feedback = "Koi baat nahi bacho! Seekhte rahenge. Ek baar fir se try karte hain! 💪"

        html_content = (
            f'<div style="background-color: #FFFFFF; border: 3px solid #F59E0B; border-radius: 16px; padding: 35px; text-align: center; box-shadow: 0 10px 25px rgba(245, 158, 11, 0.1); margin-bottom: 25px;">'
            f'<div style="font-size: 36px; font-weight: 800; color: #F59E0B; margin-bottom: 5px;">🏆 Quiz Complete!</div>'
            f'<div style="font-size: 22px; color: #475569; margin-bottom: 25px; font-weight: 600;">Topic: {topic}</div>'
            f'<div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 30px; flex-wrap: wrap;">'
            f'<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px 25px; min-width: 120px;">'
            f'<div style="font-size: 18px; color: #475569; font-weight: bold; margin-bottom: 5px;">✅ Correct</div>'
            f'<div style="font-size: 28px; color: #16A34A; font-weight: 800;">{score}</div>'
            f'</div>'
            f'<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px 25px; min-width: 120px;">'
            f'<div style="font-size: 18px; color: #475569; font-weight: bold; margin-bottom: 5px;">❌ Incorrect</div>'
            f'<div style="font-size: 28px; color: #DC2626; font-weight: 800;">{incorrect}</div>'
            f'</div>'
            f'<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px 25px; min-width: 120px;">'
            f'<div style="font-size: 18px; color: #475569; font-weight: bold; margin-bottom: 5px;">📈 Accuracy</div>'
            f'<div style="font-size: 28px; color: #2563EB; font-weight: 800;">{accuracy}%</div>'
            f'</div>'
            f'</div>'
            f'<div style="font-size: 24px; font-weight: bold; color: #1E293B; line-height: 1.4; padding-top: 15px; border-top: 1px solid #E2E8F0;">'
            f'🎉 {feedback}'
            f'</div>'
            f'</div>'
        )
        st.markdown(html_content, unsafe_allow_html=True)

        if st.button("🔄 New Quiz", key="reset_quiz_btn"):
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
