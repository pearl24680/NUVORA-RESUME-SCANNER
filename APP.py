import streamlit as st
import PyPDF2
import re
import time
from sentence_transformers import SentenceTransformer, util

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Nuvora AI - Resume Chat Assistant",
    page_icon="💫",
    layout="wide"
)

# -----------------------------------
# CUSTOM CSS - CHATGPT STYLE THEME
# -----------------------------------
st.markdown("""
<style>
body {
    background-color: #E6F0FF;
}
.stApp {
    background: linear-gradient(to bottom right, #e0f7ff, #f9ffff);
    color: #001B48;
    font-family: "Poppins", sans-serif;
}
.chat-bubble-user {
    background-color: #0078FF;
    color: white;
    padding: 0.8em 1em;
    border-radius: 20px;
    margin: 8px;
    text-align: right;
    width: fit-content;
    max-width: 75%;
    margin-left: auto;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.chat-bubble-ai {
    background-color: #ffffff;
    color: #001B48;
    padding: 0.8em 1em;
    border-radius: 20px;
    margin: 8px;
    text-align: left;
    width: fit-content;
    max-width: 75%;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.stButton button {
    background: linear-gradient(to right, #0078FF, #00C6FF);
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    border: none;
}
.stButton button:hover {
    background: linear-gradient(to right, #0062CC, #0096FF);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# LOAD MODEL
# -----------------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')
model = load_model()

# -----------------------------------
# FUNCTIONS
# -----------------------------------
def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        t = page.extract_text()
        if t:
            text += t + " "
    return text.lower()

def calculate_similarity(jd_text, resume_text):
    jd_embed = model.encode(jd_text, convert_to_tensor=True)
    resume_embed = model.encode(resume_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(jd_embed, resume_embed).item()
    return round(similarity * 100, 2)

def extract_skills(text):
    skill_set = [
        "python","java","c++","html","css","javascript","sql","mongodb","react","node",
        "machine learning","deep learning","nlp","data analysis","data visualization",
        "power bi","tableau","excel","pandas","numpy","matplotlib","seaborn","tensorflow",
        "keras","communication","leadership","problem solving","teamwork","critical thinking",
        "data science","flask","django","git","github"
    ]
    found = [s.title() for s in skill_set if re.search(rf"\\b{s}\\b", text, re.IGNORECASE)]
    return list(set(found))

# -----------------------------------
# HEADER
# -----------------------------------
st.title("💫 Nuvora AI Chat — Resume Screening Assistant")
st.caption("Developed by Pearl & Vasu | Final Year Project ")

# -----------------------------------
# INPUT AREA
# -----------------------------------
st.markdown("### 🧠 Chat with Nuvora AI")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_prompt = st.chat_input("Ask Nuvora or upload resumes for analysis...")

# -----------------------------------
# CHAT SYSTEM
# -----------------------------------
if user_prompt:
    st.session_state.chat_history.append(("user", user_prompt))
    st.session_state.chat_history.append(("ai", "Let me think 🤔..."))

    with st.spinner("Analyzing..."):
        time.sleep(1.5)
        if "upload" in user_prompt.lower() or "resume" in user_prompt.lower():
            st.session_state.chat_history.append(("ai", "Please upload the resumes below so I can analyze them."))

# -----------------------------------
# FILE UPLOAD + JOB DESCRIPTION
# -----------------------------------
st.markdown("### 📄 Upload Job Description & Resumes")

job_description = st.text_area("Paste Job Description", height=180, placeholder="Example: Looking for Data Analyst skilled in Python, SQL, Power BI, Excel...")
uploaded_files = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

# -----------------------------------
# ANALYZE BUTTON
# -----------------------------------
if st.button("🚀 Analyze Resumes"):
    if not job_description:
        st.warning("⚠️ Please provide a Job Description first.")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one resume.")
    else:
        st.session_state.chat_history.append(("ai", "Analyzing resumes... please wait ⏳"))
        jd_text = job_description.lower()
        results = []
        for file in uploaded_files:
            resume_text = extract_text_from_pdf(file)
            if not resume_text.strip():
                st.session_state.chat_history.append(("ai", f"❌ {file.name}: No readable text found."))
                continue
            match = calculate_similarity(jd_text, resume_text)
            skills = extract_skills(resume_text)
            result_msg = (
                f"📄 **{file.name}**\n\n"
                f"🧠 Match Score: **{match}%**\n"
                f"💡 Skills Found: {', '.join(skills) if skills else 'No skills detected'}"
            )
            st.session_state.chat_history.append(("ai", result_msg))
            results.append({"name": file.name, "match": match, "skills": skills})

        if results:
            best = max(results, key=lambda x: x["match"])
            summary = f"🥇 **Top Candidate:** {best['name']} with a {best['match']}% match!"
            st.session_state.chat_history.append(("ai", summary))
            st.balloons()

# -----------------------------------
# DISPLAY CHAT HISTORY
# -----------------------------------
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div class='chat-bubble-user'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-ai'>{msg}</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align:center;'>💼 Nuvora AI | Chat-based Resume Screening Assistant</p>", unsafe_allow_html=True)
