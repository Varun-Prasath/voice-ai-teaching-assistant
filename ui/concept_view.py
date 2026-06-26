import streamlit as st
from core.stt import transcribe_audio
from core.llm import explain_concept, get_friendly_error_message
from core.tts import synthesize_speech

def render_concept_view():
    st.markdown('<div style="font-size: 26px; font-weight: bold; color: #1E40AF; margin-bottom: 10px;">📝 Ask a Concept Question</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 18px; color: #475569; margin-bottom: 20px;">Use your voice to ask a question in Hinglish (e.g., "Photosynthesis kya hota hai, basic steps samjhao?")</div>', unsafe_allow_html=True)

    # Initialize session states
    if "concept_transcript" not in st.session_state:
        st.session_state.concept_transcript = ""
    if "concept_explanation" not in st.session_state:
        st.session_state.concept_explanation = None
    if "concept_audio_bytes" not in st.session_state:
        st.session_state.concept_audio_bytes = None
    if "last_active_audio" not in st.session_state:
        st.session_state.last_active_audio = None

    # Primary Action Card for Voice Input (Merged into unified container card)
    with st.container(key="concept_voice_card"):
        st.markdown('<div style="font-size: 20px; font-weight: 700; color: #1E40AF; margin-bottom: 5px;">🎙️ Speak to Smart Board (Primary Action)</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 15px; color: #475569; margin-bottom: 12px;">Tap the record button below to speak your question directly to the system.</div>', unsafe_allow_html=True)
        audio_file = st.audio_input("Speak to Smart Board", label_visibility="collapsed", key="concept_mic_input")

    # Secondary Expander for File Upload Fallback
    st.markdown('<div style="margin-top: 15px; margin-bottom: 25px;">', unsafe_allow_html=True)
    with st.expander("📁 Fallback: Upload an audio file instead", key="concept_fallback_expander"):
        uploaded_file = st.file_uploader("Upload wav/mp3/m4a audio file", type=["wav", "mp3", "m4a"], key="concept_file_upload")
    st.markdown('</div>', unsafe_allow_html=True)

    active_audio = audio_file if audio_file is not None else uploaded_file

    # Auto-reset state when audio input changes
    if active_audio != st.session_state.last_active_audio:
        st.session_state.concept_transcript = ""
        st.session_state.concept_explanation = None
        st.session_state.concept_audio_bytes = None
        st.session_state.last_active_audio = active_audio
        st.rerun()

    if active_audio is not None:
        st.info("Audio source detected. Click below to simplify the concept.")
        
        # Stage 1: Transcription
        if not st.session_state.concept_transcript:
            if st.button("Simplify Concept", key="simplify_concept_btn"):
                with st.spinner("🎙️ Listening... thinking... preparing your answer..."):
                    try:
                        transcript = transcribe_audio(active_audio)
                        
                        # Validate the transcript
                        if not transcript or not transcript.strip() or transcript.strip() in [".", "...", ",", "?", "!"]:
                            # Reset/Clear all related states to avoid reuse
                            st.session_state.concept_transcript = ""
                            st.session_state.concept_explanation = None
                            st.session_state.concept_audio_bytes = None
                            st.error("🎤 Didn't catch that — please try speaking again")
                            return
                        
                        st.session_state.concept_transcript = transcript.strip()
                        st.rerun()
                    except Exception as e:
                        st.error(get_friendly_error_message(e))
                        return

        # Stage 2: Explanation (automatic trigger after Stage 1)
        if st.session_state.concept_transcript and not st.session_state.concept_explanation:
            st.markdown(f"<div style='font-size: 20px; font-weight: bold; color: #1E40AF; margin-bottom: 15px;'>🎤 Heard: '{st.session_state.concept_transcript}'</div>", unsafe_allow_html=True)
            with st.spinner("🎙️ Listening... thinking... preparing your answer..."):
                try:
                    st.session_state.concept_explanation = explain_concept(st.session_state.concept_transcript)
                    st.rerun()
                except Exception as e:
                    st.error(get_friendly_error_message(e))
                    st.session_state.concept_transcript = ""
                    return

        # Stage 3: TTS Synthesis (automatic trigger after Stage 2)
        if st.session_state.concept_explanation and not st.session_state.concept_audio_bytes:
            st.markdown(f"<div style='font-size: 20px; font-weight: bold; color: #1E40AF; margin-bottom: 15px;'>🎤 Heard: '{st.session_state.concept_transcript}'</div>", unsafe_allow_html=True)
            with st.spinner("🎙️ Listening... thinking... preparing your answer..."):
                try:
                    explanation_text = st.session_state.concept_explanation.get("explanation", "")
                    st.session_state.concept_audio_bytes = synthesize_speech(explanation_text)
                    st.rerun()
                except Exception as e:
                    st.error(get_friendly_error_message(e))
                    # Do not block UI display of card if TTS fails, just flag as empty bytes
                    st.session_state.concept_audio_bytes = b""
                    st.rerun()

    # Render Transcript immediately
    if st.session_state.concept_transcript:
        st.markdown("### 🎙️ Detected Transcript:")
        st.markdown(
            f'<div style="font-size: 24px; font-weight: bold; background-color: #FFFFFF; color: #1E293B; padding: 20px; border-radius: 8px; border-left: 6px solid #2563EB; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(30, 64, 175, 0.05); margin-bottom: 20px;">{st.session_state.concept_transcript}</div>', 
            unsafe_allow_html=True
        )

    # Render Visual Concept Card and steps
    if st.session_state.concept_explanation:
        explanation_data = st.session_state.concept_explanation
        explanation = explanation_data.get("explanation", "")
        key_points = explanation_data.get("key_points", [])
        diagram_hint = explanation_data.get("diagram_hint", None)

        st.markdown("### 🔬 Visual Concept Card:")
        
        # High-contrast smart-board container (must have 0 leading spaces to prevent markdown code block triggers)
        html_content = f"""<div style="background-color: #FFFFFF; border: 3px solid #1E40AF; border-radius: 12px; padding: 25px; box-shadow: 0 10px 15px -3px rgba(30, 64, 175, 0.08); margin-bottom: 20px;">
<div style="font-size: 26px; font-weight: bold; color: #1E40AF; margin-bottom: 15px; border-bottom: 2px solid #F1F5F9; padding-bottom: 10px;">
💡 Topic Summary
</div>
<div style="font-size: 24px; line-height: 1.6; color: #1E293B; margin-bottom: 25px; font-weight: 500;">
{explanation}
</div>
<div style="margin-top: 15px;">
<div style="font-size: 20px; font-weight: bold; color: #475569; margin-bottom: 10px;">🔑 Key Points:</div>
<ul style="list-style-type: none; padding-left: 0;">
{"".join(f'<li style="font-size: 22px; color: #1E293B; margin-bottom: 12px; font-weight: 500;">{point}</li>' for point in key_points)}
</ul>
</div>
</div>"""
        st.markdown(html_content, unsafe_allow_html=True)

        # Audio Playback Control
        if st.session_state.concept_audio_bytes:
            st.markdown("### 🔊 Audio Co-Pilot Voice:")
            st.audio(st.session_state.concept_audio_bytes, format="audio/mp3", autoplay=True)

        # Diagram Section
        if diagram_hint:
            st.markdown("### 📊 Process Diagram:")
            steps = [s.strip() for s in diagram_hint.split("->")]
            if len(steps) > 1:
                html_str = '<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 10px; margin-top: 10px; margin-bottom: 30px; background-color: #FFFFFF; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(30, 64, 175, 0.05);">'
                for i, step in enumerate(steps):
                    html_str += f"""
                    <div style="background-color: #1E40AF; color: white; padding: 15px 25px; border-radius: 8px; font-size: 22px; font-weight: bold; box-shadow: 0 4px 6px rgba(30,64,175,0.1); margin: 5px; text-align: center; min-width: 150px; border: 1px solid #2563EB;">
                        {step}
                    </div>
                    """
                    if i < len(steps) - 1:
                        html_str += '<div style="font-size: 32px; color: #2563EB; font-weight: bold; padding: 0 10px;">➡️</div>'
                html_str += '</div>'
                st.markdown(html_str, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #F8FAFC; border: 2px dashed #2563EB; padding: 15px; border-radius: 8px; font-size: 20px; font-weight: bold; color: #1E40AF; text-align: center; margin-bottom: 30px;">
                    📊 Process Flow: {diagram_hint}
                </div>
                """, unsafe_allow_html=True)

        # Reset action button
        st.markdown('<div style="margin-top: 25px; margin-bottom: 25px;">', unsafe_allow_html=True)
        if st.button("🔄 Ask Another Question", key="reset_concept_btn"):
            st.session_state.concept_transcript = ""
            st.session_state.concept_explanation = None
            st.session_state.concept_audio_bytes = None
            st.session_state.last_active_audio = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
