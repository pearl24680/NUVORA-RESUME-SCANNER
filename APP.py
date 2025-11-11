# app.py
import streamlit as st
import pdfplumber
import docx
import re
from io import BytesIO
import matplotlib.pyplot as plt

# -------------------------
# Page config + CSS (dark)
# -------------------------
st.set_page_config(page_title="Nuvora — AI Resume Dashboard", page_icon="💫", layout="wide")

st.markdown("""
<style>
/* Page */
body { background-color: #0B1220; color: #E6EDF3; }

/* Title */
.title { font-size:32px; font-weight:800; color: #9FE8FF; text-align:center; }

/* Card */
.card {
  background: linear-gradient(180deg, #0F1724 0%, #0B1220 100%);
  border: 1px solid rgba(255,255,255,0.04);
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 6px 18px rgba(2,8,23,0.6);
}

/* Progress area */
.progress-area {
  background: #071522;
  border-radius: 10px;
  padding: 12px;
}

/* Chat */
.chat-box {
  background: #071427;
  border-radius: 12px;
  padding: 12px;
  max-height: 440px;
  overflow-y: auto;
}
.user-bubble {
  background: linear-gradient(90deg,#00C6FF,#0072FF);
  color: #fff;
  padding: 10px 12px;
  border-radius: 14px;
  display: inline-block;
  margin: 6px 0; float: right;
}
.bot-bubble {
  background: #0F1B2D;
  color: #E6EDF3;
  padding: 10px 12px;
  border-radius: 14px;
  display: inline-block;
  margin: 6px 0; float: left;
}
.clear { clear: both; }
.small-muted { color: #9aa9bf; font-size:12px; }
.metric { font-size: 22px; font-weight:700; color:#DFF7FF; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Helper functions
# -------------------------
def extract_text_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
    except Exception:
        # try reading bytes
        try:
            file.seek(0)
            with pdfplumber.open(BytesIO(file.read())) as pdf:
                for p in pdf.pages:
                    text += p.extract_text() or ""
        except Exception:
            return ""
    return text

def extract_text_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception:
        try:
            file.seek(0)
            doc = docx.Document(BytesIO(file.read()))
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            return ""

def extract_text(file):
    if file is None:
        return ""
    name = file.name.lower()
    if name.endswith(".pdf"):
        return extract_text_pdf(file)
    if name.endswith(".docx"):
        return extract_text_docx(file)
    if name.endswith(".txt"):
        try:
            return file.read().decode("utf-8")
        except Exception:
            return ""
    return ""

def tokenize_words(text):
    return re.findall(r'\b[a-zA-Z0-9\+\#\.\-]+\b', text.lower())

# curated skill keywords (expandable)
SKILLS = [
    "python","pandas","numpy","scikit-learn","sklearn","tensorflow","keras","pytorch",
    "sql","power bi","tableau","excel","matplotlib","seaborn","nlp","natural language processing",
    "machine learning","deep learning","data science","statistics","probability","spark","hadoop",
    "docker","flask","django","git","github","aws","azure","gcp","keras","feature engineering"
]

def extract_skills_from_text(text):
    text_l = text.lower()
    found = []
    for s in SKILLS:
        if re.search(rf'\b{re.escape(s)}\b', text_l):
            found.append(s)
    return sorted(list(set(found)))

def compute_ats(jd_text, resume_text):
    jd_tokens = set(tokenize_words(jd_text))
    res_tokens = set(tokenize_words(resume_text))
    if not jd_tokens:
        return 0.0, [], []
    matched = sorted(list(jd_tokens & res_tokens))
    missing = sorted(list(jd_tokens - res_tokens))
    score = round((len(matched) / len(jd_tokens)) * 100, 2)
    return score, matched, missing

def suggestions_for_role(missing_skills, role):
    suggestions = []
    if not missing_skills:
        suggestions.append("Your resume already contains the key JD keywords — good job! 👍")
    else:
        suggestions.append(f"Add these keywords/sections to your resume (from JD): {', '.join(missing_skills[:8])}")
        # role-specific hints
        if role == "Data Scientist":
            suggestions.append("Add a Projects section: include dataset, approach, model used, and metrics (accuracy, F1).")
            suggestions.append("Mention libraries and tools: pandas, numpy, scikit-learn, matplotlib, seaborn.")
        elif role == "AI Engineer":
            suggestions.append("Show model deployment experience: Flask/Docker or cloud deployment (AWS/GCP).")
        elif role == "Web Developer":
            suggestions.append("List frontend & backend tech (React, Node.js) and sample live projects or GitHub links.")
        else:
            suggestions.append("Use action verbs and quantify achievements (improved X by Y%).")
    return suggestions

# -------------------------
# Session state init
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (role,msg)
if "ats_result" not in st.session_state:
    st.session_state.ats_result = None

# -------------------------
# Layout: header
# -------------------------
st.markdown('<div style="text-align:center"><span class="title">💫 Nuvora — AI Resume Dashboard (Dark)</span></div>', unsafe_allow_html=True)
st.write("")  # spacer

# top row: inputs on left, cards on right
left, right = st.columns([1.4, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Upload Inputs")
    resume_file = st.file_uploader("Upload Resume (PDF / DOCX)", type=["pdf", "docx"])
    jd_choice = st.selectbox("Choose Job Description or upload custom", ["-- select --", "Data Scientist", "AI Engineer", "Web Developer", "Software Developer", "Custom Upload"])
    job_text = ""
    if jd_choice == "Custom Upload":
        jd_file = st.file_uploader("Upload JD (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"])
        if jd_file:
            job_text = extract_text(jd_file)
    elif jd_choice == "-- select --":
        st.info("Pick a JD preset or upload one.")
    else:
        presets = {
            "Data Scientist": "Proficiency in Python, Pandas, NumPy, Machine Learning, Data Visualization, Scikit-learn, SQL, Deep Learning, Model Deployment, statistics.",
            "AI Engineer": "Experience in Python, TensorFlow, PyTorch, Deep Learning, Model Optimization, NLP, deployment, Docker, AWS.",
            "Web Developer": "HTML, CSS, JavaScript, React, Node.js, REST APIs, SQL/NoSQL, Responsive Design.",
            "Software Developer": "Java, C++, OOP, Data Structures, Algorithms, Testing, Databases, problem solving."
        }
        job_text = presets.get(jd_choice, "")

    run_btn = st.button("Analyze Resume", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Quick Summary")
    if st.session_state.ats_result:
        res = st.session_state.ats_result
        st.markdown(f'<div class="small-muted">Last analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric">{res["score"]}%</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="small-muted">Matched keywords: {len(res["matched"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="small-muted">Missing keywords: {len(res["missing"])}</div>', unsafe_allow_html=True)
    else:
        st.write("No analysis run yet.")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")  # spacer

# -------------------------
# Run analysis
# -------------------------
if run_btn:
    if not resume_file:
        st.warning("Please upload a resume file.")
    elif not job_text or job_text.strip() == "":
        st.warning("Please choose a JD preset or upload a JD file.")
    else:
        with st.spinner("Analyzing resume & JD..."):
            resume_text = extract_text(resume_file) or ""
            score, matched, missing = compute_ats(job_text, resume_text)
            # also extract skill keywords
            resume_skills = extract_skills_from_text(resume_text)
            suggestions = suggestions_for_role(missing, jd_choice if jd_choice != "Custom Upload" else "Custom")
            st.session_state.ats_result = {
                "score": score,
                "matched": matched,
                "missing": missing,
                "resume_skills": resume_skills,
                "suggestions": suggestions,
                "role": jd_choice
            }

# -------------------------
# Main reporting area
# -------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

if st.session_state.ats_result:
    res = st.session_state.ats_result
    # top: compact progress bar area
    st.markdown("### Matching Score")
    col1, col2 = st.columns([4,1])
    with col1:
        # small horizontal progress bar
        prog = int(res["score"])
        st.progress(prog)
        st.markdown(f"<div class='small-muted' style='margin-top:6px;'>ATS Score: <b>{res['score']}%</b></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align:right'><span class='metric'>{res['score']}%</span></div>", unsafe_allow_html=True)

    st.write("")  # spacer

    # skill cards row
    a, b, c = st.columns(3)
    with a:
        st.markdown("**✅ Top Matching Skills**")
        if res["matched"]:
            for m in res["matched"][:12]:
                st.markdown(f"- {m}")
        else:
            st.info("No matching keywords found")

    with b:
        st.markdown("**⚠️ Missing Skills (from JD)**")
        if res["missing"]:
            for m in res["missing"][:12]:
                st.markdown(f"- {m}")
        else:
            st.success("No missing skills — great match!")

    with c:
        st.markdown("**💡 Suggestions**")
        for s in res["suggestions"]:
            st.markdown(f"- {s}")

    st.markdown("---")
    # optional small bar chart of resume skills count
    st.markdown("### Resume Skills Detected (sample)")
    if res["resume_skills"]:
        counts = [1]*len(res["resume_skills"])
        fig, ax = plt.subplots(figsize=(6,1.2))
        ax.barh(res["resume_skills"], counts, color="#00C6FF")
        ax.set_xlim(0, max(1, max(counts)))
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.info("No known skill keywords detected in resume.")

else:
    st.info("Upload files and click **Analyze Resume** to see ATS results here.")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Chat box (ChatGPT-like local)
# -------------------------
st.write("")  # spacer
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("💬 Ask Nuvora (offline assistant)")

chat_col1, chat_col2 = st.columns([3,1])
with chat_col1:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for role,msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f'<div class="user-bubble">{msg}</div><div class="clear"></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-bubble">{msg}</div><div class="clear"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with chat_col2:
    user_msg = st.text_input("Type message...", key="chat_input")
    if st.button("Send", key="send_btn"):
        if user_msg and user_msg.strip():
            st.session_state.chat_history.append(("user", user_msg))
            # simple local responses — keep improving later
            prompt = user_msg.lower()
            if "how" in prompt and "improve" in prompt and "resume" in prompt:
                reply = "Start with a summary, add 2-3 projects (goal, approach, metrics), list tools and quantify results."
            elif "data science" in prompt:
                reply = "Focus on Python, ML algorithms, statistical analysis, feature engineering, and model evaluation metrics."
            elif "interview" in prompt:
                reply = "Practice explaining projects end-to-end. Prepare STAR answers and coding fundamentals."
            elif "skills" in prompt:
                reply = "Check the JD and add missing keywords. Add tools and libraries in a separate 'Skills' section."
            else:
                reply = local_reply = ("I can help with resume improvements, job-fit, and skill suggestions. "
                                       "Ask me things like 'How to improve my resume for Data Scientist?'")
            st.session_state.chat_history.append(("bot", reply))
            # clear input
            st.session_state.chat_input = ""
            st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Footer
# -------------------------
st.markdown("""
<div style="text-align:center; color:#94a3b8; margin-top:18px;">
Nuvora — Offline Resume Intelligence • Built with Streamlit & Python
</div>
""", unsafe_allow_html=True)
