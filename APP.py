import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="💫 Nuvora Resume Dashboard", page_icon="💼", layout="wide")

# ==============================
# CUSTOM CSS
# ==============================
st.markdown("""
<style>
body, .stApp { background-color: #0A0F24; color: #EAEAEA; font-family: 'Poppins', sans-serif; }
.title { font-size: 42px; font-weight: 800; background: linear-gradient(90deg, #00C6FF, #0072FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 20px; }
.card { background: linear-gradient(145deg, #1B1F3B, #101325);
    padding: 25px; border-radius: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
.mini-card { background: #13193B; padding: 20px; border-radius: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4); text-align: center; }
.user-msg { background-color: #0072FF; color: white; padding: 12px 15px; border-radius: 20px 20px 0 20px;
    text-align: right; max-width: 70%; margin-left: 30%; margin-bottom: 10px; word-wrap: break-word; }
.bot-msg { background-color: #1B1F3B; color: #EAEAEA; padding: 12px 15px; border-radius: 20px 20px 20px 0;
    max-width: 70%; margin-right: 30%; margin-bottom: 10px; word-wrap: break-word; }
.chat-container { height: 400px; overflow-y: auto; padding: 10px; border: 1px solid #333;
    border-radius: 10px; background-color: #0A0F24; margin-bottom: 10px; }
.stButton>button { background: linear-gradient(90deg, #0072FF, #00C6FF); color: white; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================
# FILE FUNCTIONS
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
    elif uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
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
# SIDEBAR
# ==============================
st.sidebar.title("💫 Nuvora AI")
page = st.sidebar.radio("Navigate:", ["🏠 Home", "📊 Resume Scanner", "💬 Chat Assistant"])
st.sidebar.caption("Developed by Pearl & Vasu | Final Year Project")

# ==============================
# HOME PAGE
# ==============================
if page == "🏠 Home":
    st.markdown('<p class="title">💫 Nuvora AI - Resume Dashboard</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
        <h3>🚀 Welcome!</h3>
        <p>Analyze your resume with job descriptions and get insights:</p>
        <ul>
        <li>🎯 ATS Score</li>
        <li>📊 Matched & Missing Skills</li>
        <li>💡 Resume Suggestions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# RESUME SCANNER DASHBOARD
# ==============================
elif page == "📊 Resume Scanner":
    st.markdown('<p class="title">📈 Resume Analyzer Dashboard</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        resume_file = st.file_uploader("📄 Upload Resume (PDF/DOCX/TXT)", type=["pdf","docx","txt"])
    with col2:
        jd_option = st.selectbox("🎯 Choose a Job Description", 
                                ["-- Select JD --","Data Scientist","Web Developer","AI Engineer","Software Developer","Custom Upload"])
        jd_presets = {
            "Data Scientist": "Python, Pandas, NumPy, Machine Learning, Scikit-learn, SQL, Deep Learning, Data Visualization, Model Deployment",
            "Web Developer": "HTML, CSS, JavaScript, React, Node.js, REST APIs, Git, Responsive Web Design",
            "AI Engineer": "TensorFlow, PyTorch, NLP, Machine Learning, Python, Deep Learning frameworks",
            "Software Developer": "Java, C++, OOP, Data Structures, Algorithms, Databases, Problem Solving"
        }
        job_desc = ""
        if jd_option in jd_presets:
            job_desc = jd_presets[jd_option]
        elif jd_option=="Custom Upload":
            jd_file = st.file_uploader("📝 Upload Job Description (TXT/PDF/DOCX)", type=["pdf","docx","txt"])
            if jd_file: job_desc = extract_text(jd_file)

    if resume_file and job_desc:
        resume_text = extract_text(resume_file)
        score, matched, missing = calculate_ats_score(resume_text, job_desc)

        # --- Mini Dashboard Cards ---
        st.markdown("<div class='card'><h4>📊 Resume Match Overview</h4>", unsafe_allow_html=True)
        dash1,dash2,dash3,dash4 = st.columns([1,1,1,1.2])
        dash1.markdown(f"<div class='mini-card'><h3 style='color:#00C6FF;'>{score}%</h3><p>ATS Score</p></div>", unsafe_allow_html=True)
        dash2.markdown(f"<div class='mini-card'><h3 style='color:#34D399;'>{len(matched)}</h3><p>Matched</p></div>", unsafe_allow_html=True)
        dash3.markdown(f"<div class='mini-card'><h3 style='color:#F87171;'>{len(missing)}</h3><p>Missing</p></div>", unsafe_allow_html=True)
        
        # --- Bar Chart ---
        fig, ax = plt.subplots(figsize=(2,2.5))
        bars = ax.bar(["ATS Match %"], [score], color="#007BFF")
        ax.set_ylim(0,100)
        for bar in bars:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,f"{score}%",ha='center',va='bottom',fontsize=10,fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Missing Keywords ---
        st.markdown("<div class='card'><h4>🔍 Missing Keywords</h4>", unsafe_allow_html=True)
        if missing: st.write(", ".join(list(missing)[:20]))
        else: st.write("✅ All key skills covered!")
        st.markdown("</div>", unsafe_allow_html=True)
        st.info(f"💡 Suggestion: Add missing keywords to boost your ATS score.")

# ==============================
# CHAT ASSISTANT
# ==============================
elif page=="💬 Chat Assistant":
    st.markdown('<p class="title">💬 Nuvora Chat</p>', unsafe_allow_html=True)
    st.markdown("<div class='card'>Chat with Nuvora for resume tips, interview prep, skill growth, or code queries!</div>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Scrollable chat
    chat_placeholder = st.empty()
    with chat_placeholder.container():
        for sender, msg in st.session_state.chat_history:
            if sender=="You":
                st.markdown(f"<div class='user-msg'>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-msg'>{msg}</div>", unsafe_allow_html=True)

    # Input at bottom
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("💭 Type your message here...")
        submit_btn = st.form_submit_button("Send")

        if submit_btn and user_input:
            st.session_state.chat_history.append(("You", user_input))
            msg = user_input.lower()
            if "resume" in msg:
                reply = "Your resume should highlight technical skills, certifications, and projects."
            elif "skill" in msg:
                reply = "Focus on Python, SQL, Power BI/Tableau for analytics roles."
            elif "interview" in msg:
                reply = "Prepare for HR & technical rounds. Be ready to explain your projects clearly."
            elif any(k in msg for k in ["python","javascript","code","loop","function"]):
                reply = "💻 CODE HELP: Ask me about Python/JS examples, loops, functions, or concepts."
            else:
                reply = "I'm your career buddy! Ask about resume, interview, skills, or code."
            st.session_state.chat_history.append(("Nuvora 💫", reply))
            st.experimental_rerun()

# ==============================
# FOOTER
# ==============================
st.markdown("<hr><p style='text-align:center;color:gray;'>Developed with ❤️ by Pearl and Vasu</p>", unsafe_allow_html=True)
