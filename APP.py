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
        return "Unsupported file format!"

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
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate to:", ["🏠 Home", "📊 Resume Scanner", "💬 Chat Assistant"])
st.sidebar.markdown("---")
st.sidebar.caption("Developed by Pearl and Vasu (Final Year Project)")

# ==============================
# 🏠 HOME
# ==============================
if page == "🏠 Home":
    st.markdown('<p class="title">💫 Nuvora AI - Resume Intelligence Dashboard</p>', unsafe_allow_html=True)
    st.markdown("""
        <div class='card'>
        <h3>🚀 Welcome to Nuvora Resume Scanner</h3>
        <p>Compare your resume with job descriptions and get:</p>
        <ul>
        <li>🎯 ATS Score (Resume Match %)</li>
        <li>📊 Top & Missing Skills</li>
        <li>💬 Smart Resume Suggestions</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

# ==============================
# 📊 ATS RESUME SCANNER
# ==============================
elif page == "📊 Resume Scanner":
    st.markdown('<p class="title">📈 Resume & Job Description Analyzer</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        resume_file = st.file_uploader("📄 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

    with col2:
        jd_option = st.selectbox("🎯 Choose a Job Description", 
                                 ["-- Select JD --", "Data Scientist", "Web Developer", "AI Engineer", "Software Developer", "Custom Upload"])
        
        jd_presets = {
            "Data Scientist": "Python, Pandas, NumPy, Machine Learning, Scikit-learn, SQL, Deep Learning, Data Visualization, Model Deployment",
            "Web Developer": "HTML, CSS, JavaScript, React, Node.js, REST APIs, Git, Responsive Web Design",
            "AI Engineer": "TensorFlow, PyTorch, NLP, Machine Learning, Python, Deep Learning frameworks",
            "Software Developer": "Java, C++, OOP, Data Structures, Algorithms, Databases, Problem Solving"
        }

        job_desc = ""
        if jd_option in jd_presets:
            job_desc = jd_presets[jd_option]
        elif jd_option == "Custom Upload":
            jd_file = st.file_uploader("🧾 Upload Job Description (TXT/PDF/DOCX)", type=["txt", "pdf", "docx"])
            if jd_file:
                if jd_file.name.endswith(".txt"):
                    job_desc = jd_file.read().decode("utf-8")
                else:
                    job_desc = extract_text(jd_file)

    # Analysis
    if resume_file and job_desc:
        resume_text = extract_text(resume_file)
        score, matched, missing = calculate_ats_score(resume_text, job_desc)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("🎯 ATS Score", f"{score}%")
        col2.metric("✅ Matched", len(matched))
        col3.metric("⚠️ Missing", len(missing))
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Mini White ATS Bar Graph ---
        fig, ax = plt.subplots(figsize=(1.2, 1.2))  # smaller compact graph
        ax.bar(["ATS Match %"], [score], color="#007BFF", width=0.3)
        ax.set_facecolor("white")
        fig.patch.set_facecolor("white")

        # Clean minimal style
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        ax.set_ylim(0, 100)
        ax.text(0, score + 3, f"{score}%", ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

        st.pyplot(fig, transparent=True)

        # Missing Keywords Section
        st.markdown("<div class='card'><h4>🔍 Missing Keywords:</h4>", unsafe_allow_html=True)
        if missing:
            st.write(", ".join(list(missing)[:10]))
        else:
            st.write("✅ Your resume covers all key skills!")
        st.markdown("</div>", unsafe_allow_html=True)

        # Suggestions
        st.info(f"💡 Suggestion: Add missing keywords related to the {jd_option} role to boost your ATS score.")

# ==============================
# 💬 CHAT ASSISTANT
# ==============================
elif page == "💬 Chat Assistant":
    st.markdown('<p class="title">💬 Nuvora Chat</p>', unsafe_allow_html=True)
    st.markdown("<div class='card'>Chat with Nuvora for resume tips, interview prep, and skill advice!</div>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("💭 You:", placeholder="Ask me anything about career or resume...")

    if user_input:
        st.session_state.chat_history.append(("You", user_input))

        # Simple Rule-Based AI
        if "resume" in user_input.lower():
            reply = "Your resume should highlight your technical skills, certifications, and relevant projects."
        elif "skill" in user_input.lower():
            reply = "Focus on Python, SQL, and data visualization tools like Power BI or Tableau for analytics roles."
        elif "interview" in user_input.lower():
            reply = "Prepare for HR and technical rounds. Be ready to explain your projects clearly."
        else:
            reply = "I'm your career buddy! Try asking about resume tips, interview advice, or skill growth."

        st.session_state.chat_history.append(("Nuvora 💫", reply))

    for sender, msg in st.session_state.chat_history:
        st.markdown(f"<div class='card'><b>{sender}:</b><br>{msg}</div>", unsafe_allow_html=True)

# ==============================
# 🧾 FOOTER
# ==============================
st.markdown("<hr><p style='text-align:center;color:gray;'>Developed with ❤️ by Pearl and Vasu</p>", unsafe_allow_html=True)
