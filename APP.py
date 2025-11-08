import streamlit as st
import PyPDF2
import nltk
import re
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="Nuvora - AI Resume Screener", page_icon="💼", layout="wide")

st.title("💫 SmartHire — AI Resume Screening using NLP")
st.caption("Developed by Pearl Sethi | Final Year Project | Powered by NLP 🧠")

# -------------------------------
# Input Section
# -------------------------------
st.sidebar.header("📋 Instructions")
st.sidebar.write("""
1️⃣ Paste a **Job Description**  
2️⃣ Upload one or more **Resume PDFs**  
3️⃣ Click **Analyze Resumes 🚀**  
4️⃣ View Match %, Skills, and Charts 📊  
""")

job_description = st.text_area("📄 Paste Job Description", height=200)
uploaded_files = st.file_uploader("📂 Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

# -------------------------------
# Helper Functions
# -------------------------------
def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def calculate_similarity(jd_text, resume_text):
    documents = [jd_text, resume_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 2)

def extract_skills(text):
    skills = [
        "python", "java", "c++", "machine learning", "deep learning", "data analysis",
        "sql", "excel", "tableau", "power bi", "communication", "teamwork",
        "html", "css", "javascript", "nlp", "pandas", "numpy", "matplotlib"
    ]
    found = [skill for skill in skills if re.search(rf"\\b{skill}\\b", text, re.IGNORECASE)]
    return list(set(found))

# -------------------------------
# Main Processing
# -------------------------------
if st.button("🚀 Analyze Resumes"):
    if not job_description:
        st.warning("⚠️ Please enter a Job Description first.")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one resume.")
    else:
        st.info("⏳ Analyzing resumes... please wait.")

        results = []
        for file in uploaded_files:
            resume_text = extract_text_from_pdf(file)
            similarity = calculate_similarity(job_description, resume_text)
            skills_found = extract_skills(resume_text)
            results.append({"name": file.name, "match": similarity, "skills": ", ".join(skills_found)})

        # Sort by best match
        results = sorted(results, key=lambda x: x["match"], reverse=True)

        st.success("✅ Analysis Complete!")

        # Display table
        st.subheader("🏆 Ranked Candidates")
        st.table(results)

        # Show bar chart
        st.subheader("📊 Resume Match Percentage")
        names = [r["name"] for r in results]
        scores = [r["match"] for r in results]

        fig, ax = plt.subplots()
        ax.barh(names, scores, color="skyblue")
        ax.set_xlabel("Match %")
        ax.set_ylabel("Resume Name")
        ax.set_title("Resume Ranking by Match %")
        st.pyplot(fig)

        # Highlight top candidate
        best = results[0]
        st.markdown(f"### 🥇 Best Match: **{best['name']}** — {best['match']}%")
        st.markdown(f"**Skills Found:** {best['skills']}")
        st.balloons()
