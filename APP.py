import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt

# ==============================
# 🎨 PAGE CONFIGURATION
# ==============================
st.set_page_config(page_title="Nuvora AI - Resume & Career Assistant", page_icon="💫", layout="wide")

# --- Dark Premium Theme CSS ---
st.markdown("""
    <style>
    body { background-color: #0A0F24; color: #EAEAEA; font-family: 'Poppins', sans-serif; }
    .stApp { background-color: #0A0F24; color: #EAEAEA; }
    .title { font-size: 42px; font-weight: 800; background: linear-gradient(90deg, #00C6FF, #0072FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    .card { background: linear-gradient(145deg, #1B1F3B, #101325); padding: 25px; border-radius: 20px;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.4); }
    .stButton>button { background: linear-gradient(90deg, #0072FF, #00C6FF);
        color: white; border-radius: 10px; border: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==============================
# 📂 HELPER FUNCTIONS
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
        return "Unsupported file format!"

def calculate_ats_score(resume_text, job_desc):
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    jd_words = set(re.findall(r'\b\w+\b', job_desc.lower()))
    matched = resume_words.intersection(jd_words)
    score = (len(matched) / len(jd_words)) * 100 if len(jd_words) > 0 else 0
    missing = jd_words - resume_words
    return round(score, 2), matched, missing

# ==============================
# 🧠 OFFLINE LOCAL CHATBOT
# ==============================
def local_ai_reply(prompt):
    prompt = prompt.lower()
    if "hello" in prompt or "hi" in prompt:
        return "👋 Hi there! I'm Nuvora — your resume and career assistant."
    elif "resume" in prompt:
        return "📄 You can upload your resume and job description to get ATS analysis instantly!"
    elif "data science" in prompt:
        return "🧠 For Data Science roles, focus on Python, Pandas, NumPy, ML models, and visualization tools like Power BI."
    elif "web" in prompt or "developer" in prompt:
        return "💻 Web Developers should highlight HTML, CSS, JS, React, and backend frameworks like Node or Django."
    elif "ai" in prompt:
        return "🤖 AI Engineers often work with ML frameworks like TensorFlow, PyTorch, and deep learning algorithms."
    elif "help" in prompt:
        return "💡 You can ask me about resumes, interview skills, or best practices for tech jobs!"
    else:
        return "💬 I’m Nuvora! Ask me about resumes, coding, or job skills — I’ll try to help!"

# ==============================
# 🧭 SIDEBAR NAVIGATION
# ==============================
st.sidebar.title("💫 Nuvora AI")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate to:", ["🏠 Home", "📊 ATS Resume Scanner", "💬 Career Chat"])
st.sidebar.markdown("---")
st.sidebar.caption("Developed by Team Nuvora 💙")

# ==============================
# 🏠 HOME
# ==============================
if page == "🏠 Home":
    st.markdown('<p class="title">💫 Nuvora AI - Resume & Career Assistant</p>', unsafe_allow_html=True)
    st.markdown("""
        <div class='card'>
        <h3>🚀 Welcome to Nuvora!</h3>
        <p>Upload your Resume & compare it with a Job Description to get:</p>
        <ul>
        <li>🎯 ATS Score</li>
        <li>📊 Skill Match & Missing Keywords</li>
        <li>💬 AI Career Guidance</li>
        </ul>
        <p>Switch to "📊 ATS Resume Scanner" to start!</p>
        </div>
    """, unsafe_allow_html=True)

# ==============================
# 📊 ATS RESUME SCANNER
# ==============================
elif page == "📊 ATS Resume Scanner":
    st.markdown('<p class="title">📈 ATS Resume Analyzer</p>', unsafe_allow_html=True)
    st.write("Upload your Resume & choose or upload a Job Description to see how well they match.")

    col1, col2 = st.columns(2)

    with col1:
        resume_file = st.file_uploader("📄 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

    with col2:
        jd_option = st.selectbox("🎯 Choose a Job Description", 
                                 ["-- Select JD --", "Data Scientist", "Web Developer", "AI Engineer", "Software Developer", "Custom Upload"])
        
        jd_presets = {
            "Data Scientist": """Proficiency in Python, Pandas, NumPy, Machine Learning, Data Visualization, Scikit-learn, SQL, Deep Learning, and Model Deployment.""",
            "Web Developer": """Strong in HTML, CSS, JavaScript, React, Node.js, REST APIs, Git, and Responsive Web Design.""",
            "AI Engineer": """Experience with TensorFlow, PyTorch, NLP, Machine Learning, Python, and Deep Learning frameworks.""",
            "Software Developer": """Knowledge of Java, C++, OOP, Data Structures, Algorithms, Databases, and Problem Solving."""
        }

        job_desc = ""
        if jd_option in jd_presets:
            job_desc = jd_presets[jd_option]
        elif jd_option == "Custom Upload":
            jd_file = st.file_uploader("🧾 Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
            if jd_file:
                job_desc = jd_file.read().decode("utf-8") if jd_file.name.endswith(".txt") else extract_text(jd_file)

    # --- Perform Analysis ---
    if resume_file and job_desc:
        resume_text = extract_text(resume_file)
        score, matched, missing = calculate_ats_score(resume_text, job_desc)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("🎯 ATS Score", f"{score}%")
        col2.metric("✅ Matched", len(matched))
        col3.metric("⚠️ Missing", len(missing))
        st.markdown("</div>", unsafe_allow_html=True)

        # Graph
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.bar(["Match %"], [score], color="#00C6FF")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Selection Probability")
        ax.set_facecolor("#0A0F24")
        fig.patch.set_facecolor("#0A0F24")
        st.pyplot(fig)

        st.markdown("### ✅ Matched Skills")
        st.success(", ".join(list(matched)) if matched else "No matched skills found.")

        st.markdown("### ⚠️ Missing Skills (Improve These)")
        st.warning(", ".join(list(missing)) if missing else "Perfect Match!")

        st.markdown("### 💡 Smart Suggestions for This Role")
        st.info("Add relevant projects, mention metrics (like accuracy %), and list strong tools like Python, SQL, and visualization skills.")

# ==============================
# 💬 CAREER CHAT
# ==============================
elif page == "💬 Career Chat":
    st.markdown('<p class="title">💬 Ask Nuvora AI</p>', unsafe_allow_html=True)
    user_input = st.text_input("💭 You:", placeholder="Ask about skills, resume, or job roles...")

    if user_input:
        with st.spinner("Thinking... 💫"):
            reply = local_ai_reply(user_input)
        st.markdown(f"<div class='card'><b>Nuvora 💫:</b><br>{reply}</div>", unsafe_allow_html=True)

# ==============================
# 🧾 FOOTER
# ==============================
st.markdown("""
<hr>
<p style='text-align:center; color:gray;'>
Developed with ❤️ by <b>pearl</b> | Resume Intelligence & Career Insights
</p>
""", unsafe_allow_html=True)
