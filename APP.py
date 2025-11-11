import streamlit as st
import PyPDF2
import re
import nltk
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="Nuvora - Resume Screening", page_icon="💫", layout="wide")

# -------------------------------
# Custom Styling
# -------------------------------
st.markdown("""
    <style>
        body { background-color: #E6F0FF; }
        .stApp { background-color: #E6F0FF; }
        .stButton button {
            background-color: #0078FF;
            color: white;
            border-radius: 10px;
            padding: 10px 25px;
            font-weight: bold;
            border: none;
        }
        .stButton button:hover {
            background-color: #005FCC;
            color: white;
        }
        textarea {
            background-color: white !important;
            color: #000 !important;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Header
# -------------------------------
st.title("💫 Nuvora — AI Resume Screening System")
st.caption("Developed by Pearl Sethi | Final Year Project")

# -------------------------------
# Inputs
# -------------------------------
job_desc = st.text_area("📄 Paste Job Description", height=200)
uploaded_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])

# -------------------------------
# Helper Functions
# -------------------------------
def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.lower()

def calculate_similarity(jd, resume):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([jd, resume])
    return round(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100, 2)

def extract_skills(text):
    skills = [
        "python", "java", "sql", "machine learning", "deep learning", "data science", "pandas", "numpy",
        "matplotlib", "tensorflow", "keras", "power bi", "tableau", "excel", "data visualization",
        "statistics", "flask", "django", "communication", "teamwork", "problem solving"
    ]
    found = [s for s in skills if re.search(rf"\\b{s}\\b", text)]
    return found, list(set(skills) - set(found))

# -------------------------------
# Main Logic
# -------------------------------
if st.button("🚀 Analyze Resume"):
    if not job_desc or not uploaded_file:
        st.warning("⚠️ Please provide both Job Description and Resume.")
    else:
        jd_text = job_desc.lower()
        resume_text = extract_text_from_pdf(uploaded_file)

        ats_score = calculate_similarity(jd_text, resume_text)
        found_skills, missing_skills = extract_skills(resume_text)

        # Display results
        st.success(f"✅ Nuvora Analysis Complete! ATS Score: **{ats_score}%**")

        # 📊 ATS Graph
        st.subheader("📊 Selection Probability")
        fig, ax = plt.subplots()
        ax.bar(["ATS Score"], [ats_score], color="#0078FF")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Percentage")
        ax.set_title("Resume Selection Probability")
        st.pyplot(fig)

        # 🧠 Skill Analysis
        st.subheader("🧠 Skill Analysis")
        st.write(f"**Skills Detected:** {', '.join(found_skills) if found_skills else 'None'}")
        st.write(f"**Missing Important Skills:** {', '.join(missing_skills)}")

        # 🎯 Selection Probability Message
        if ats_score >= 85:
            st.success("Excellent match! High chance of shortlisting ✅")
        elif ats_score >= 70:
            st.info("Good match. You can improve a few points for a higher ATS score.")
        else:
            st.warning("Low match. Consider revising your resume to match the job description better.")

        # 💡 Suggestions for Data Science
        st.subheader("💡 Resume Suggestions (For Data Science Profile)")
        suggestions = [
            "Add projects demonstrating hands-on data analysis or model building.",
            "Mention frameworks like Scikit-learn, TensorFlow, or PyTorch.",
            "Highlight experience with data visualization tools (Power BI, Tableau).",
            "Include any Kaggle or internship experience.",
            "Focus on problem statements, not just tools."
        ]
        for s in suggestions:
            st.markdown(f"✅ {s}")

        st.balloons()

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("💼 Built with ❤️ using Python, NLP & Streamlit | © 2025 Nuvora")
