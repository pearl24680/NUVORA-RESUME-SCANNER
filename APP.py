import streamlit as st
import pdfplumber
import docx
import re

# ==============================
# 🎨 PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="💫 Nuvora Resume Scanner",
    page_icon="💼",
    layout="wide"
)

# ==============================
# 🎨 CUSTOM CSS
# ==============================
st.markdown("""
<style>
body, .stApp {
    background-color: #0A0F24;
    color: #EAEAEA;
    font-family: Poppins;
}

/* Title Gradient */
.title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #00C6FF, #0072FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}

/* Cards */
.card {
    background: linear-gradient(145deg, #1B1F3B, #101325);
    padding: 25px;
    border-radius: 20px;
    margin-bottom: 15px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #0072FF, #00C6FF);
    color: white; 
    font-weight: bold;
}

/* Chat bubbles */
.user-msg {
    background-color: #0072FF;
    color: white;
    padding: 12px 15px;
    border-radius: 20px 20px 0 20px;
    text-align: right;
    max-width: 70%;
    margin-left: 30%;
    margin-bottom: 10px;
    word-wrap: break-word;
}
.bot-msg {
    background-color: #1B1F3B;
    color: #EAEAEA;
    padding: 12px 15px;
    border-radius: 20px 20px 20px 0;
    max-width: 70%;
    margin-right: 30%;
    margin-bottom: 10px;
    word-wrap: break-word;
}

/* Scrollable chat container */
.chat-container {
    height: 400px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #333;
    border-radius: 10px;
    background-color: #0A0F24;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 📂 FILE FUNCTIONS
# ==============================
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text(file):
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    return ""

def calculate_ats_score(resume, jd):
    resume_words = set(re.findall(r"\w+", resume.lower()))
    jd_words = set(re.findall(r"\w+", jd.lower()))
    match = resume_words.intersection(jd_words)
    score = (len(match) / len(jd_words)) * 100 if jd_words else 0
    return round(score, 2), match, jd_words - match

# ==============================
# 🧭 SIDEBAR
# ==============================
st.sidebar.title("💫 Nuvora AI")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📊 Resume Scanner", "🎓 Career & Course Chat"]
)
st.sidebar.caption("Final Year Project | Pearl & Vasu")

# ==============================
# 🏠 HOME
# ==============================
if page == "🏠 Home":
    st.markdown("<p class='title'>💫 Nuvora AI</p>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <h3>📌 Project Overview</h3>
        <ul>
            <li>ATS Resume Scanner</li>
            <li>Career Guidance Chat</li>
            <li>Full Course Roadmaps</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# 📊 RESUME SCANNER
# ==============================
elif page == "📊 Resume Scanner":
    st.markdown("<p class='title'>📊 Resume Analyzer</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
    with col2:
        jd = st.selectbox(
            "Select Job Role",
            ["Data Analyst", "Data Scientist", "Web Developer"]
        )

    jd_data = {
        "Data Analyst": "python sql excel statistics power bi tableau",
        "Data Scientist": "python machine learning statistics pandas numpy",
        "Web Developer": "html css javascript react node"
    }

    if resume_file:
        resume_text = extract_text(resume_file)
        score, matched, missing = calculate_ats_score(resume_text, jd_data[jd])
        st.markdown(f"<div class='card'><h3>ATS Score: {score}%</h3></div>",
                    unsafe_allow_html=True)

# ==============================
# 🎓 CAREER & COURSE CHAT
# ==============================
elif page == "🎓 Career & Course Chat":
    st.markdown("<p class='title'>🎓 Nuvora Education Chat</p>", unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    # Scrollable chat container
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for role, text in st.session_state.history:
        if role == "Student":
            st.markdown(f"<div class='user-msg'>{text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'>{text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Input box always at the bottom
    user_input = st.text_input("Type your message here...", key="input")

    if user_input:
        msg = user_input.lower()
        st.session_state.history.append(("Student", user_input))

        # ===== DATA SCIENCE =====
        if "data science" in msg or "data scientist" in msg:
            reply = (
                "🎓 FULL DATA SCIENCE COURSE\n\n"
                "📘 Phase 1 – Basics\n"
                "- Python Basics\n- Statistics\n- Linear Algebra\n\n"
                "📘 Phase 2 – Data Handling\n"
                "- Pandas\n- NumPy\n- Data Cleaning\n\n"
                "📘 Phase 3 – Machine Learning\n"
                "- Regression\n- Classification\n- Clustering\n\n"
                "📘 Phase 4 – Advanced\n"
                "- Deep Learning\n- NLP\n- Projects"
            )

        # ===== DATA ANALYST =====
        elif "data analyst" in msg or "data analysis" in msg:
            reply = (
                "🎓 FULL DATA ANALYST COURSE\n\n"
                "📘 Phase 1\n- Excel\n- Statistics\n\n"
                "📘 Phase 2\n- SQL\n- Python\n\n"
                "📘 Phase 3\n- Power BI / Tableau\n- Dashboards\n\n"
                "📘 Phase 4\n- Real-world projects"
            )

        # ===== WEB DEVELOPER =====
        elif "web developer" in msg or "web development" in msg:
            reply = (
                "🎓 FULL WEB DEVELOPMENT COURSE\n\n"
                "📘 Frontend\n- HTML\n- CSS\n- JavaScript\n\n"
                "📘 Backend\n- Node.js\n- Databases\n\n"
                "📘 Projects\n- Portfolio websites"
            )

        # ===== RESUME =====
        elif "resume" in msg or "cv" in msg:
            reply = (
                "📄 RESUME GUIDELINES\n"
                "- 1–2 pages\n"
                "- Skills + Projects\n"
                "- ATS-friendly format"
            )

        # ===== INTERVIEW =====
        elif "interview" in msg:
            reply = (
                "🎤 INTERVIEW PREP\n"
                "- Revise concepts\n"
                "- Explain projects\n"
                "- Practice mock interviews"
            )

        # ===== GREETING =====
        elif "hi" in msg or "hello" in msg:
            reply = "👋 Hello! Ask me about courses, skills, or career paths."

        else:
            reply = (
                "ℹ️ Ask education-related queries only:\n"
                "- Data Science\n- Data Analyst\n- Web Development\n"
                "- Resume\n- Interview"
            )

        st.session_state.history.append(("Nuvora 🎓", reply))
        st.experimental_rerun()  # Refresh page to show new messages at bottom

# ==============================
# FOOTER
# ==============================
st.markdown(
    "<hr><center>Developed with ❤️ by Pearl & Vasu</center>",
    unsafe_allow_html=True
)
