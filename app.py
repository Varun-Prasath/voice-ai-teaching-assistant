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
    
    /* Voice recorder widget (st.audio_input) styling */
    .stAudioInput, 
    div[data-testid="stAudioInput"],
    .st-key-concept_mic_input,
    .st-key-quiz_mic_input {
        background-color: #F1F5F9 !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02) !important;
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
