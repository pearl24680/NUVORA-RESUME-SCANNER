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
st.set_page_config(page_title="Nuvora Resume Scanner", page_icon="💫", layout="wide")

# -------------------------------
# CUSTOM CSS FOR LIGHT SKY THEME
# -------------------------------
st.markdown("""
    <style>
        body {
            background-color: #E6F0FF;
        }
        .stApp {
            background-color: #E6F0FF;
        }
        h1, h2, h3, h4, h5, h6, p, label {
            color: #002B5B !important;
        }
        .stButton button {
            background-color: #0078FF;
            color: white;
            border-radius: 10px;
            border: none;
            padding: 0.6em 1.2em;
            font-weight: bold;
        }
        .stButton button:hover {
            background-color: #005FCC;
            color: white;
        }
        textarea {
            background-color: #ffffff !important;
            color: #000 !important;
        }
        div[data-testid="stFileUploaderDropzone"] {
            background-color: #ffffff !important;
            border: 2px dashed #0078FF !important;
            border-radius: 10px !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.title("💫 Nuvora — AI Resume Screening System")
st.caption("Developed by Pearl and vasu | Final Year Project")

# -------------------------------
# SIDEBAR INFO
# -------------------------------
st.sidebar.header("📋 How to Use")
st.sidebar.write("""
1️⃣ Paste your **Job Description**  
2️⃣ Upload one or more **Resume PDFs**  
3️⃣ Click **Analyze Resumes 🚀**  
4️⃣ See **Match %, Extracted Skills**, and **Top Candidate**
""")

# -------------------------------
# INPUT SECTION
# -------------------------------
job_description = st.text_area("📄 Paste Job Description", height=200, placeholder="Example: Looking for Data Analyst skilled in Python, SQL, Power BI...")
uploaded_files = st.file_uploader("📂 Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

# -------------------------------
# FUNCTIONS
# -------------------------------
def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.lower()

def calculate_similarity(jd_text, resume_text):
    documents = [jd_text, resume_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 2)

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
# MAIN
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

        results = sorted(results, key=lambda x: x["match"], reverse=True)

        st.success("✅ Nuvora Analysis Complete!")

        st.subheader("🏆 Resume Ranking")
        st.dataframe(results, use_container_width=True)

        st.subheader("📊 Resume Match % Comparison")
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

st.markdown("---")
st.markdown("💼 **Nuvora Resume Scanner** | Final Year Project | Built using Python, NLP & Streamlit 🚀")
