import streamlit as st
import os
from PyPDF2 import PdfReader
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from openai import OpenAI

# -------------------------------
# APP CONFIG
# -------------------------------
st.set_page_config(page_title="Nuvora AI – ATS Resume Analyzer", layout="wide", page_icon="💫")

st.markdown("""
    <style>
    body {background: linear-gradient(180deg, #E6F2FF, #FFFFFF);}
    .stApp {background-color: transparent;}
    .title {font-size: 36px; font-weight: 800; color: #002B5B; text-align:center;}
    .subtitle {font-size: 16px; color: #005FCC; text-align:center; margin-bottom: 20px;}
    .card {background: #ffffff; border-radius: 12px; padding: 18px; 
           box-shadow: 0 6px 20px rgba(0, 40, 100, 0.08);}
    .chat-user {background:#0078FF; color:black; padding:10px 14px; border-radius:18px; float:right; margin:6px;}
    .chat-bot {background:#F1F3F4; color:#002B5B; padding:10px 14px; border-radius:18px; float:left; margin:6px;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>💫 Nuvora AI — ATS Resume Analyzer & Career Chatbot</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Upload resumes, analyze ATS score, and chat with your AI career mentor.</div>", unsafe_allow_html=True)

# -------------------------------
# SECURE API SETUP
# -------------------------------
api_key = os.getenv("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")
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None

# -------------------------------
# FUNCTIONS
# -------------------------------
def extract_text_from_pdf(file):
    text = ""
    try:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception:
        pass
    return text.lower()

def extract_skills(text):
    skills = [
        "python", "java", "sql", "html", "css", "javascript", "react", "node", "pandas", "numpy",
        "power bi", "tableau", "excel", "machine learning", "deep learning", "nlp", "flask", "django",
        "data analysis", "data visualization", "communication", "leadership", "teamwork"
    ]
    found = []
    for skill in skills:
        if re.search(rf"\\b{skill}\\b", text, re.IGNORECASE):
            found.append(skill.title())
        elif fuzz.partial_ratio(skill.lower(), text) > 85:
            found.append(skill.title())
    return sorted(list(set(found)))

def calculate_similarity(jd_text, resume_text):
    documents = [jd_text, resume_text]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(sim * 100, 2)

def ats_score(jd, resume):
    jd = jd.lower()
    resume = resume.lower()
    skills_jd = extract_skills(jd)
    skills_resume = extract_skills(resume)
    matched = [s for s in skills_resume if s.lower() in [x.lower() for x in skills_jd]]
    skill_match = (len(matched) / len(skills_jd) * 100) if skills_jd else 0
    sim = calculate_similarity(jd, resume)
    overall = round(0.6 * sim + 0.4 * skill_match, 2)
    return overall, skill_match, matched, skills_resume

# -------------------------------
# INPUTS
# -------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])

with col1:
    job_description = st.text_area("📄 Paste Job Description", height=200,
                                   placeholder="Example: Looking for Data Analyst with Python, SQL, Power BI...")
with col2:
    uploaded_files = st.file_uploader("📂 Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# ANALYSIS
# -------------------------------
if st.button("🚀 Analyze Resumes"):
    if not job_description:
        st.warning("Please enter a job description first.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        st.info("Analyzing resumes... please wait.")
        results = []

        for file in uploaded_files:
            text = extract_text_from_pdf(file)
            if not text.strip():
                st.error(f"❌ Could not read {file.name}. Try a text-based PDF.")
                continue
            overall, skill_match, matched, all_skills = ats_score(job_description, text)
            results.append({
                "Resume": file.name,
                "ATS %": overall,
                "Skill Match %": round(skill_match, 2),
                "Matched Skills": ", ".join(matched) if matched else "None",
                "Skills Found": ", ".join(all_skills)
            })

        if results:
            df = pd.DataFrame(results).sort_values(by="ATS %", ascending=False)
            st.success("✅ Analysis complete!")
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("Resume")["ATS %"])
            st.session_state["results"] = df

# -------------------------------
# CHATBOT SECTION
# -------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("💬 Ask Nuvora — AI Career Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='clear:both'></div>", unsafe_allow_html=True)

user_input = st.chat_input("Ask something about your resume, ATS score, or job prep...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    answer = ""

    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Nuvora, an AI career assistant giving professional resume and job advice."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=400,
                temperature=0.5
            )
            answer = response.choices[0].message.content.strip()
        except Exception:
            answer = "⚠️ AI response temporarily unavailable. Please try again later."
    else:
        # Offline fallback
        answer = "I can give you career tips! Try asking about resume improvement or interview preparation."

    st.session_state.chat_history.append({"role": "bot", "content": answer})
    st.experimental_rerun()

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#005FCC;'>💼 Developed by Pearl | Nuvora Final Year Project</p>", unsafe_allow_html=True)

