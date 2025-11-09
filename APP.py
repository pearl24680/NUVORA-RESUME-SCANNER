import streamlit as st
from PyPDF2 import PdfReader
import re

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="Nuvora AI Career Assistant", layout="centered")

# ==================== CUSTOM CSS ====================
st.markdown("""
    <style>
    body {
        background: linear-gradient(to bottom right, #E3F2FD, #BBDEFB);
        font-family: 'Poppins', sans-serif;
    }
    .title {
        font-size: 38px;
        font-weight: 800;
        color: #0D47A1;
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 16px;
        color: #1A237E;
        text-align: center;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #0D47A1;
        margin-top: 30px;
    }
    .upload-box {
        border: 2px dashed #2196F3;
        border-radius: 15px;
        padding: 15px;
        background-color: #E3F2FD;
        text-align: center;
        color: #0D47A1;
        font-weight: 500;
    }
    .chat-box {
        border-radius: 15px;
        background-color: #FFFFFF;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        padding: 15px;
        margin-top: 15px;
        height: 300px;
        overflow-y: auto;
    }
    .chat-input {
        margin-top: 10px;
        border-radius: 20px;
        border: 1px solid #90CAF9;
    }
    .footer {
        text-align: center;
        font-size: 14px;
        color: #1565C0;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown('<h1 class="title">💼 Nuvora AI Career Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Chat with your AI Career Coach & Resume Analyzer</p>', unsafe_allow_html=True)

# ==================== SECTION 1 - RESUME MATCH & SKILLS ====================
st.markdown('<h3 class="section-header">📊 Resume Match & Skill Analysis</h3>', unsafe_allow_html=True)

job_desc = st.text_area("📄 Paste Job Description", placeholder="Paste the job description here...", height=150)

uploaded_files = st.file_uploader("📂 Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_skills(text):
    common_skills = ['python', 'java', 'c++', 'sql', 'excel', 'machine learning', 'deep learning', 'nlp',
                     'power bi', 'tableau', 'communication', 'leadership', 'teamwork', 'data analysis']
    found = [skill for skill in common_skills if re.search(rf'\\b{skill}\\b', text.lower())]
    return list(set(found))

if uploaded_files and job_desc:
    for file in uploaded_files:
        st.subheader(f"📘 Analyzing {file.name}...")
        resume_text = extract_text_from_pdf(file)

        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_desc)

        matched = [skill for skill in resume_skills if skill in job_skills]
        missing = [skill for skill in job_skills if skill not in resume_skills]

        st.progress(len(matched) / len(job_skills) if job_skills else 0)

        st.success(f"✅ Match Percentage: {round((len(matched)/len(job_skills))*100, 2) if job_skills else 0}%")
        st.info(f"**Skills Found in Resume:** {', '.join(resume_skills) if resume_skills else 'None'}")
        st.warning(f"**Skills Missing for this Job:** {', '.join(missing) if missing else 'None'}")

# ==================== SECTION 2 - AI CHAT BOT ====================
st.markdown('<h3 class="section-header">💬 Ask Nuvora Anything</h3>', unsafe_allow_html=True)

# Chat box placeholder
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        st.markdown(f"<b>{msg['sender']}:</b> {msg['text']}", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

user_input = st.chat_input("Ask Nuvora about your career, skills, or resume...")

if user_input:
    # Simple mock response (can be replaced with OpenAI API call)
    response = f"Based on your resume, you should focus on enhancing your {', '.join(extract_skills(user_input)) or 'key technical'} skills."
    st.session_state.chat_history.append({"sender": "You", "text": user_input})
    st.session_state.chat_history.append({"sender": "Nuvora", "text": response})
    st.rerun()

# ==================== FOOTER ====================
st.markdown('<p class="footer">🚀 Powered by Nuvora AI | Smart Career Insights</p>', unsafe_allow_html=True)
