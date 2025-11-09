# app.py
import streamlit as st
from PyPDF2 import PdfReader
import re
import time
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import io

# Optional OpenAI import (used only if key provided)
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# ---------------------------
# Page config and CSS
# ---------------------------
st.set_page_config(page_title="Nuvora AI — ATS Resume Analyzer", layout="wide",
                   page_icon="💫")

st.markdown(
    """
    <style>
      body {background: linear-gradient(180deg,#e8f5ff 0%, #f9fcff 100%);}
      .title {font-size:36px; font-weight:800; color:#012a4a; text-align:center;}
      .subtitle {font-size:14px; color:#045a8d; text-align:center; margin-bottom:20px;}
      .card {background:#fff; border-radius:12px; padding:18px; box-shadow:0 6px 20px rgba(2,48,71,0.06);}
      .small {font-size:13px; color:#0b2948}
      .chat-user {background:#0078ff; color:#fff; padding:10px 14px; border-radius:18px; display:inline-block; margin:6px 0; float:right;}
      .chat-bot {background:#fff; color:#012a4a; padding:10px 14px; border-radius:18px; display:inline-block; margin:6px 0; float:left;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">💫 Nuvora AI — ATS Resume Analyzer & Career Coach</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload resumes, paste job descriptions, get ATS score, skill gaps, and AI career advice.</div>', unsafe_allow_html=True)

# ---------------------------
# Helper functions
# ---------------------------
def clean_text(txt: str) -> str:
    if not txt:
        return ""
    txt = re.sub(r'\s+', ' ', txt)  # collapse whitespace/newlines
    txt = re.sub(r'\u200b', '', txt)  # remove zero-width
    return txt.strip()

def extract_text_from_pdf(uploaded_file) -> str:
    try:
        reader = PdfReader(uploaded_file)
    except Exception:
        return ""
    text = ""
    for page in reader.pages:
        p = page.extract_text() or ""
        text += p + " "
    return clean_text(text.lower())

# predefined skill list (extend as needed)
DEFAULT_SKILLS = [
    "python","java","c++","c#","sql","excel","r","pandas","numpy","matplotlib","seaborn",
    "power bi","tableau","machine learning","deep learning","nlp","tensorflow","keras",
    "scikit-learn","django","flask","git","github","aws","azure","gcp","docker","kubernetes",
    "data analysis","data visualization","communication","leadership","problem solving"
]

def extract_skills(text: str, skill_list=DEFAULT_SKILLS, fuzzy_threshold=80):
    found = set()
    text = clean_text(text).lower()
    # Exact boundary match first
    for skill in skill_list:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text):
            found.add(skill.title())
    # Fuzzy pass for cases like "Py thon" or minor OCR issues
    if not found:
        for skill in skill_list:
            if fuzz.partial_ratio(skill.lower(), text) >= fuzzy_threshold:
                found.add(skill.title())
    return sorted(list(found))

def compute_tfidf_similarity(jd: str, resume: str):
    if not jd.strip() or not resume.strip():
        return 0.0
    vect = TfidfVectorizer(stop_words='english').fit([jd, resume])
    tfidf = vect.transform([jd, resume])
    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(float(sim) * 100, 2)

def ats_scoring(resume_text: str, jd_text: str):
    resume_text = clean_text(resume_text.lower())
    jd_text = clean_text(jd_text.lower())

    skills_resume = extract_skills(resume_text)
    skills_jd = extract_skills(jd_text)

    matched_skills = [s for s in skills_resume if s.lower() in [k.lower() for k in skills_jd]]
    # Skill match % (if JD lists skills)
    if skills_jd:
        skill_match_pct = round(len(matched_skills) / len(skills_jd) * 100, 2)
    else:
        skill_match_pct = 0.0

    # Section presence check (basic)
    sections = ["summary","objective","experience","education","skills","projects","certification","certifications"]
    found_sections = sum(1 for s in sections if s in resume_text)
    section_score = round((found_sections / len(sections)) * 100, 2)

    # TF-IDF semantic similarity between JD and resume
    semantic_pct = compute_tfidf_similarity(jd_text, resume_text)

    # Word count effect (penalize extremely short resumes)
    wc = max(0, len(resume_text.split()))
    wc_score = min(100, (wc / 500) * 100)  # if >=500 words -> 100

    # Overall composite ATS compatibility (weights can be tuned)
    overall = round(0.45 * skill_match_pct + 0.20 * semantic_pct + 0.20 * section_score + 0.15 * wc_score, 2)

    return {
        "skills_jd": skills_jd,
        "skills_resume": skills_resume,
        "matched_skills": matched_skills,
        "skill_match_pct": skill_match_pct,
        "section_score": section_score,
        "semantic_pct": semantic_pct,
        "word_count": wc,
        "wc_score": round(wc_score,2),
        "overall_score": overall
    }

# ---------------------------
# UI: Inputs
# ---------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
colA, colB = st.columns([2,1])

with colA:
    jd_text = st.text_area("📄 Paste Job Description (required for ATS comparison)", height=200, placeholder="E.g., Looking for Data Analyst with Python, SQL, Power BI...")
    jd_text = clean_text(jd_text)

with colB:
    st.write("📁 Upload resumes (PDF)")
    uploaded_files = st.file_uploader("Upload one or more resume PDFs", type=["pdf"], accept_multiple_files=True)
    st.write("Tip: Upload text-based (not scanned) PDFs for best results.")
st.markdown("</div>", unsafe_allow_html=True)

# Chat UI area
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# Analyze button and logic
# ---------------------------
if st.button("🚀 Analyze Uploaded Resumes"):
    if not jd_text:
        st.warning("Please paste a Job Description before analyzing.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume PDF.")
    else:
        results = []
        for f in uploaded_files:
            raw = extract_text_from_pdf(f)
            if not raw.strip():
                st.error(f"Could not extract text from {f.name}. Try a text-based PDF.")
                continue
            res = ats_scoring(raw, jd_text)
            # also compute TF-IDF semantic score separately (already included)
            res_row = {
                "file_name": f.name,
                "overall_score": res["overall_score"],
                "semantic_pct": res["semantic_pct"],
                "skill_match_pct": res["skill_match_pct"],
                "section_score": res["section_score"],
                "word_count": res["word_count"],
                "matched_skills": ", ".join(res["matched_skills"]) if res["matched_skills"] else "None",
                "skills_found": ", ".join(res["skills_resume"]) if res["skills_resume"] else "None",
            }
            results.append(res_row)

        if not results:
            st.error("No resumes were successfully analyzed.")
        else:
            # show sorted table & visuals
            df = pd.DataFrame(results).sort_values(by="overall_score", ascending=False)
            st.success("✅ Analysis complete!")
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("🏆 Resume Ranking (by ATS Compatibility)")
            st.dataframe(df[["file_name","overall_score","skill_match_pct","semantic_pct","section_score"]].rename(
                columns={"file_name":"Resume","overall_score":"ATS %","skill_match_pct":"Skill Match %","semantic_pct":"Semantic %","section_score":"Section Score %"}
            ), use_container_width=True)

            # bar chart for top results
            st.subheader("📊 Match Scores")
            chart_df = df[["file_name","overall_score"]].set_index("file_name")
            st.bar_chart(chart_df)

            # Detailed cards per resume
            st.subheader("📄 Detailed Resume Reports")
            for idx, row in df.iterrows():
                st.markdown(f"**{row['file_name']}** — ATS Score: **{row['overall_score']}%**")
                st.write(f"- Skill Match %: {row['skill_match_pct']}%")
                st.write(f"- Semantic similarity: {row['semantic_pct']}%")
                st.write(f"- Section score: {row['section_score']}%")
                st.write(f"- Word count: {row['word_count']}")
                st.write(f"- Skills found: {row['skills_found']}")
                st.write(f"- Matched skills: {row['matched_skills']}")
                st.markdown("---")

            # Download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Analysis CSV", data=csv, file_name="nuvora_analysis.csv", mime="text/csv")
            st.markdown("</div>", unsafe_allow_html=True)

            # Save last results in session for chat context
            st.session_state.last_df = df

# ---------------------------
# Chat - Career Assistant
# ---------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("💬 Ask Nuvora — Career Assistant (chat)")

# Option to set OpenAI API key in app (use secrets in production)
if OPENAI_AVAILABLE:
    api_key = st.sidebar.text_input("OpenAI API Key (optional — put in Secrets on Cloud)", type="password")
    if api_key:
        openai.api_key = api_key

# show chat history
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f"<div class='chat-user'>{m['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'>{m['content']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='clear:both;'></div>", unsafe_allow_html=True)

def fallback_bot_answer(prompt, last_df=None):
    p = prompt.lower()
    if "why" in p and "skill" in p:
        return "If skills are not detected, usually the PDF is scanned image (not text), or the skill names are written in uncommon forms. Try a text-based PDF or add a Skills section with exact keywords from the job description."
    if "get job" in p or "will i get" in p:
        return "I cannot guarantee a job. But improving your ATS score to 70%+ and tailoring your resume to the job increases chances. I can suggest improvements if you upload JD + resume."
    if "improve" in p or "how to" in p:
        return "Focus on adding a clear Skills section, using exact keywords from the job description, adding measurable achievements, and keeping formatting simple (no images/tables)."
    # If we have last analysis, give tailored tip
    if last_df is not None and not last_df.empty:
        top = last_df.iloc[0]
        return f"Top candidate in your upload has ATS score {top['overall_score']}%. Focus on adding the missing skills listed in the matched skills field and ensure a Skills section exists."
    return "I can analyze resumes and provide tips. Ask me about skills, ATS, or how to improve your resume."

# chat input
user_msg = st.chat_input("Ask career questions (e.g., 'How to improve my resume?', 'Why no skill detected?')")

if user_msg:
    # add user message to history
    st.session_state.messages.append({"role":"user", "content": user_msg})
    st.experimental_rerun()  # re-render to show user's bubble then respond (quick trick)

# produce a bot response if last action was user (session shows last)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user = st.session_state.messages[-1]["content"]
    with st.spinner("Nuvora is thinking..."):
        answer = None
        # priority: use OpenAI if key available and library installed
        if OPENAI_AVAILABLE and (openai.api_key or st.sidebar.text_input):
            try:
                # Use user-provided key if typed earlier
                if hasattr(openai, "api_key"):
                    pass
                # prefer gpt-3.5-turbo if gpt-4 not available
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role":"system", "content":"You are Nuvora, a professional career assistant who gives concise resume and ATS improvement advice."},
                        {"role":"user", "content": last_user}
                    ],
                    max_tokens=450,
                    temperature=0.2
                )
                answer = resp["choices"][0]["message"]["content"].strip()
            except Exception:
                answer = None

        if not answer:
            # fallback rule-based
            df_for_context = st.session_state.get("last_df", pd.DataFrame())
            answer = fallback_bot_answer(last_user, df_for_context)

        # append and display
        st.session_state.messages.append({"role":"bot", "content": answer})
        st.experimental_rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown("""
    <div style='text-align:center; margin-top:18px; color:#045a8d'>
      🚀 Nuvora AI — ATS Resume Analyzer • Make your resume ATS-friendly and get smarter career tips.
    </div>
""", unsafe_allow_html=True)
