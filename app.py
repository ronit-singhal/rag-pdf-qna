import streamlit as st
import os
import tempfile
from streamlit_lottie import st_lottie
import requests
from streamlit_extras.colored_header import colored_header

from RAGQASystem import RAGQASystem

if 'rag_system' not in st.session_state:
    st.session_state.rag_system = RAGQASystem()
if 'current_document' not in st.session_state:
    st.session_state.current_document = None

# Function to load Lottie animation
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Lottie animations
lottie_robot = load_lottie_url("https://assets7.lottiefiles.com/packages/lf20_M9p23l.json")

# Set page config
st.set_page_config(page_title="📚 Interactive QA Bot", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        font-family: 'Roboto', sans-serif;
    }
    .main {
        background: transparent;
    }
    .stApp {
        max-width: 100%;
        padding: 2rem;
    }
    .upload-box {
        border: 2px dashed #ffffff;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        background-color: rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    .upload-box:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    .stTextInput>div>div>input {
        width: 100%;
        height: 15px;
        padding: 15px;
        font-size: 1.2rem;
        border-radius: 10px;
        border: 2px solid #a29bfe;
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }
    .stButton>button {
        background-color: #6c5ce7;
        color: white;
        font-size: 1.1rem;
        padding: 10px 20px;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #5851db;
        transform: translateY(-2px);
    }
    .css-1avcm0n, .css-vurnku {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);

    }
    h1 {
        color: #ffffff;
        font-weight: bold;
        font-size: 3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    h2 {
        color: #a29bfe;
        font-size: 2rem;
    }
    h3 {
        color: #dfe6e9;
        font-size: 1.5rem;
    }
    .sidebar .sidebar-content {
        background-color: rgba(108, 92, 231, 0.1);
        padding: 30px;
        border-radius: 20px;
    }
    .sidebar-text {
        color: #dfe6e9;
        font-size: 1.1rem;
    }
    .sidebar-header {
        color: #a29bfe;
        font-size: 1.5rem;
        margin-bottom: 20px;
    }
    .expander {
        background-color: rgba(108, 92, 231, 0.2);
        color: #dfe6e9;
        border-radius: 10px;
        margin-bottom: 10px;
        padding: 10px;
    }
    .stAlert {
        background-color: rgba(46, 213, 115, 0.2);
        color: #ffffff;
        border-radius: 10px;
        border: none;
    }
    .stSpinner > div {
        border-top-color: #a29bfe !important;
    }
    .css-1uqoehk {
        display: none;
    }
    /* Animated gradient background */
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📚 Interactive QA Bot")
st.markdown("<h2>Upload a PDF document and ask questions about its content.</h2>", unsafe_allow_html=True)

# Sidebar with instructions
with st.sidebar:
    st_lottie(lottie_robot, height=250, key="robot")
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    colored_header(label="How to use", description="Follow these steps", color_name="blue-70")
    st.markdown('<div class="sidebar-text">1. Upload a PDF document</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">2. Wait for the document to be processed</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">3. Ask questions about the document</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">4. View the bot\'s response</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("📄 Upload a PDF file", type="pdf")

if uploaded_file is not None:
    if st.session_state.current_document != uploaded_file.name:
        st.session_state.current_document = uploaded_file.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        with st.spinner("⏳ Processing document..."):
            st.session_state.rag_system.load_documents(tmp_file_path)

        st.success("✅ Document processed successfully!")

        # Clean up temporary file
        os.unlink(tmp_file_path)

    # Text input for questions
    user_question = st.text_input("🤖 Ask a question about the document:", key="question_input")

    if user_question and st.button("Find Answer", key="find_answer"):
        with st.spinner("🔍 Finding answer..."):
            answer, source_docs = st.session_state.rag_system.answer_question(user_question)

        # Display answer
        colored_header(label="Answer", description="Here's what I found", color_name="blue-70")
        st.markdown(f"<div class='css-1avcm0n'>{answer}</div>", unsafe_allow_html=True)

        # Display source documents with expanders for each relevant segment
        colored_header(label="Relevant Document Segments", description="Supporting information", color_name="blue-30")
        for i, doc in enumerate(source_docs):
            with st.expander(f"📄 Segment {i+1}"):
                st.write(doc.page_content)