import streamlit as st
from PyPDF2 import PdfReader
import re, time
import openai

# ==================== CONFIG ====================
st.set_page_config(page_title="Nuvora AI Career Assistant", layout="wide")

# Add your API key here or in Streamlit Secrets
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-api-key-here")

# ==================== CUSTOM STYLING ====================
st.markdown("""
    <style>
    body {
        background: linear-gradient(to bottom right, #E3F2FD, #FFFFFF);
        font-family: 'Poppins', sans-serif;
    }
    .title {
        font-size: 42px;
        font-weight: 800;
        color: #0D47A1;
        text-align: center;
    }
    .subtitle {
        font-size: 18px;
        text-align: center;
        color: #1565C0;
        margin-bottom: 40px;
    }
    .section-header {
        font-size: 22px;
        color: #0D47A1;
        font-weight: 700;
        margin-top: 25px;
    }
    .card {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
        margin-bottom: 25px;
    }
    .chat-box {
        height: 350px;
        overflow-y: auto;
        background: #FAFAFA;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid #BBDEFB;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown('<h1 class="title">💼 Nuvora AI Career Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your Smart ATS Resume Analyzer + AI Career Coach</p>', unsafe_allow_html=True)

# ==================== RESUME ANALYSIS SECTION ====================
st.markdown('<h3 class="section-header">📊 Resume & ATS Match Analysis</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    job_desc = st.text_area("📄 Paste Job Description", placeholder="Paste the job description here...", height=180)
with col2:
    resume_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])

# ========== FUNCTIONS ==========
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_skills(text):
    skills = ['python','java','c++','sql','excel','machine learning','deep learning','nlp',
              'power bi','tableau','communication','leadership','teamwork','data analysis',
              'project management','data visualization','ai','ml','analytics','cloud']
    found = [s for s in skills if re.search(rf'\\b{s}\\b', text.lower())]
    return list(set(found))

def ats_score(resume_text, job_desc):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_desc)
    matched = [s for s in resume_skills if s in job_skills]
    missing = [s for s in job_skills if s not in resume_skills]
    score = (len(matched) / len(job_skills)) * 100 if job_skills else 0
    return score, matched, missing

# ========== ANALYSIS ==========
if resume_file and job_desc:
    with st.spinner("🔍 Analyzing your resume..."):
        resume_text = extract_text_from_pdf(resume_file)
        score, matched, missing = ats_score(resume_text, job_desc)
        time.sleep(1)
        st.success(f"✅ ATS Match Score: {round(score, 2)}%")
        st.progress(score/100)
        st.markdown(f"**✔️ Skills Matched:** {', '.join(matched) if matched else 'None'}")
        st.markdown(f"**⚠️ Missing Skills:** {', '.join(missing) if missing else 'None'}")

        # Extra checks for ATS format
        word_count = len(resume_text.split())
        sections = ['education', 'experience', 'skills', 'projects', 'summary']
        section_count = sum(1 for sec in sections if sec in resume_text.lower())
        ats_compatibility = min(100, (score * 0.6) + (section_count * 10) + (min(word_count, 800)/8))

        st.markdown("### 🧾 ATS Compatibility Report")
        st.info(f"""
        **Formatting Quality:** {section_count}/5 key sections found  
        **Word Count:** {word_count} words  
        **Overall ATS Compatibility:** {round(ats_compatibility, 2)}%
        """)

# ==================== AI CHAT SECTION ====================
st.markdown('<h3 class="section-header">💬 Chat with Nuvora</h3>', unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = []

# Display chat history
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.chat:
        sender = "🧑‍💼 You" if msg["sender"] == "user" else "🤖 Nuvora"
        color = "#0D47A1" if msg["sender"] == "bot" else "#1A237E"
        st.markdown(f"<p style='color:{color}'><b>{sender}:</b> {msg['text']}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

user_message = st.chat_input("Ask Nuvora about your resume, career or interview prep...")

if user_message:
    st.session_state.chat.append({"sender": "user", "text": user_message})
    with st.spinner("Nuvora is thinking..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are Nuvora, an expert AI career coach and resume evaluator."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response["choices"][0]["message"]["content"]
        except Exception as e:
            reply = "⚠️ (Simulated Response) Please configure OpenAI API key to enable real AI chat."
    st.session_state.chat.append({"sender": "bot", "text": reply})
    st.rerun()

st.markdown("<br><hr><p style='text-align:center;color:#0D47A1;'>🚀 Powered by Nuvora AI | Smart ATS + Career Insights</p>", unsafe_allow_html=True)

