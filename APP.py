import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt
import google.generativeai as genai

# ==============================
# 🎨 PAGE SETUP
# ==============================
st.set_page_config(page_title="Nuvora AI - Resume Scanner & Job Assistant", page_icon="💫", layout="wide")

# --- Dark Theme CSS ---
st.markdown("""
    <style>
    body { background-color: #0e1117; color: white; }
    .stApp { background-color: #0e1117; color: white; }
    .title { font-size: 36px; font-weight: bold; color: #00BFFF; text-align:center; }
    .metric { color: #FFD700; font-size: 22px; }
    .stProgress > div > div > div > div { background-color: #00BFFF; }
    </style>
""", unsafe_allow_html=True)

# ==============================
# 🔑 Gemini API Setup
# ==============================
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your key

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ==============================
# 📄 Helper Functions
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
# 🧠 Sidebar Navigation
# ==============================
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Dashboard", "📊 ATS Analysis", "💬 AI Career Chat"])

# ==============================
# 📤 Upload Section
# ==============================
st.sidebar.subheader("📂 Upload Files")
resume_file = st.sidebar.file_uploader("📄 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
jd_file = st.sidebar.file_uploader("🧾 Upload Job Description", type=["pdf", "docx", "txt"])

# ==============================
# 🏠 Dashboard
# ==============================
if page == "🏠 Dashboard":
    st.markdown('<p class="title">💫 Nuvora AI - Resume & Job Assistant</p>', unsafe_allow_html=True)
    st.write("Welcome to your personal AI-powered job assistant! Upload your resume and job description to analyze your ATS score and get smart insights.")
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712104.png", width=150)
    st.info("Tip: After uploading your files, go to **ATS Analysis** to view your detailed results.")

# ==============================
# 📊 ATS ANALYSIS
# ==============================
elif page == "📊 ATS Analysis":
    st.markdown('<p class="title">📈 Resume ATS Analysis</p>', unsafe_allow_html=True)
    if resume_file and jd_file:
        resume_text = extract_text(resume_file)

        if jd_file.name.endswith(".txt"):
            job_desc = jd_file.read().decode("utf-8")
        else:
            job_desc = extract_text(jd_file)

        score, matched, missing = calculate_ats_score(resume_text, job_desc)

        col1, col2, col3 = st.columns(3)
        col1.metric("🎯 ATS Score", f"{score}%")
        col2.metric("✅ Matched Keywords", len(matched))
        col3.metric("⚠️ Missing Keywords", len(missing))

        # Graph
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.bar(["Match %"], [score], color="#00BFFF")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Selection Probability")
        ax.set_facecolor("#111")
        fig.patch.set_facecolor("#0e1117")
        st.pyplot(fig)

        st.markdown("### ✅ Matched Skills")
        st.write(", ".join(list(matched)) if matched else "No matches found")

        st.markdown("### ⚠️ Missing Skills (Improve These)")
        st.write(", ".join(list(missing)) if missing else "Perfect Match!")

        st.markdown("### 💡 Suggestions for Data Science Profile")
        suggestions = [
            "Add more ML or AI-related project keywords.",
            "Include libraries like Python, Pandas, NumPy, Scikit-learn.",
            "Highlight visualization tools: Power BI, Matplotlib, Seaborn.",
            "Add measurable outcomes like accuracy improvements.",
            "Include teamwork and communication soft skills."
        ]
        for s in suggestions:
            st.markdown(f"- {s}")
    else:
        st.warning("⚠️ Please upload your resume and job description files from the sidebar first!")

# ==============================
# 💬 AI Career Chat
# ==============================
elif page == "💬 AI Career Chat":
    st.markdown('<p class="title">💬 Nuvora AI Career Chat</p>', unsafe_allow_html=True)
    st.write("Chat with Nuvora AI about career advice, resume tips, or skill recommendations.")
    user_input = st.text_input("💭 You:", placeholder="Ask me anything about your career...")
    if user_input:
        with st.spinner("Thinking... 💫"):
            reply = ask_gemini(user_input)
        st.markdown(f"**Nuvora 💫:** {reply}")

# ==============================
# 🧾 Footer
# ==============================
st.markdown("""
<hr>
<p style='text-align:center; color:gray;'>
Developed by <b>Nuvora AI</b> 💫 | Resume Intelligence & Career Assistant
</p>
""", unsafe_allow_html=True)

