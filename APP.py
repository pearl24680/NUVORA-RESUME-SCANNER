import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt

# ==============================
# 🎨 Page Configuration
# ==============================
st.set_page_config(page_title="Nuvora AI Resume Scanner", page_icon="💫", layout="wide")

# --- Custom CSS ---
st.markdown("""
    <style>
    body { background-color: #0e1117; color: white; }
    .stApp { background-color: #0e1117; color: white; }
    .big-font { font-size: 36px !important; font-weight: 700; color: #00BFFF; text-align: center; }
    .stProgress > div > div > div > div { background-color: #00BFFF; }
    .stTextInput > div > div > input { color: white; }
    </style>
""", unsafe_allow_html=True)

# ==============================
# 🔍 Helper Functions
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
    matched_keywords = resume_words.intersection(jd_words)
    score = (len(matched_keywords) / len(jd_words)) * 100 if len(jd_words) > 0 else 0
    missing_keywords = jd_words - resume_words
    return round(score, 2), matched_keywords, missing_keywords

def local_ai_chat(user_input):
    """Simple offline chatbot logic."""
    user_input = user_input.lower()
    if "hello" in user_input or "hi" in user_input:
        return "💫 Hi there! I'm Nuvora — your AI study and career assistant."
    elif "resume" in user_input:
        return "📄 I can help you analyze resumes and job descriptions for ATS compatibility."
    elif "data science" in user_input:
        return "🧠 Data Science involves Python, Pandas, NumPy, Machine Learning, and visualization tools like Power BI or Tableau."
    elif "python" in user_input:
        return "🐍 Python is great for automation, data analysis, and AI. Would you like to see example code?"
    elif "help" in user_input:
        return "💡 You can upload your resume and job description to get ATS score, missing keywords, and smart suggestions."
    else:
        return "🤖 I'm Nuvora! I can answer study, coding, and career-related questions. Try asking me about Python, resumes, or data science."

# ==============================
# 🧠 Page Layout
# ==============================
st.markdown('<p class="big-font">💫 Nuvora AI Resume Scanner</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📤 Upload Files", "📈 ATS Analysis", "💬 Ask Nuvora AI"])

# ------------------------------
# 📤 TAB 1: Upload Files
# ------------------------------
with tab1:
    st.subheader("Upload your Resume and Job Description")
    resume_file = st.file_uploader("📄 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    jd_file = st.file_uploader("🧾 Upload Job Description (Text/PDF/DOCX)", type=["pdf", "docx", "txt"])

    if resume_file and jd_file:
        if jd_file.name.endswith(".txt"):
            job_desc = jd_file.read().decode("utf-8")
        else:
            job_desc = extract_text(jd_file)

        resume_text = extract_text(resume_file)

        score, matched, missing = calculate_ats_score(resume_text, job_desc)

        st.session_state["ats_result"] = {
            "score": score,
            "matched": matched,
            "missing": missing
        }

        st.success("✅ Files uploaded successfully! Now open 'ATS Analysis' tab.")

# ------------------------------
# 📈 TAB 2: ATS Analysis
# ------------------------------
with tab2:
    st.subheader("AI Resume Analysis Report")

    if "ats_result" not in st.session_state:
        st.warning("⚠️ Please upload your resume and job description first!")
    else:
        ats_data = st.session_state["ats_result"]
        score = ats_data["score"]
        matched = ats_data["matched"]
        missing = ats_data["missing"]

        col1, col2, col3 = st.columns(3)
        col1.metric("📊 ATS Score", f"{score}%")
        col2.metric("✅ Matched Keywords", len(matched))
        col3.metric("⚠️ Missing Keywords", len(missing))

        # --- Graph for Selection Probability ---
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.bar(["Match %"], [score], color="#00BFFF")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Selection Probability")
        ax.set_facecolor("#111")
        fig.patch.set_facecolor('#0e1117')
        st.pyplot(fig)

        # --- Keywords Info ---
        st.markdown("### ✅ Matched Skills")
        st.write(", ".join(list(matched)) if matched else "No matches found")

        st.markdown("### ⚠️ Missing Skills (Improve These)")
        st.write(", ".join(list(missing)) if missing else "Perfect Match!")

        # --- Smart Suggestions ---
        st.markdown("### 💡 Smart Suggestions for This Role")
        suggestions = [
            "Add ML or AI project experience.",
            "Include Python, Pandas, NumPy, Scikit-learn.",
            "Mention Power BI, Tableau, or Excel visualization.",
            "Quantify achievements (e.g., 'Improved accuracy by 15%').",
            "Add teamwork and communication skills."
        ]
        for s in suggestions:
            st.markdown(f"- {s}")

# ------------------------------
# 💬 TAB 3: Ask Nuvora AI
# ------------------------------
with tab3:
    st.subheader("💬 Chat with Nuvora AI Assistant")
    user_input = st.text_input("Type your question here...")

    if st.button("Ask"):
        if user_input.strip():
            response = local_ai_chat(user_input)
            st.markdown(f"**Nuvora 💫:** {response}")
        else:
            st.warning("Please type something before clicking Ask!")

# ==============================
# 🌐 Footer
# ==============================
st.markdown("""
<hr>
<p style='text-align:center; color:gray;'>
Developed by <b>pearl</b> 💫 |  Resume Intelligence
</p>
""", unsafe_allow_html=True)

