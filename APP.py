import streamlit as st
import PyPDF2
import re
import time
from sentence_transformers import SentenceTransformer, util
from fuzzywuzzy import fuzz

# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------
st.set_page_config(page_title="💫 Nuvora AI", page_icon="💼", layout="wide")

# ---------------------------------------
# STYLE (ChatGPT look)
# ---------------------------------------
st.markdown("""
<style>
body { background-color: #E6F0FF; }
.stApp {
    background: linear-gradient(160deg, #dff3ff 0%, #f9fbff 100%);
    font-family: 'Poppins', sans-serif;
}
h1, h2, h3 { color: #0056b3; }
.chat-bubble {
    background-color: black;
    border-radius: 18px;
    padding: 1em 1.2em;
    margin-bottom: 0.8em;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}
.chat-bubble-ai {
    background-color: #0078FF;
    color: white;
    border-radius: 18px;
    padding: 1em 1.2em;
    margin-bottom: 0.8em;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}
.stChatInput textarea {
    border-radius: 25px !important;
    padding: 0.8em !important;
    border: 2px solid #0078FF !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# HEADER
# ---------------------------------------
st.markdown("<h1 style='text-align:center;'>💫 Nuvora AI Career Assistant</h1>", unsafe_allow_html=True)
st.caption("Chat with your AI Career Coach & Resume Analyzer")

# ---------------------------------------
# MODEL
# ---------------------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ---------------------------------------
# FUNCTIONS
# ---------------------------------------
def extract_text_from_pdf(file):
    text = ""
    pdf = PyPDF2.PdfReader(file)
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += re.sub(r'\s+', ' ', page_text) + " "
    return text.lower()

def calculate_similarity(jd_text, resume_text):
    jd_embed = model.encode(jd_text, convert_to_tensor=True)
    resume_embed = model.encode(resume_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(jd_embed, resume_embed).item()
    return round(similarity * 100, 2)

def extract_skills(text):
    skill_keywords = [
        "python", "java", "c++", "html", "css", "javascript", "sql", "mongodb",
        "react", "node", "machine learning", "deep learning", "nlp",
        "data analysis", "data visualization", "power bi", "tableau", "excel",
        "pandas", "numpy", "matplotlib", "seaborn", "tensorflow", "keras",
        "flask", "django", "git", "github", "communication", "leadership",
        "problem solving", "teamwork", "critical thinking", "data science"
    ]
    found = []
    for skill in skill_keywords:
        if fuzz.partial_ratio(skill, text) > 80:
            found.append(skill.title())
    return list(set(found))

def chat_ai_response(prompt):
    """Simple rule-based chatbot logic"""
    prompt = prompt.lower()

    if "no skill" in prompt or "skills" in prompt:
        return "If no skills were detected, your resume text might be unclear or scanned incorrectly. Try saving as a text-based PDF and check if skill names are clearly written!"
    elif "job" in prompt:
        return "You have potential! 🚀 Focus on matching your resume to the job description, highlight keywords, and target a match score above 70%."
    elif "resume" in prompt:
        return "Your resume is your first impression. Keep it one page, clear, and keyword-rich for ATS systems!"
    elif "improve" in prompt:
        return "To improve your resume, make sure you use measurable achievements (e.g., 'increased efficiency by 20%') and match job skills closely."
    elif "hello" in prompt or "hi" in prompt:
        return "Hey there 👋! I’m Nuvora, your AI Career Assistant. Upload your resume and job description to begin!"
    else:
        return "I'm here to help you with resumes, jobs, and skills 💼. Try asking something like 'How can I improve my resume?'"

# ---------------------------------------
# STATE
# ---------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------
# CHAT INPUT
# ---------------------------------------
user_prompt = st.chat_input("💬 Ask Nuvora about your career, skills, or resume...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Let me think 🤔..."):
            time.sleep(1)
            ai_reply = chat_ai_response(user_prompt)
            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# ---------------------------------------
# RESUME ANALYZER
# ---------------------------------------
st.markdown("---")
st.markdown("### 📊 Resume Match & Skill Analysis")

job_description = st.text_area("📄 Paste Job Description", height=150)
uploaded_files = st.file_uploader("📂 Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 Analyze Resumes"):
    if not job_description:
        st.warning("⚠️ Please paste a Job Description first.")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one resume.")
    else:
        with st.spinner("Analyzing resumes..."):
            jd_text = job_description.lower()
            results = []
            for file in uploaded_files:
                resume_text = extract_text_from_pdf(file)
                similarity = calculate_similarity(jd_text, resume_text)
                skills = extract_skills(resume_text)
                results.append((file.name, similarity, skills))

        st.success("✅ Analysis Complete!")
        for name, score, skills in results:
            st.markdown(f"""
            <div class="chat-bubble">
                📄 <b>{name}</b><br>
                🧠 Match Score: <b>{score}%</b><br>
                💡 Skills Found: {', '.join(skills) if skills else 'No skills detected'}
            </div>
            """, unsafe_allow_html=True)

st.markdown("<p style='text-align:center; font-size:13px;'>💼 Nuvora AI | Chat-based Career Assistant</p>", unsafe_allow_html=True)
