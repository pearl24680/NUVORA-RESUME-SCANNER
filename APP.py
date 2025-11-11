import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt
import google.generativeai as genai

# ==============================
# 🎨 Page Configuration
# ==============================
st.set_page_config(page_title="Nuvora AI - Resume & Career Assistant", page_icon="💫", layout="wide")

# --- Custom Premium Dark Theme ---
st.markdown("""
    <style>
    body {
        background-color: #0A0F24;
        color: #EAEAEA;
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background-color: #0A0F24;
        color: #EAEAEA;
    }
    .title {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(90deg, #00C6FF, #0072FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .card {
        background: linear-gradient(145deg, #1B1F3B, #101325);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.4);
    }
    .metric {
        font-size: 28px;
        font-weight: 600;
        color: #00C6FF;
    }
    .stTextInput>div>div>input {
        background-color: #1E223D;
        color: white;
    }
    .stButton>button {
        background: linear-gradient(90deg, #0072FF, #00C6FF);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================
# 🔑 Gemini AI Setup
# ==============================
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your Gemini key

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ==============================
# 📂 Helper Functions
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
# 🧭 Sidebar Navigation
# ==============================
st.sidebar.title("💫 Nuvora AI")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate to:", ["🏠 Home", "📊 ATS Resume Scanner", "💬 Career Chat"])

st.sidebar.markdown("---")
st.sidebar.caption("Developed by Team Nuvora 💙")

# ==============================
# 🏠 Home
# ==============================
if page == "🏠 Home":
    st.markdown('<p class="title">💫 Nuvora AI - Resume & Career Assistant</p>', unsafe_allow_html=True)
    st.markdown("""
        <div class='card'>
        <h3>🚀 Welcome to Nuvora!</h3>
        <p>Empower your career with smart AI tools:</p>
        <ul>
        <li>📄 Analyze your Resume for ATS Optimization</li>
        <li>📊 Compare your skills with Job Descriptions</li>
        <li>💬 Chat with AI for career and skill guidance</li>
        </ul>
        <p>Start by uploading your resume and job description!</p>
        </div>
    """, unsafe_allow_html=True)

# ==============================
# 📊 ATS Resume Scanner
# ==============================
elif page == "📊 ATS Resume Scanner":
    st.markdown('<p class="title">📈 ATS Resume Analyzer</p>', unsafe_allow_html=True)
    st.write("Upload your Resume and Job Description to see how well they match.")

    col1, col2 = st.columns(2)
    with col1:
        resume_file = st.file_uploader("📄 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    with col2:
        jd_file = st.file_uploader("🧾 Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

    if resume_file and jd_file:
        resume_text = extract_text(resume_file)
        job_desc = jd_file.read().decode("utf-8") if jd_file.name.endswith(".txt") else extract_text(jd_file)

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

        st.markdown("### 💡 Smart Suggestions for Data Science Profile")
        suggestions = [
            "Include strong project keywords like 'Machine Learning' or 'AI'.",
            "Mention tools such as Pandas, NumPy, Scikit-learn, and TensorFlow.",
            "Add data visualization skills: Matplotlib, Power BI, or Seaborn.",
            "Highlight impact metrics, e.g., 'Improved accuracy by 12%'.",
            "Include teamwork, leadership, and problem-solving examples."
        ]
        for s in suggestions:
            st.markdown(f"- {s}")

# ==============================
# 💬 AI Career Chat
# ==============================
elif page == "💬 Career Chat":
    st.markdown('<p class="title">💬 Ask Nuvora AI</p>', unsafe_allow_html=True)
    st.write("Ask anything about career, resume tips, or interview advice.")
    user_input = st.text_input("💭 You:", placeholder="Ask your question here...")

    if user_input:
        with st.spinner("Thinking... 💫"):
            reply = ask_gemini(user_input)
        st.markdown(f"<div class='card'><b>Nuvora 💫:</b><br>{reply}</div>", unsafe_allow_html=True)

# ==============================
# 🧾 Footer
# ==============================
st.markdown("""
<hr>
<p style='text-align:center; color:gray;'>
Developed with ❤️ by <b>Nuvora AI</b> | Empowering Resumes with Intelligence
</p>
""", unsafe_allow_html=True)
