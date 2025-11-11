import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="💖 Nuvora AI Job Assistant", layout="wide")

# ---------------------------------------------------
# CSS STYLING (Pink-Purple Theme)
# ---------------------------------------------------
st.markdown("""
<style>
body { background-color: #fdf6ff; font-family: 'Arial', sans-serif; }
div[data-testid="stSidebar"] { background-color: #f3d7ff; }
.section {
    background:white;
    padding:25px;
    border-radius:15px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.1);
    margin-bottom:25px;
}
.metric-box {
    background: linear-gradient(135deg, #f48fb1, #ba68c8);
    color:white;
    padding:20px;
    border-radius:12px;
    text-align:center;
    font-weight:bold;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.metric-box span { font-size:32px; display:block; margin-top:5px; font-weight:bold; }
.project-box {
    background: #fbe8ff;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
}
.user-msg {
    background:#ffd6f7;
    border-radius:8px;
    padding:8px 12px;
    margin:6px 0;
}
.bot-msg {
    background:#e1c4ff;
    border-radius:8px;
    padding:8px 12px;
    margin:6px 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------
def extract_text(uploaded_file):
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

def analyze_resume(resume_text, jd_text=""):
    resume_text = resume_text.lower()
    jd_text = jd_text.lower() if jd_text else ""

    ds_keywords = [
        "python","machine learning","data analysis","sql","excel","pandas",
        "numpy","deep learning","statistics","power bi","tableau",
        "visualization","modeling","ai","communication","teamwork",
        "data cleaning","eda","nlp","classification","regression"
    ]

    found = [kw for kw in ds_keywords if kw in resume_text]
    missing = [kw for kw in ds_keywords if kw not in found]
    ats_score = int((len(found)/len(ds_keywords))*100)

    jd_keywords = []
    if jd_text:
        jd_keywords = list(set(re.findall(r'\b[a-zA-Z]{4,}\b', jd_text)))

    return ats_score, found, missing, jd_keywords

def extract_projects(resume_text):
    patterns = [
        r'(?i)(projects?|academic projects?|personal projects?|internship projects?)[:\-]?\s*(.*)',
        r'(?i)(?:\*\*|##|###)?\s*Project\s*[:\-]?\s*(.*)'
    ]
    matches = []
    for pat in patterns:
        found = re.findall(pat, resume_text)
        for f in found:
            matches.append(f[1] if isinstance(f, tuple) else f)
    return list(set(matches))

def plot_ats(ats_score):
    fig, ax = plt.subplots(figsize=(4,2))
    ax.barh(["Selection Probability"], [ats_score], color="#ba68c8")
    ax.set_xlim(0,100)
    ax.set_xlabel("ATS Score (%)")
    ax.xaxis.set_major_formatter(PercentFormatter())
    for i, v in enumerate([ats_score]):
        ax.text(v+2, i, f"{v}%", va='center', fontweight='bold', color='#4a148c')
    st.pyplot(fig)

# ---------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------
st.sidebar.title("🧭 Nuvora AI Assistant")
menu = ["🏠 Dashboard","📊 ATS Analysis","💼 Project Extraction","🤖 AI Career Chat"]
choice = st.sidebar.radio("Navigate:", menu)

# ---------------------------------------------------
# GLOBAL FILE UPLOAD
# ---------------------------------------------------
st.sidebar.subheader("📂 Upload Files")
resume_file = st.sidebar.file_uploader("Resume (PDF/DOCX)", type=["pdf","docx"])
jd_file = st.sidebar.file_uploader("Job Description (optional)", type=["pdf","docx","txt"])

resume_text, jd_text = "", ""
if resume_file:
    resume_text = extract_text(resume_file)
if jd_file:
    if jd_file.name.endswith(".txt"):
        jd_text = jd_file.read().decode("utf-8")
    else:
        jd_text = extract_text(jd_file)

# ---------------------------------------------------
# 1️⃣ DASHBOARD
# ---------------------------------------------------
if choice == "🏠 Dashboard":
    st.title("💖 Nuvora AI Career Dashboard")
    if resume_file:
        ats_score, found, missing, jd_keywords = analyze_resume(resume_text,jd_text)
        projects = extract_projects(resume_text)

        col1,col2,col3 = st.columns(3)
        col1.markdown(f"<div class='metric-box'>📊 ATS Score<span>{ats_score}%</span></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='metric-box'>✅ Matched Keywords<span>{len(found)}</span></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='metric-box'>⚠️ Missing Keywords<span>{len(missing)}</span></div>", unsafe_allow_html=True)

        st.markdown("### 📈 Selection Probability")
        plot_ats(ats_score)

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("✅ Matched Keywords")
        st.write(", ".join(found))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("⚠️ Missing Keywords")
        st.write(", ".join(missing) if missing else "None! 🎉")
        st.markdown("</div>", unsafe_allow_html=True)

        if jd_keywords:
            st.markdown("<div class='section'>", unsafe_allow_html=True)
            st.subheader("📋 Job Description Keywords")
            st.write(", ".join(jd_keywords[:40])+" ...")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("💼 Projects Detected")
        if projects:
            for i,p in enumerate(projects,1):
                st.markdown(f"<div class='project-box'>**{i}.** {p.strip()}</div>", unsafe_allow_html=True)
        else:
            st.write("No projects detected.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🧠 Suggestions for Improvement")
        st.markdown("""
        - Add missing **DS skills/tools**.
        - Highlight **quantifiable results** in projects.
        - Use **keywords from JD** for better ATS matching.
        - Keep resume clean, concise, and professional.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("👆 Upload your resume to generate dashboard.")

# ---------------------------------------------------
# 2️⃣ ATS ANALYSIS
# ---------------------------------------------------
elif choice == "📊 ATS Analysis":
    st.title("📊 Detailed ATS Analysis")
    if resume_file:
        ats_score, found, missing, jd_keywords = analyze_resume(resume_text,jd_text)
        st.metric("ATS Score", f"{ats_score}%")
        plot_ats(ats_score)
        st.subheader("Matched Keywords")
        st.write(", ".join(found))
        st.subheader("Missing Keywords")
        st.write(", ".join(missing))
    else:
        st.warning("Upload your resume to analyze.")

# ---------------------------------------------------
# 3️⃣ PROJECT EXTRACTION
# ---------------------------------------------------
elif choice == "💼 Project Extraction":
    st.title("💼 Resume Project Extraction")
    if resume_file:
        projects = extract_projects(resume_text)
        if projects:
            for i,p in enumerate(projects,1):
                st.markdown(f"<div class='project-box'>**{i}.** {p.strip()}</div>", unsafe_allow_html=True)
        else:
            st.warning("No projects detected.")
    else:
        st.info("Upload your resume to extract projects.")

# ---------------------------------------------------
# 4️⃣ AI CAREER CHAT
# ---------------------------------------------------
elif choice == "🤖 AI Career Chat":
    st.title("🤖 Nuvora AI Career Assistant Chat")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("💬 Ask about resume, ATS, projects, or careers:")
    if st.button("Send") and user_input.strip():
        st.session_state.chat_history.append({"role":"user","content":user_input})
        text_lower = user_input.lower()
        if "resume" in text_lower:
            response="Ensure your resume highlights key skills, tools, and measurable impact."
        elif "ats" in text_lower:
            response="ATS prefers clear formatting, keyword alignment, and concise structure."
        elif "python" in text_lower or "data" in text_lower:
            response="Include Python, pandas, numpy, EDA, visualization, ML & AI projects."
        elif "job" in text_lower:
            response="Target roles matching your skills and tailor resume for each JD."
        else:
            response="I can guide you about resume structure, ATS, or Data Science careers."
        st.session_state.chat_history.append({"role":"assistant","content":response})

    for chat in st.session_state.chat_history:
        if chat["role"]=="user":
            st.markdown(f"<div class='user-msg'>{chat['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'>{chat['content']}</div>", unsafe_allow_html=True)

