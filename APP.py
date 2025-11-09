import streamlit as st
import openai
import pdfplumber
import docx
import re

# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------
st.set_page_config(page_title="Nuvora AI Career Assistant", layout="wide")

# Sky Blue Background CSS
st.markdown("""
    <style>
    body {
        background-color: #e6f2ff;
    }
    .main {
        background-color: #e6f2ff;
    }
    div[data-testid="stSidebar"] {
        background-color: #b3daff;
    }
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
    }
    .user-msg {
        background: #d9f2d9;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 6px 0;
    }
    .bot-msg {
        background: #cce0ff;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 6px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD OPENAI API KEY FROM STREAMLIT SECRETS
# --------------------------------------------------
try:
    openai.api_key = st.secrets["openai"]["api_key"]
    ai_available = True
except Exception:
    ai_available = False

# --------------------------------------------------
# FUNCTION TO EXTRACT TEXT FROM RESUME
# --------------------------------------------------
def extract_text_from_resume(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

# --------------------------------------------------
# FUNCTION TO PERFORM ATS ANALYSIS
# --------------------------------------------------
def analyze_resume_for_ats(text):
    score = 0
    keywords = ["python", "data", "machine learning", "ai", "sql", "excel", "communication", "team", "project"]
    found = [kw for kw in keywords if kw.lower() in text.lower()]
    score = int((len(found) / len(keywords)) * 100)
    missing = [kw for kw in keywords if kw not in found]
    return score, found, missing

# --------------------------------------------------
# FUNCTION TO EXTRACT PROJECTS
# --------------------------------------------------
def extract_projects_from_resume(text):
    project_patterns = [
        r'(?i)(projects?|academic projects?|personal projects?|internship projects?|major projects?|minor projects?)[:\-]?\s*(.*)',
        r'(?i)(\b[A-Z][a-z]+ Project\b.*?)\n',
        r'(?i)(?:\*\*|##|###)?\s*Project\s*[:\-]?\s*(.*)'
    ]

    matches = []
    for pattern in project_patterns:
        found = re.findall(pattern, text)
        if found:
            for f in found:
                if isinstance(f, tuple):
                    matches.append(f[1])
                else:
                    matches.append(f)
    return list(set(matches))

# --------------------------------------------------
# SIDEBAR MENU
# --------------------------------------------------
st.sidebar.title("🧭 Navigation")
menu = ["🏠 Home", "📊 ATS Resume Analysis", "💼 Resume Project Extraction", "🤖 Ask Nuvora (AI Chat)"]
choice = st.sidebar.radio("Go to:", menu)

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------
if choice == "🏠 Home":
    st.title("💎 Nuvora AI Career Assistant")
    st.markdown("""
        Welcome to **Nuvora**, your smart AI-powered career companion.  
        Analyze your resume, check ATS compatibility, extract project info,  
        and chat with our AI assistant for career insights.
    """)

# --------------------------------------------------
# ATS ANALYSIS
# --------------------------------------------------
elif choice == "📊 ATS Resume Analysis":
    st.title("📄 ATS Resume Analyzer")

    uploaded_file = st.file_uploader("Upload your resume (PDF/DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        text = extract_text_from_resume(uploaded_file)
        score, found, missing = analyze_resume_for_ats(text)

        st.subheader("✅ ATS Match Report")
        st.metric("ATS Score", f"{score}%")

        st.write("**Matched Keywords:**")
        st.success(", ".join(found) if found else "None")

        st.write("**Missing Keywords:**")
        st.warning(", ".join(missing) if missing else "None")

# --------------------------------------------------
# PROJECT EXTRACTION
# --------------------------------------------------
elif choice == "💼 Resume Project Extraction":
    st.title("💼 Resume Project Extraction")

    uploaded_file = st.file_uploader("Upload your resume (PDF/DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        text = extract_text_from_resume(uploaded_file)
        projects = extract_projects_from_resume(text)

        if projects:
            st.subheader("📁 Detected Projects")
            for i, project in enumerate(projects, 1):
                st.markdown(f"**{i}. {project.strip()}**")
        else:
            st.warning("⚠️ No clear projects detected. Try checking your resume formatting or section titles.")

# --------------------------------------------------
# --------------------------------------------------🤖 Ask Nuvora (AI Chat)
elif choice == "🤖 Ask Nuvora (AI Chat)":
    st.title("🤖 Ask Nuvora")

    if not ai_available:
        st.warning("⚠️ OpenAI API key not found. Chat feature is disabled.")
    else:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.text_input("Ask your career questions or advice here:")

        if st.button("Send"):
            if user_input:
                # Append user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                # Call OpenAI API
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=st.session_state.chat_history,
                        temperature=0.7,
                        max_tokens=500
                    )

                    bot_message = response['choices'][0]['message']['content']
                    st.session_state.chat_history.append({"role": "assistant", "content": bot_message})
                except Exception as e:
                    st.error(f"❌ API Error: {e}")

        # Display chat
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f'<div class="user-msg">{chat["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg">{chat["content"]}</div>', unsafe_allow_html=True)
