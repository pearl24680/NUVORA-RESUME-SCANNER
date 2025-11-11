import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt
import io

# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------
st.set_page_config(page_title="Nuvora AI Job Assistant", layout="wide")

# --------------------------------------------------
# CSS STYLING
# --------------------------------------------------
st.markdown("""
    <style>
    body {
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
# FILE TEXT EXTRACTION FUNCTIONS
# --------------------------------------------------
def extract_text(uploaded_file):
    """Extract text from PDF or DOCX"""
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
# ATS ANALYSIS FUNCTION
# --------------------------------------------------
def analyze_resume_with_jd(resume_text, jd_text):
    """Compare Resume vs Job Description"""
    # Normalize
    resume_text = resume_text.lower()
    jd_text = jd_text.lower()

    # Extract JD keywords
    jd_keywords = list(set(re.findall(r'\b[a-zA-Z]{3,}\b', jd_text)))
    jd_keywords = [word for word in jd_keywords if len(word) > 3]

    # Define target Data Science keywords
    ds_keywords = [
        "python", "machine learning", "data analysis", "sql", "excel", "pandas", "numpy",
        "deep learning", "statistics", "power bi", "tableau", "visualization", "modeling",
        "ai", "communication", "teamwork", "data cleaning", "eda", "nlp", "classification", "regression"
    ]

    # Match keywords
    found = [kw for kw in ds_keywords if kw in resume_text]
    missing = [kw for kw in ds_keywords if kw not in found]

    # ATS score
    ats_score = int((len(found) / len(ds_keywords)) * 100)

    return ats_score, found, missing, jd_keywords

# --------------------------------------------------
# PLOT FUNCTION
# --------------------------------------------------
def plot_ats_score(ats_score):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(["ATS Match"], [ats_score], color="#66b3ff")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Score (%)")
    ax.set_title("Resume Selection Probability")
    for i, v in enumerate([ats_score]):
        ax.text(i, v + 2, f"{v}%", ha='center', fontweight='bold')
    return fig

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
st.sidebar.title("🧭 Navigation")
menu = ["🏠 Home", "📊 Resume + JD Analysis", "💼 Extract Projects", "🤖 Ask AI Assistant"]
choice = st.sidebar.radio("Go to:", menu)

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------
if choice == "🏠 Home":
    st.title("💎 Nuvora AI Job Assistant")
    st.markdown("""
    Welcome to **Nuvora**, your smart AI career companion 🚀  
    Upload your **Resume & Job Description** to check ATS match, missing keywords,  
    and see your **selection probability graph**!
    """)

# --------------------------------------------------
# ATS ANALYSIS (Resume + JD)
# --------------------------------------------------
elif choice == "📊 Resume + JD Analysis":
    st.title("📊 Resume & Job Description Analyzer")

    resume_file = st.file_uploader("📄 Upload your Resume (PDF/DOCX)", type=["pdf", "docx"])
    jd_file = st.file_uploader("💼 Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

    if resume_file and jd_file:
        resume_text = extract_text(resume_file)
        jd_text = extract_text(jd_file) if jd_file.name.endswith((".pdf", ".docx")) else jd_file.read().decode("utf-8")

        ats_score, found, missing, jd_keywords = analyze_resume_with_jd(resume_text, jd_text)

        st.subheader("✅ ATS Analysis Summary")
        st.metric("ATS Score", f"{ats_score}%")

        st.pyplot(plot_ats_score(ats_score))

        st.write("### ✅ Matched Data Science Keywords")
        st.success(", ".join(found) if found else "None")

        st.write("### ⚠️ Missing Important Keywords")
        st.warning(", ".join(missing) if missing else "None")

        st.write("### 📋 Keywords Found in Job Description")
        st.info(", ".join(jd_keywords[:30]) + " ...")

        st.write("### 🧠 Suggestions")
        st.markdown("""
        - Add missing **Data Science** skills or tools.  
        - Include measurable project outcomes.  
        - Tailor your resume summary to reflect the **JD's language**.  
        - Use similar wording for skills mentioned in the JD.
        """)

# --------------------------------------------------
# PROJECT EXTRACTION
# --------------------------------------------------
elif choice == "💼 Extract Projects":
    st.title("💼 Resume Project Extraction")

    uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        text = extract_text(uploaded_file)
        project_patterns = [
            r'(?i)(projects?|academic projects?|personal projects?|internship projects?)[:\-]?\s*(.*)',
            r'(?i)(?:\*\*|##|###)?\s*Project\s*[:\-]?\s*(.*)'
        ]
        matches = []
        for pattern in project_patterns:
            found = re.findall(pattern, text)
            for f in found:
                if isinstance(f, tuple):
                    matches.append(f[1])
                else:
                    matches.append(f)
        if matches:
            st.subheader("📁 Detected Projects")
            for i, project in enumerate(set(matches), 1):
                st.markdown(f"**{i}. {project.strip()}**")
        else:
            st.warning("⚠️ No projects detected. Try reformatting your resume.")

# --------------------------------------------------
# AI CHAT ASSISTANT
# --------------------------------------------------
elif choice == "🤖 Ask AI Assistant":
    st.title("🤖 Nuvora Career Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("💬 Ask your career or resume question:")
    if st.button("Send") and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        text_lower = user_input.lower()

        if "resume" in text_lower:
            response = "Make sure your resume includes technical, analytical, and communication skills clearly."
        elif "job" in text_lower:
            response = "Apply for roles matching your skillset. Customize your resume for each JD."
        elif "data" in text_lower:
            response = "Focus on Data Analysis, SQL, and Visualization. Include measurable project impact."
        elif "ml" in text_lower or "machine learning" in text_lower:
            response = "Showcase ML projects, Kaggle work, and model performance metrics."
        else:
            response = "That’s interesting! I can guide you on resume building, ATS optimization, or career strategy."

        st.session_state.chat_history.append({"role": "assistant", "content": response})

    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="user-msg">{chat["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">{chat["content"]}</div>', unsafe_allow_html=True)
