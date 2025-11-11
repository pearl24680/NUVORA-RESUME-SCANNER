import os
import base64
import re
from pathlib import Path
import fitz  # PyMuPDF
import streamlit as st
import plotly.express as px

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="Nuvora AI Job Assistant (Offline)", layout="wide")

# -------------------- STYLING --------------------
st.markdown("""
<style>
body { background-color: #ffffff; color: #222; }
div[data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
.card { background-color: #f7f9fc; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; }
.skill-badge { background-color: #4A90E2; color: white; padding: 4px 8px; border-radius: 5px; margin:2px; display:inline-block; }
.missing-badge { background-color: #F39C12; color: white; padding: 4px 8px; border-radius: 5px; margin:2px; display:inline-block; }
.suggestion-badge { background-color: #2ECC71; color: white; padding: 4px 8px; border-radius: 5px; margin:2px; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# -------------------- FUNCTIONS --------------------
def show_pdf(file_path):
    """Display PDF inline in Streamlit"""
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page in pdf_document:
        text += page.get_text()
    pdf_document.close()
    return text

def extract_projects(text):
    pattern = r"(?i)(projects?|internships?|experience)\s*[:\-]?\s*(.+)"
    matches = re.findall(pattern, text)
    projects = [m[1].strip() for m in matches]
    return list(set(projects))

def match_skills(resume_text, job_description):
    resume_text = resume_text.lower()
    jd_words = set(re.findall(r'\b\w+\b', job_description.lower()))
    matched = [word for word in jd_words if word in resume_text]
    missing = [word for word in jd_words if word not in resume_text]
    overall_score = int((len(matched)/len(jd_words))*100) if jd_words else 0
    return overall_score, matched, missing

def show_dashboard(overall_score, matched, missing):
    col1, col2, col3 = st.columns([1,2,2])
    with col1:
        st.markdown('<div class="card" style="text-align:center;"><h3>Overall Score</h3></div>', unsafe_allow_html=True)
        fig = px.bar(
            x=[overall_score], y=["Resume Match"],
            orientation="h", text=[f"{overall_score}%"],
            color_discrete_sequence=["#2ECC71" if overall_score>=80 else "#F39C12" if overall_score>=60 else "#E74C3C"]
        )
        fig.update_traces(textposition="inside")
        fig.update_layout(xaxis=dict(range=[0,100]), height=150, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<div class="card"><h4>✅ Matched Skills</h4></div>', unsafe_allow_html=True)
        for skill in matched:
            st.markdown(f'<span class="skill-badge">{skill}</span>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><h4>⚠️ Missing Skills</h4></div>', unsafe_allow_html=True)
        for skill in missing:
            st.markdown(f'<span class="missing-badge">{skill}</span>', unsafe_allow_html=True)

# -------------------- OFFLINE CHATBOT --------------------
def offline_chatbot(user_input, resume_text="", job_description=""):
    user_input = user_input.lower()
    if "projects" in user_input:
        projects = extract_projects(resume_text)
        return "Projects found: " + ", ".join(projects) if projects else "No projects detected."
    elif "skills" in user_input:
        overall_score, matched, missing = match_skills(resume_text, job_description)
        return f"Your skill match score is {overall_score}%.\nMatched: {', '.join(matched)}\nMissing: {', '.join(missing)}"
    elif "hello" in user_input or "hi" in user_input:
        return "Hello! I'm your offline career assistant. Ask me about your skills, projects, or resume!"
    else:
        return "I can help you check projects or skills based on your uploaded resume and job description."

# -------------------- SIDEBAR --------------------
st.sidebar.title("📘 Nuvora AI Job Assistant (Offline)")
page = st.sidebar.radio("Navigate", ["🏠 Home", "💼 Project Extractor", "🤖 Career Chatbot"])

# -------------------- HOME --------------------
if page=="🏠 Home":
    st.title("🏠 Home")
    st.info("Offline Nuvora AI Job Assistant: Upload resume and check skills/projects offline.")

    st.subheader("📋 Job Description")
    job_description = st.text_area("Paste job description here", height=150)

    st.subheader("📄 Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Upload your Resume", type=["pdf"])
    resume_text = ""
    if uploaded_file:
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        show_pdf(file_path)
        resume_text = extract_text_from_pdf(file_path)

        if st.button("🔍 Analyze Resume"):
            overall_score, matched, missing = match_skills(resume_text, job_description)
            show_dashboard(overall_score, matched, missing)

# -------------------- PROJECT EXTRACTOR --------------------
elif page=="💼 Project Extractor":
    st.title("💼 Project Extractor (Offline)")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        show_pdf(file_path)
        resume_text = extract_text_from_pdf(file_path)

        if st.button("📂 Extract Projects/Experience"):
            projects = extract_projects(resume_text)
            if projects:
                st.success(f"✅ Found {len(projects)} entries:")
                for p in projects:
                    st.markdown(f"🔹 **{p}**")
            else:
                st.warning("No projects or experience sections detected.")

# -------------------- CAREER CHATBOT --------------------
elif page=="🤖 Career Chatbot":
    st.title("🤖 Offline Career Chatbot")
    if "chat_history" not in st.session_state: st.session_state.chat_history=[]
    user_input = st.text_input("You:", key="user_input")
    if user_input:
        reply = offline_chatbot(user_input, resume_text, job_description)
        st.session_state.chat_history.append({"user": user_input, "bot": reply})
    for chat in st.session_state.chat_history[::-1]:
        st.markdown(f"👩‍💼 You: {chat['user']}")
        st.markdown(f"🤖 {chat['bot']}")
