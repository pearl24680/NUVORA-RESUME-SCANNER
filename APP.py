import streamlit as st
import PyPDF2
import nltk
import re
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Nuvora Resume Scanner", page_icon="🤖", layout="wide")

st.title("💫 Nuvora Resume Scanner — AI Resume Screener using NLP")
st.caption("Developed by Pearl Sethi | Final Year Project | Powered by AI & NLP 🧠")

# -------------------------------
# SIDEBAR INFO
# -------------------------------
st.sidebar.header("📋 How to Use")
st.sidebar.write("""
1️⃣ Paste your **Job Description**  
2️⃣ Upload one or more **Resume PDFs**  
3️⃣ Click **Analyze Resumes 🚀**  
4️⃣ See **Match %, Skills Extracted**, and **Top Candidate**
""")

# -------------------------------
# INPUT SECTION
# -------------------------------
job_description = st.text_area("📄 Paste Job Description", height=200, placeholder="Example: Looking for Data Analyst skilled in Python, SQL, Power BI...")
uploaded_files = st.file_uploader("📂 Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def extract_text_from_pdf(file):
    """Extracts all text from a PDF file."""
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.lower()

def calculate_similarity(jd_text, resume_text):
    """Calculates cosine similarity between JD and Resume."""
    documents = [jd_text, resume_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 2)

def extract_skills(text):
    """Extracts predefined technical and soft skills from resume text."""
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
# MAIN ANALYSIS SECTION
# -------------------------------
if st.button("🚀 Analyze Resumes"):
    if not job_description:
        st.warning("⚠️ Please enter a Job Description first.")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one resume.")
    else:
        st.info("⏳ Nuvora is analyzing resumes... please wait...")

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

        # Sort by similarity
        results = sorted(results, key=lambda x: x["match"], reverse=True)

        st.success("✅ Nuvora Analysis Complete!")

        # Display Results Table
        st.subheader("🏆 Resume Ranking")
        st.dataframe(results, use_container_width=True)

        # Visualization
        st.subheader("📊 Resume Match % Comparison")
        names = [r["name"] for r in results]
        scores = [r["match"] for r in results]

        fig, ax = plt.subplots()
        ax.barh(names, scores, color="#8ecae6")
        ax.set_xlabel("Match %")
        ax.set_ylabel("Resume")
        ax.set_title("Resume Match Percentage")
        plt.gca().invert_yaxis()
        st.pyplot(fig)

        # Show top match
        best = results[0]
        st.markdown(f"### 🥇 Top Match: **{best['name']}** — {best['match']}%")
        st.markdown(f"**🧠 Skills Mentioned:** {best['skills']}")
        st.balloons()

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown("💼 **Nuvora Resume Scanner** | AI-powered screening system built using Python & NLP 🚀")
