import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt

# ==============================
# 🎨 PAGE CONFIGURATION
# ==============================
st.set_page_config(page_title="💫 Nuvora Resume Scanner", page_icon="💼", layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
body, .stApp { background-color: #0A0F24; color: #EAEAEA; font-family: 'Poppins', sans-serif; }
.title { font-size: 42px; font-weight: 800; background: linear-gradient(90deg, #00C6FF, #0072FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
.card { background: linear-gradient(145deg, #1B1F3B, #101325);
    padding: 25px; border-radius: 20px; margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
.mini-card {
    background: #13193B;
    padding: 20px; border-radius: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    text-align: center;
}
.stButton>button { background: linear-gradient(90deg, #0072FF, #00C6FF);
    color: white; border-radius: 10px; border: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================
# 📂 FILE HANDLING FUNCTIONS
# ==============================
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        return ""

def calculate_ats_score(resume_text, job_desc):
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    jd_words = set(re.findall(r'\b\w+\b', job_desc.lower()))
    matched = resume_words.intersection(jd_words)
    score = (len(matched) / len(jd_words)) * 100 if len(jd_words) > 0 else 0
    missing = jd_words - resume_words
    return round(score, 2), matched, missing

# ==============================
# 🧭 SIDEBAR
# ==============================
st.sidebar.title("💫 Nuvora AI")
page = st.sidebar.radio("Navigate to:", ["🏠 Home", "📊 Resume Scanner", "🎓 Career Chat"])
st.sidebar.caption("Final Year Project – Pearl Sethi")

# ==============================
# 🏠 HOME
# ==============================
if page == "🏠 Home":
    st.markdown('<p class="title">💫 Nuvora AI – Resume Intelligence Dashboard</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
    <h3>🚀 Project Overview</h3>
    <ul>
    <li>ATS Resume Scoring</li>
    <li>Skill Gap Analysis</li>
    <li>Education & Career Chat Assistant</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# 📊 RESUME SCANNER
# ==============================
elif page == "📊 Resume Scanner":
    st.markdown('<p class="title">📈 Resume & Job Description Analyzer</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        resume_file = st.file_uploader("📄 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

    with col2:
        jd_option = st.selectbox("🎯 Choose Job Description",
            ["-- Select --", "Data Analyst", "Data Scientist", "Web Developer", "Software Developer"])

        jd_presets = {
            "Data Analyst": "Python SQL Excel Power BI Tableau Statistics Data Visualization",
            "Data Scientist": "Python Machine Learning Statistics Pandas NumPy Scikit-learn",
            "Web Developer": "HTML CSS JavaScript React Node Git APIs",
            "Software Developer": "Java C++ OOP Data Structures Algorithms Databases"
        }

        job_desc = jd_presets.get(jd_option, "")

    if resume_file and job_desc:
        resume_text = extract_text(resume_file)
        score, matched, missing = calculate_ats_score(resume_text, job_desc)

        st.markdown("<div class='card'><h4>📊 ATS Result</h4>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"<div class='mini-card'><h3>{score}%</h3><p>ATS Score</p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='mini-card'><h3>{len(matched)}</h3><p>Matched Skills</p></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='mini-card'><h3>{len(missing)}</h3><p>Missing Skills</p></div>", unsafe_allow_html=True)

        fig, ax = plt.subplots()
        ax.bar(["ATS Score"], [score])
        ax.set_ylim(0, 100)
        st.pyplot(fig)

        st.markdown("<div class='card'><b>Missing Keywords:</b></div>", unsafe_allow_html=True)
        st.write(", ".join(list(missing)[:10]))

# ==============================
# 🎓 EDUCATION & CAREER CHAT
# ==============================
elif page == "🎓 Career Chat":
    st.markdown('<p class="title">🎓 Career & Education Chat</p>', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Student Query:", placeholder="Example: Data Analyst skills")

    if user_input:
        st.session_state.chat_history.append(("Student", user_input))
        msg = user_input.lower()

        if "data analyst" in msg:
            reply = "Data Analyst needs Python, SQL, Excel, Power BI/Tableau, Statistics and projects."
        elif "data scientist" in msg:
            reply = "Data Scientist needs ML, Python, Statistics, Pandas, NumPy and higher studies."
        elif "web developer" in msg:
            reply = "Web Developer needs HTML, CSS, JS, React, backend basics and projects."
        elif "resume" in msg:
            reply = "Student resume should include skills, projects, internships and ATS keywords."
        elif "interview" in msg:
            reply = "Prepare core subjects, project explanation and practice aptitude."
        elif "skill" in msg:
            reply = "Learn one skill deeply, practice projects and maintain GitHub."
        else:
            reply = "Ask education or career related questions only."

        st.session_state.chat_history.append(("Nuvora 🎓", reply))

    for sender, msg in st.session_state.chat_history:
        st.markdown(f"<div class='card'><b>{sender}:</b><br>{msg}</div>", unsafe_allow_html=True)

# ==============================
# 🧾 FOOTER
# ==============================
st.markdown("<hr><p style='text-align:center;color:gray;'>Developed by Pearl Sethi</p>", unsafe_allow_html=True)
