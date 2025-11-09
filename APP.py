import streamlit as st
import PyPDF2
import re
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer, util
import nltk
nltk.download('punkt')
# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------
st.set_page_config(page_title="💫 Nuvora Resume Scanner", page_icon="💼", layout="wide")

# -------------------------------------------------
# CUSTOM CSS - SKY THEME
# -------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom right, #E6F0FF, #F8FBFF);
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

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("💫 Nuvora — AI Resume Screening System")
st.caption("Developed by Pearl & Vasu | Final Year Project")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.header("📋 How to Use")
st.sidebar.write("""
1️⃣ Paste your **Job Description**  
2️⃣ Upload one or more **Resume PDFs**  
3️⃣ Click **Analyze Resumes 🚀**  
4️⃣ View **Match %, Extracted Skills**, and **Top Candidate**
""")

# -------------------------------------------------
# INPUT SECTION
# -------------------------------------------------
job_description = st.text_area("📄 Paste Job Description", height=180, placeholder="Example: Looking for Data Analyst skilled in Python, SQL, Power BI, Excel...")
uploaded_files = st.file_uploader("📂 Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

# -------------------------------------------------
# LOAD BERT MODEL
# -------------------------------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# -------------------------------------------------
# FUNCTIONS
# -------------------------------------------------
def extract_text_from_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return text.lower()

def calculate_similarity(jd_text, resume_text):
    jd_embed = model.encode(jd_text, convert_to_tensor=True)
    resume_embed = model.encode(resume_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(jd_embed, resume_embed).item()
    return round(similarity * 100, 2)

def extract_skills(text):
    skill_set = [
        "python", "java", "c++", "html", "css", "javascript", "sql", "mongodb",
        "react", "node", "machine learning", "deep learning", "nlp", "data analysis",
        "data visualization", "power bi", "tableau", "excel", "pandas", "numpy",
        "matplotlib", "seaborn", "tensorflow", "keras", "communication", "leadership",
        "problem solving", "teamwork", "critical thinking", "data science",
        "flask", "django", "git", "github"
    ]
    found = [skill.title() for skill in skill_set if re.search(rf"\\b{skill}\\b", text, re.IGNORECASE)]
    return list(set(found))

# -------------------------------------------------
# MAIN LOGIC
# -------------------------------------------------
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
            if len(resume_text.strip()) == 0:
                st.error(f"❌ {file.name}: No readable text found in PDF.")
                continue
            similarity = calculate_similarity(jd_text, resume_text)
            skills_found = extract_skills(resume_text)
            results.append({
                "Resume": file.name,
                "Match %": similarity,
                "Skills Found": ", ".join(skills_found) if skills_found else "No skills detected"
            })

        if not results:
            st.error("No valid resumes found!")
        else:
            results = sorted(results, key=lambda x: x["Match %"], reverse=True)

            st.success("✅ Nuvora Analysis Complete!")
            st.subheader("🏆 Resume Ranking (AI Match %)")
            st.dataframe(results, use_container_width=True)

            # Graph
            st.subheader("📊 Resume Match Percentage Comparison")
            names = [r["Resume"] for r in results]
            scores = [r["Match %"] for r in results]
            fig, ax = plt.subplots()
            ax.barh(names, scores, color="#0078FF")
            ax.set_xlabel("Match %")
            ax.set_ylabel("Resume Name")
            ax.set_title("Resume vs Job Description Match")
            plt.gca().invert_yaxis()
            st.pyplot(fig)

            # Best Match
            best = results[0]
            st.markdown(f"### 🥇 **Top Candidate:** `{best['Resume']}` — **{best['Match %']}%**")
            st.markdown(f"**🧠 Skills Mentioned:** {best['Skills Found']}")
            st.balloons()

st.markdown("---")
st.markdown("💼 **Nuvora Resume Scanner** | Final Year Project | 🚀")
