import streamlit as st
import google.generativeai as genai
import pdfplumber
import re

st.set_page_config(page_title="Nuvora AI - Resume & Career Assistant", page_icon="💼", layout="wide")

# --- Custom CSS ---
page_bg = """
<style>
body {
    background-color: #E6F0FF;
    color: #000000;
    font-family: 'Segoe UI', sans-serif;
}
div[data-testid="stChatMessage"] {
    background: white;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
}
.stChatMessage[data-testid="stChatMessage-user"] {
    background-color: #D6EAF8;
}
h1, h2, h3 {
    color: #004080;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ================================
# ⚙️ Gemini API Setup
# ================================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ Gemini API key not found! Please add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# ================================
# 💬 Chat History
# ================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ================================
# 📄 Resume Extraction
# ================================
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_projects(resume_text):
    project_pattern = r"(?:Projects?|Project Title|Major Project|Minor Project)[:\-–\s]*([\s\S]*?)(?:\n[A-Z][a-zA-Z\s]+:|\Z)"
    projects = re.findall(project_pattern, resume_text, re.IGNORECASE)
    return [p.strip() for p in projects if len(p.strip()) > 10]

def ats_analysis(resume_text):
    prompt = f"""
You are an ATS (Applicant Tracking System) analyzer.
Analyze this resume text and give:
1. Overall ATS score (out of 100)
2. Strengths
3. Weaknesses
4. Suggestions to improve ATS ranking
Resume:
{resume_text}
"""
    response = model.generate_content(prompt)
    return response.text

# ================================
# 🧠 Sidebar - Resume Upload
# ================================
st.sidebar.header("📤 Upload Resume")
uploaded_file = st.sidebar.file_uploader("Upload your resume (PDF)", type=["pdf"])

resume_text = ""
projects = []
ats_report = ""

if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)
    if resume_text:
        st.sidebar.success("✅ Resume uploaded successfully!")

        with st.expander("📊 View Extracted Text"):
            st.text_area("Extracted Resume Text", resume_text[:2000], height=300)

        projects = extract_projects(resume_text)
        ats_report = ats_analysis(resume_text)

# ================================
# 🌟 Main UI
# ================================
st.title("💼 Nuvora AI — Resume & Career Assistant")
st.markdown("### Hi! I'm Nuvora, your **AI career guide**. Ask me about your resume, projects, or interviews!")

col1, col2 = st.columns([1, 1])

with col1:
    if projects:
        st.subheader("📁 Projects Found in Resume")
        for i, proj in enumerate(projects, 1):
            st.markdown(f"**{i}.** {proj}")
    else:
        st.info("No projects detected yet. Upload your resume to extract them.")

with col2:
    if ats_report:
        st.subheader("📊 ATS Analysis Report")
        st.markdown(ats_report)
    else:
        st.info("Upload a resume to generate ATS insights.")

# ================================
# 💬 Chat Section
# ================================
st.markdown("---")
st.subheader("💬 Ask Nuvora — AI Career Chatbot")

# Display chat history
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# User input
user_input = st.chat_input("Ask about your resume, projects, or interview tips...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = model.generate_content(user_input)
        ai_reply = response.text
    except Exception as e:
        ai_reply = "⚠️ Sorry, I'm having trouble connecting to Gemini right now."

    st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
    with st.chat_message("assistant"):
        st.markdown(ai_reply)

# ================================
# 🔁 Clear Chat Button
# ================================
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()
