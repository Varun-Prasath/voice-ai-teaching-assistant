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
    .smartboard-title {
        font-size: 46px !important;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .smartboard-subtitle {
        font-size: 20px !important;
        color: #475569;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 500;
    }
    /* Tab formatting */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 22px !important;
        font-weight: bold !important;
        height: 60px !important;
        background-color: #E2E8F0 !important;
        border-radius: 8px 8px 0px 0px !important;
        padding: 10px 30px !important;
        color: #1E293B !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: white !important;
    }
    /* Force high contrast dark text for base text labels and markdown paragraphs */
    div[data-testid="stWidgetLabel"] p, 
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stText"] p,
    .stApp label {
        color: #0F172A !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="smartboard-title">🏫 Voice-Enabled AI Teaching Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="smartboard-subtitle">Haryana School Smart Board Co-Pilot (Hinglish Support)</div>', unsafe_allow_html=True)

# Create the two core views as tabs
tab_concept, tab_quiz = st.tabs(["📝 Explain a Concept", "❓ Take a Quiz"])

with tab_concept:
    render_concept_view()

with tab_quiz:
    render_quiz_view()
