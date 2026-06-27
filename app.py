import streamlit as st
from ui.concept_view import render_concept_view
from ui.quiz_view import render_quiz_view

# Configure page metadata and wide layout for smart board visibility
st.set_page_config(
    page_title="Hinglish AI Teaching Assistant",
    page_icon="🏫",
    layout="wide",
)

# Set up smart board CSS overrides for large text sizes and high-contrast colors
st.markdown("""
<style>
    /* Global large text and margins */
    .stApp {
        background-color: #F8FAFC;
    }
    .hero-container {
        background-color: #1E40AF;
        padding: 24px 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(30, 64, 175, 0.1), 0 4px 6px -2px rgba(30, 64, 175, 0.05);
        border: 2px solid #2563EB;
    }
    .hero-title {
        font-size: 38px !important;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0 !important;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 18px !important;
        color: #F8FAFC !important;
        margin-top: 8px !important;
        margin-bottom: 0 !important;
        font-weight: 500;
        opacity: 0.95;
    }
    .hero-accent {
        color: #F59E0B !important;
        font-weight: 700;
    }
    
    /* Tab formatting */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        justify-content: center;
        margin-bottom: 25px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 20px !important;
        font-weight: bold !important;
        height: 55px !important;
        background-color: #FFFFFF !important;
        border-radius: 8px 8px 0px 0px !important;
        padding: 10px 25px !important;
        color: #475569 !important; /* Muted Text */
        border: 1px solid #E2E8F0 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E40AF !important; /* Primary Blue */
        color: white !important;
        border: 1px solid #1E40AF !important;
    }
    
    /* Force high contrast dark text for base text labels and markdown paragraphs */
    div[data-testid="stWidgetLabel"] p, 
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stText"] p,
    .stApp label {
        color: #1E293B !important;
    }
    /* Ensure all button text paragraphs inherit color from their parent button container */
    .stApp button p {
        color: inherit !important;
    }
    
    /* Unified Card for Voice Action */
    .st-key-concept_voice_card,
    .st-key-quiz_voice_card {
        background-color: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 4px 6px rgba(30, 64, 175, 0.02) !important;
        margin-bottom: 25px !important;
    }
    
    /* Voice recorder widget (st.audio_input) styling */
    .stAudioInput, 
    div[data-testid="stAudioInput"],
    .st-key-concept_mic_input,
    .st-key-quiz_mic_input {
        background-color: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.01) !important;
        --primary-color: #1E40AF !important;
        --secondary-color: #2563EB !important;
    }
    /* Force inner components of st.audio_input to be light theme and readable,
       excluding divs to allow visualizer/waveform placeholder gradients to render properly */
    div[data-testid="stAudioInput"] span,
    div[data-testid="stAudioInput"] p,
    div[data-testid="stAudioInput"] button {
        background-color: transparent !important;
        color: #1E293B !important;
    }
    /* Ensure action button icons are clearly visible in theme blue */
    div[data-testid="stAudioInput"] button {
        color: #1E40AF !important;
    }
    div[data-testid="stAudioInput"] button svg {
        color: #1E40AF !important;
        fill: currentColor !important;
    }
    div[data-testid="stAudioInput"] label {
        display: none !important;
    }
    /* Style the placeholder dots visualizer in theme blue */
    div[data-testid="stAudioInput"] div:not([data-testid]) div:not([data-testid]) div:not([data-testid]) {
        background: radial-gradient(#1E40AF 2px, transparent 0) !important;
        background-size: 24px 24px !important;
    }
    
    /* Manual text input (st.text_input) styling */
    div[data-testid="stTextInput"] div {
        background-color: transparent !important;
        background-image: none !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        background-image: none !important;
        background: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 4px 8px !important;
        color: #1E293B !important;
        box-shadow: none !important;
        transition: border-color 0.15s ease-in-out !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: #2563EB !important;
    }
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        color: #1E293B !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #64748B !important;
        opacity: 1 !important;
    }
    
    /* Fallback upload expander container styling */
    div[data-testid="stExpander"],
    .st-key-concept_fallback_expander,
    .st-key-quiz_fallback_expander {
        background-color: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(30, 64, 175, 0.02) !important;
    }
    
    /* Fallback upload expander header styling */
    div[data-testid="stExpander"] summary,
    .st-key-concept_fallback_expander summary,
    .st-key-quiz_fallback_expander summary {
        background-color: #F8FAFC !important;
        border-radius: 10px !important;
        padding: 10px 15px !important;
    }
    
    /* Fallback upload expander title text styling */
    div[data-testid="stExpander"] summary p,
    .st-key-concept_fallback_expander summary p,
    .st-key-quiz_fallback_expander summary p {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 18px !important;
    }
    
    /* Primary action buttons styling (Prominent CTA) */
    .st-key-simplify_concept_btn button,
    .st-key-generate_quiz_btn button {
        background-color: #1E40AF !important;
        color: #FFFFFF !important;
        font-size: 22px !important;
        font-weight: bold !important;
        padding: 16px 32px !important;
        border-radius: 12px !important;
        border: 2px solid #2563EB !important;
        box-shadow: 0 4px 6px rgba(30, 64, 175, 0.15) !important;
        transition: all 0.2s ease-in-out !important;
        width: auto !important;
        min-height: 55px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .st-key-simplify_concept_btn button:hover,
    .st-key-generate_quiz_btn button:hover {
        background-color: #2563EB !important;
        border-color: #3B82F6 !important;
        transform: scale(1.02) !important;
        box-shadow: 0 6px 12px rgba(30, 64, 175, 0.25) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-container">
    <div class="hero-title">🎓 Voice-Enabled AI Teaching Assistant</div>
    <div class="hero-subtitle">Smart Board Co-Pilot for <span class="hero-accent">Government Schools</span></div>
</div>
""", unsafe_allow_html=True)

# Create the two core views as tabs
tab_concept, tab_quiz = st.tabs(["📝 Explain a Concept", "❓ Take a Quiz"])

with tab_concept:
    render_concept_view()

with tab_quiz:
    render_quiz_view()
