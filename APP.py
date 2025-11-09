# -------------------------------
# IMPORTS
# -------------------------------
import streamlit as st
import PyPDF2
import re
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os

# -------------------------------
# INITIAL SETUP
# -------------------------------
st.set_page_config(page_title="Nuvora AI — Resume Scanner", page_icon="💫", layout="wide")

# Load OpenAI client (from secrets in Streamlit)
client = None
if "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" in os.environ:
    try:
        client = OpenAI(api_key=os.getenv("sk-proj-vbeoadVOCR05oDvkvj7oRUkQT0aYa-xM0bexJjeX7TP1yf2f4Q-8HEYv9Ubk83f9hy1O8mhLrnT3BlbkFJn4SjBKHWWvK4rF1v-1PcPe2Aneri0axlSfWLVCq8Kvm5tWPxkvD94kxZ12EmaglqS8c0kKfU0"))
    except Exception:
        client = None

# -------------------------------
# CUSTOM CSS — Sky Blue Theme
# -------------------------------
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #D9ECFF 0%, #E6F3FF 100%);
            color: #003366;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #002B5B !important;
            font-weight: 600;
        }
        p, label, span, div {
            color: #003366;
        }
        .stButton button {
            background-color: #0078FF;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6em 1.2em;
            font-weight: 600;
            box-shadow: 0px 4px 8px rgba(0, 120, 255, 0.2);
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            background-color: #005FCC;
            box-shadow: 0px 6px 12px rgba(0, 95, 204, 0.3);
        }
        div[data-testid="stFileUploaderDropzone"] {
            background-color: #ffffff;
            border: 2px dashed #0078FF;
            border-radius: 10px;
        }
        textarea {
            background-color: #ffffff !important;
            color: #000 !important;
            border-radius: 10px !important;
            border: 1px solid #99C2FF !important;
        }
        .dataframe {
            border: 1px solid #A8CFFF !important;
            border-radius: 10px !important;
            background-color: white !important;
        }
        .chat-user {
            background-color: #0078FF;
            color: white;
            padding: 10px 15px;
            border-radius: 15px 15px 0px 15px;
            margin-bottom: 8px;
            float: right;
            max-width: 80%;
            box-shadow: 0 4px 10px rgba(0, 120, 255, 0.3);
        }
        .chat-bot {
            background-color: #ffffff;
            color: #002B5B;
            padding: 10px 15px;
            border-radius: 15px 15px 15px 0px;
            margin-bottom: 8px;
            float: left;
            max-width: 80%;
            border: 1px solid #99C2FF;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 120, 255, 0.1);
            margin-bottom: 20px;
        }
        [data-testid="column"]:nth-child(2) {
            background-color: rgba(255, 255, 255, 0.85);
            border-left: 2px solid #99C2FF;
            border-radius: 16px;
            padding: 15px;
        }
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background-color: #99C2FF;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.title("💫 Nuvora — AI Resume & ATS Analyzer")
st.caption("Developed by Pearl & Vasu | Final Year Project | Smart Resume + Career Assistant")

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def extract_text_from_pdf(file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception:
        text = ""
    return text.lower()

def calculate_similarity(jd_text, resume_text):
    try:
        docs = [jd_text, resume_text]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform(docs)
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(similarity * 100, 2)
    except Exception:
        return 0.0

def extract_skills(text):
    skill_set = [
        "python", "java", "c++", "html", "css", "javascript", "sql", "mongodb", "react", "node",
        "machine learning", "deep learning", "nlp", "data analysis", "data visualization",
        "power bi", "tableau", "excel", "pandas", "numpy", "matplotlib", "seaborn", "tensorflow",
        "keras", "communication", "leadership", "problem solving", "teamwork", "critical thinking",
        "data science", "flask", "django", "git", "github"
    ]
    found_skills = [skill.title() for skill in skill_set if re.search(rf"\\b{skill}\\b", text, re.IGNORECASE)]
    return list(set(found_skills))

# -------------------------------
# MAIN DASHBOARD
# -------------------------------
col1, col2 = st.columns([2, 1], gap="large")

# --- LEFT: ATS ANALYZER ---
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("📊 Resume ATS Analysis")

    job_description = st.text_area("📄 Paste Job Description", height=180)
    uploaded_files = st.file_uploader("📂 Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

    if st.button("🚀 Analyze Resumes"):
        if not job_description:
            st.warning("⚠️ Please enter a Job Description first.")
        elif not uploaded_files:
            st.warning("⚠️ Please upload at least one resume.")
        else:
            st.info("⏳ Analyzing resumes... please wait...")
            jd_text = job_description.lower()
            results = []

            for file in uploaded_files:
                resume_text = extract_text_from_pdf(file)
                similarity = calculate_similarity(jd_text, resume_text)
                skills_found = extract_skills(resume_text)
                results.append({
                    "name": file.name,
                    "match": similarity,
                    "skills": ", ".join(skills_found) if skills_found else "No skills detected"
                })

            results = sorted(results, key=lambda x: x["match"], reverse=True)
            st.success("✅ Nuvora Analysis Complete!")

            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True)

            # Bar Chart
            names = [r["name"] for r in results]
            scores = [r["match"] for r in results]

            fig, ax = plt.subplots()
            ax.barh(names, scores, color="#0078FF")
            ax.set_xlabel("Match %")
            ax.set_ylabel("Resume")
            ax.set_title("Resume Match Percentage")
            plt.gca().invert_yaxis()
            st.pyplot(fig)

            best = results[0]
            st.markdown(f"### 🥇 Top Match: **{best['name']}** — {best['match']}%")
            st.markdown(f"**🧠 Skills Mentioned:** {best['skills']}")
            st.balloons()

    st.markdown("</div>", unsafe_allow_html=True)

# --- RIGHT: AI CHAT ASSISTANT ---
with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💬 Ask Nuvora — AI Career Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "bot", "content": "👋 Hi! I'm Nuvora, your AI career assistant. Ask about resumes, ATS, or interviews."}
        ]

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-user'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'>{msg['content']}</div>", unsafe_allow_html=True)
        st.markdown("<div style='clear:both;'></div>", unsafe_allow_html=True)

    user_input = st.chat_input("Ask something about your resume or job interview...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        answer = ""

        try:
            if client:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are Nuvora, a smart career assistant giving detailed professional resume and ATS advice."},
                        *st.session_state.chat_history
                    ],
                    max_tokens=400,
                    temperature=0.5
                )
                answer = response.choices[0].message.content.strip()
            else:
                answer = "⚠️ AI unavailable. Please set your OpenAI API key in Streamlit Secrets."
        except Exception:
            answer = "⚠️ Connection issue. Try again later."

        st.session_state.chat_history.append({"role": "bot", "content": answer})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

