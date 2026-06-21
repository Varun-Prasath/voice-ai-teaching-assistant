import streamlit as st
from core.stt import transcribe_audio
from core.llm import explain_concept

def render_concept_view():
    st.markdown('<div style="font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 10px;">📝 Ask a Concept Question</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 18px; color: #475569; margin-bottom: 20px;">Use your voice to ask a question in Hinglish (e.g., "Photosynthesis kya hota hai, basic steps samjhao?")</div>', unsafe_allow_html=True)

    # Initialize session states
    if "concept_transcript" not in st.session_state:
        st.session_state.concept_transcript = ""
    if "concept_explanation" not in st.session_state:
        st.session_state.concept_explanation = None
    if "last_active_audio" not in st.session_state:
        st.session_state.last_active_audio = None

    # Audio recording input
    audio_file = st.audio_input("Record your voice command")

    # File uploader fallback
    uploaded_file = st.file_uploader("Or upload an audio file (wav/mp3/m4a)", type=["wav", "mp3", "m4a"])

    active_audio = audio_file if audio_file is not None else uploaded_file

    # Auto-reset state when audio input changes
    if active_audio != st.session_state.last_active_audio:
        st.session_state.concept_transcript = ""
        st.session_state.concept_explanation = None
        st.session_state.last_active_audio = active_audio
        st.rerun()

    if active_audio is not None:
        st.info("Audio source detected. Click below to simplify the concept.")
        
        # Trigger button (Stage 1: STT)
        if not st.session_state.concept_transcript:
            if st.button("Simplify Concept", key="simplify_concept_btn"):
                with st.spinner("Step 1/2: Listening to audio (STT)..."):
                    try:
                        st.session_state.concept_transcript = transcribe_audio(active_audio)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to transcribe: {str(e)}")
                        return

        # Stage 2: LLM (Automatic trigger after Stage 1 finishes)
        if st.session_state.concept_transcript and not st.session_state.concept_explanation:
            with st.spinner("Step 2/2: Simplifying concept with Gemini LLM..."):
                try:
                    st.session_state.concept_explanation = explain_concept(st.session_state.concept_transcript)
                    st.rerun()
                except Exception as e:
                    st.error(f"Gemini LLM Error: {str(e)}")
                    # Allow user to retry LLM if it fails by clearing transcript
                    st.session_state.concept_transcript = ""
                    return

    # Render transcript immediately
    if st.session_state.concept_transcript:
        st.markdown("### 🎙️ Detected Transcript:")
        st.markdown(
            f'<div style="font-size: 24px; font-weight: bold; background-color: #EFF6FF; color: #1E293B; padding: 20px; border-radius: 8px; border-left: 6px solid #3B82F6; margin-bottom: 20px;">{st.session_state.concept_transcript}</div>', 
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
        html_content = f"""<div style="background-color: #FFFFFF; border: 3px solid #1E3A8A; border-radius: 12px; padding: 25px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 20px;">
<div style="font-size: 26px; font-weight: bold; color: #1E3A8A; margin-bottom: 15px; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px;">
💡 Topic Summary
</div>
<div style="font-size: 24px; line-height: 1.6; color: #1E293B; margin-bottom: 25px; font-weight: 500;">
{explanation}
</div>
<div style="margin-top: 15px;">
<div style="font-size: 20px; font-weight: bold; color: #475569; margin-bottom: 10px;">🔑 Key Points:</div>
<ul style="list-style-type: none; padding-left: 0;">
{"".join(f'<li style="font-size: 22px; color: #0F172A; margin-bottom: 12px; font-weight: 500;">{point}</li>' for point in key_points)}
</ul>
</div>
</div>"""
        st.markdown(html_content, unsafe_allow_html=True)

        # Diagram Section
        if diagram_hint:
            st.markdown("### 📊 Process Diagram:")
            steps = [s.strip() for s in diagram_hint.split("->")]
            if len(steps) > 1:
                html_str = '<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 10px; margin-top: 10px; margin-bottom: 30px; background-color: #F8FAFC; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0;">'
                for i, step in enumerate(steps):
                    html_str += f"""
                    <div style="background-color: #1E3A8A; color: white; padding: 15px 25px; border-radius: 8px; font-size: 22px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 5px; text-align: center; min-width: 150px;">
                        {step}
                    </div>
                    """
                    if i < len(steps) - 1:
                        html_str += '<div style="font-size: 32px; color: #1E3A8A; font-weight: bold; padding: 0 10px;">➡️</div>'
                html_str += '</div>'
                st.markdown(html_str, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #EFF6FF; border: 2px dashed #3B82F6; padding: 15px; border-radius: 8px; font-size: 20px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 30px;">
                    📊 Process Flow: {diagram_hint}
                </div>
                """, unsafe_allow_html=True)
