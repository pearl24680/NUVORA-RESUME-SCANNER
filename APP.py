# app.py
import streamlit as st
import PyPDF2, io, re
import nltk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt', quiet=True)

# ------------------ Page config & style ------------------
st.set_page_config(page_title="Nuvora Resume Scanner", page_icon="💫", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #E6F0FF; }
    .reportview-container .main .block-container{ padding-top:1rem; }
    .big-title {font-size:34px; font-weight:700; color:#002B5B}
    .card {background: white; border-radius: 8px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.08)}
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ Header ------------------
col1, col2 = st.columns([8,2])
with col1:
    st.markdown('<div class="big-title">💫 Nuvora — AI Job Assistant Dashboard</div>', unsafe_allow_html=True)
    st.write("Upload Job Description and Resumes — get ATS score, missing keywords, charts and suggestions.")
with col2:
    st.write("")
    st.write("")
    st.image("https://raw.githubusercontent.com/pearl-sethi/assets/main/nuvora-icon.png" if False else "https://i.imgur.com/3yBvQdA.png", width=70)  # optional icon

# ------------------ Sidebar ------------------
st.sidebar.title("🔎 Navigation")
page = st.sidebar.radio("Go to:", ["Dashboard", "ATS Analysis", "Project Extraction", "AI Career Chat"])

st.sidebar.markdown("---")
st.sidebar.header("📂 Upload Files")
resume_files = st.sidebar.file_uploader("Upload Resume PDFs (multiple)", type=["pdf"], accept_multiple_files=True)
job_text_input = st.sidebar.text_area("Or paste Job Description (optional)", height=150)
job_file = st.sidebar.file_uploader("Upload Job Description (PDF) (optional)", type=["pdf"])

st.sidebar.markdown("---")
st.sidebar.caption("Tip: For best ATS score, paste the exact Job Description and upload clean resumes (PDF/text).")

# ------------------ Helpers ------------------
def extract_text_from_pdf_file(file_obj):
    try:
        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for p in pdf_reader.pages:
            text += p.extract_text() or ""
        return text
    except Exception:
        # try reading bytes
        try:
            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_obj.read()))
            text = ""
            for p in pdf_reader.pages:
                text += p.extract_text() or ""
            return text
        except Exception:
            return ""

def clean_text(t: str):
    if not isinstance(t, str): return ""
    t = re.sub(r'\s+', ' ', t)
    return t.strip().lower()

# A curated skill list (extend as needed)
SKILL_CANDIDATE = [
    "python","pandas","numpy","scikit-learn","sklearn","tensorflow","keras","pytorch",
    "sql","nosql","mongodb","power bi","tableau","excel","data visualization","matplotlib","seaborn",
    "machine learning","deep learning","nlp","natural language processing","statistics","probability",
    "data analysis","data science","feature engineering","modeling","deployment","flask","django",
    "git","github","aws","azure","gcp","bigquery","spark","hadoop","docker","kubernetes","communication",
    "teamwork","leadership","problem solving","sql server","hive","airflow"
]

def extract_skills_from_text(text: str, skill_list=SKILL_CANDIDATE):
    text_l = text.lower()
    found = []
    for skill in skill_list:
        # match word boundary to avoid partial matches
        if re.search(rf'\b{re.escape(skill)}\b', text_l):
            found.append(skill)
    return list(set(found))

def compute_ats(jd_text: str, resume_text: str, weight_similarity=0.7, weight_skill=0.3):
    # similarity
    try:
        vec = TfidfVectorizer(stop_words='english').fit_transform([jd_text, resume_text])
        sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
    except Exception:
        sim = 0.0
    # skill match ratio (skills mentioned in JD vs resume)
    jd_skills = extract_skills_from_text(jd_text)
    resume_skills = extract_skills_from_text(resume_text)
    if len(jd_skills) == 0:
        skill_ratio = 1.0 if len(resume_skills) > 0 else 0.0
    else:
        skill_ratio = len(set(jd_skills).intersection(set(resume_skills))) / len(set(jd_skills))
    # weighted score
    score = (weight_similarity * sim + weight_skill * skill_ratio) * 100
    return round(score, 2), sim, skill_ratio, jd_skills, resume_skills

def suggest_improvements(jd_skills, resume_skills):
    missing = [s for s in jd_skills if s not in resume_skills]
    suggestions = []
    if "python" not in resume_skills:
        suggestions.append("Add Python projects or mention Python experience (libraries like pandas/numpy).")
    if any(k in jd_skills for k in ["machine learning","deep learning","nlp"]):
        if "machine learning" not in resume_skills and "deep learning" not in resume_skills:
            suggestions.append("Include ML project(s): dataset, model, metrics (accuracy, F1).")
    if "data visualization" in jd_skills or any(x in jd_skills for x in ["tableau","power bi","matplotlib","seaborn"]):
        suggestions.append("Add a visualization project and mention tools (Tableau/Power BI/Matplotlib/Seaborn).")
    if "deployment" in jd_skills or any(x in jd_skills for x in ["flask","django","docker","kubernetes"]):
        suggestions.append("Mention if you've deployed models/APIs (Flask/Docker) or used cloud services (AWS/GCP).")
    if "sql" in jd_skills and "sql" not in resume_skills:
        suggestions.append("Add SQL projects or mention database experience (queries, joins, optimization).")
    # fallback missing list
    if missing and not suggestions:
        suggestions = [f"Consider adding: {', '.join(missing)}"]
    return missing, suggestions

# ------------------ Page: Dashboard ------------------
if page == "Dashboard":
    st.subheader("Dashboard Overview")
    colA, colB, colC = st.columns([2,1,1])
    if resume_files and (job_text_input or job_file):
        st.info("Ready to analyze uploaded resumes.")
    else:
        st.info("Upload resume(s) in the sidebar and paste job description or upload job PDF.")

    # show quick stats if we have data
    if resume_files:
        st.write(f"Uploaded resumes: **{len(resume_files)}**")
    if job_text_input:
        st.write("Job Description: **Provided (text)**")
    if job_file:
        st.write("Job Description: **Provided (PDF)**")

# ------------------ Page: ATS Analysis ------------------
if page == "ATS Analysis":
    st.header("🧾 ATS Analysis")

    if not resume_files:
        st.warning("Upload at least one resume PDF in the sidebar to start analysis.")
    else:
        # get job description text
        jd_text = ""
        if job_text_input:
            jd_text = job_text_input
        elif job_file:
            jd_text = extract_text_from_pdf_file(job_file)
        else:
            st.warning("Please paste job description text or upload a JD PDF in the sidebar.")
            jd_text = ""

        jd_text = clean_text(jd_text)

        results = []
        for f in resume_files:
            r_text = extract_text_from_pdf_file(f)
            r_text_clean = clean_text(r_text)
            ats_score, sim, skill_ratio, jd_skills, resume_skills = compute_ats(jd_text, r_text_clean)
            missing, suggestions = suggest_improvements(jd_skills, resume_skills)
            results.append({
                "file": f.name,
                "ats_score": ats_score,
                "similarity": round(sim*100,2),
                "skill_match_ratio": round(skill_ratio*100,2),
                "found_skills": resume_skills,
                "missing_skills": missing,
                "suggestions": suggestions
            })

        # sort by ats_score
        results = sorted(results, key=lambda x: x["ats_score"], reverse=True)

        # Summary top cards
        top_score = results[0]["ats_score"] if results else 0
        total_matches = sum(len(r["found_skills"]) for r in results)
        total_missing = sum(len(r["missing_skills"]) for r in results)
        c1, c2, c3 = st.columns(3)
        c1.metric("Top ATS Score", f"{top_score}%")
        c2.metric("Total Skills Detected", total_matches)
        c3.metric("Total Missing Keywords", total_missing)

        # Table of results
        df = pd.DataFrame([{
            "Resume": r["file"],
            "ATS Score (%)": r["ats_score"],
            "Similarity (%)": r["similarity"],
            "Skill Match (%)": r["skill_match_ratio"],
            "Found Skills": ", ".join(r["found_skills"]) if r["found_skills"] else "—",
            "Missing": ", ".join(r["missing_skills"]) if r["missing_skills"] else "—"
        } for r in results])

        st.subheader("🏆 Ranked Resumes")
        st.dataframe(df, use_container_width=True)

        # Bar chart
        st.subheader("📊 Resume Selection Probability")
        fig, ax = plt.subplots(figsize=(8, max(2, len(results)*0.6)))
        names = [r["file"] for r in results]
        scores = [r["ats_score"] for r in results]
        ax.barh(names, scores, color="#0078FF")
        ax.set_xlim(0, 100)
        ax.set_xlabel("ATS Score (%)")
        ax.set_title("Selection Probability (ATS)")
        ax.invert_yaxis()
        for i, v in enumerate(scores):
            ax.text(v + 1, i, f"{v}%", va='center')
        st.pyplot(fig)

        # detailed expanders per resume
        st.subheader("🔎 Resume Details & Suggestions")
        for r in results:
            with st.expander(f"{r['file']} — {r['ats_score']}%"):
                st.write(f"**Found skills:** {', '.join(r['found_skills']) if r['found_skills'] else 'None'}")
                st.write(f"**Missing (according to JD):** {', '.join(r['missing_skills']) if r['missing_skills'] else 'None'}")
                st.write("**Suggestions to improve this resume:**")
                for s in r["suggestions"]:
                    st.markdown(f"- {s}")
                # optional: show short text preview of resume (first 800 chars)
                try:
                    txt = extract_text_from_pdf_file([f_obj for f_obj in resume_files if f_obj.name==r["file"]][0])
                    st.text_area("Resume preview (first 1000 chars):", value=txt[:1000], height=150)
                except Exception:
                    pass

# ------------------ Page: Project Extraction ------------------
if page == "Project Extraction":
    st.header("📁 Project / Experience Extraction")
    st.write("This section extracts project titles and lines that often represent projects (simple heuristic).")
    if not resume_files:
        st.warning("Upload resumes in the sidebar to extract projects.")
    else:
        for f in resume_files:
            st.subheader(f.name)
            txt = extract_text_from_pdf_file(f)
            # simple rule: lines containing 'project' or 'implemented' or 'developed'
            lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
            candidates = [ln for ln in lines if re.search(r'project|implemented|developed|designed|built', ln, re.IGNORECASE)]
            if not candidates:
                st.info("No clear project lines found by heuristic.")
            else:
                for c in candidates[:10]:
                    st.markdown(f"- {c}")

# ------------------ Page: AI Career Chat ------------------
if page == "AI Career Chat":
    st.header("💬 Ask Nuvora — Career & Resume Assistant")
    st.write("You can ask suggestions like 'How to improve my resume for Data Science?' or 'What projects should I add?'")
    user_q = st.text_input("Ask Nuvora (type your question)...")
    OPENAI_KEY = st.secrets.get("openai_api_key", "") if "openai_api_key" in st.secrets else ""
    if st.button("Ask"):
        if not user_q:
            st.warning("Type a question first.")
        else:
            if OPENAI_KEY:
                # If you want to use OpenAI, you can add code here to call the API.
                st.info("OpenAI key found in Streamlit secrets — calling GPT (if configured).")
                st.write("**(OpenAI integration available — add your key to Streamlit secrets to enable GPT responses)**")
                st.write("Local quick reply:")
                st.write("Try adding concrete projects, metrics (accuracy, revenue), and tools used (Python, SQL, Tableau).")
            else:
                # local rule-based responses
                q = user_q.lower()
                if "improve" in q or "how to" in q:
                    st.write("Suggestions to improve resume:")
                    st.write("- Add a clear 'Projects' section with 2-3 hands-on projects (dataset, goal, model, results).")
                    st.write("- Mention tools/libraries used and metrics (accuracy, F1-score) and deployment details.")
                    st.write("- Keep bullet points concise and use action verbs (Implemented, Designed, Deployed).")
                elif "projects" in q:
                    st.write("Project ideas for Data Science:")
                    st.write("- Sales prediction with feature engineering (XGBoost, evaluation & dashboard).")
                    st.write("- NLP sentiment analysis with transformer & deployment using Flask.")
                    st.write("- Image classification pipeline with transfer learning and model explainability.")
                else:
                    st.write("Nuvora tip: Be specific — ask like 'What projects should I use to show SQL skills?'")

# ------------------ Footer ------------------
st.markdown("---")
st.caption("Nuvora  | Final Year Project")
