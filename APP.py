import streamlit as st
import pdfplumber
import docx
import re
import matplotlib.pyplot as plt

# ---------------------------------------------
# PAGE CONFIG
# ---------------------------------------------
st.set_page_config(page_title="Nuvora AI Job Assistant Dashboard", layout="wide")

# ---------------------------------------------
# CSS STYLING
# ---------------------------------------------
st.markdown("""
<style>
body { background-color: #f0f3ff; }
div[data-testid="stSidebar"] { background-color: #dbe8ff; }
.big-font { font-size:30px !important; font-weight:700; color:#003366; }
.section-box {
    background-color:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0px 0px 10px rgba(0,0,0,0.1);
    margin-bottom:20px;
}
.metric-box {
    background:#edf3ff;
    padding:15px;
    border-radius:10px;
    text-align:center;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------
# FUNCTIONS
# ---------------------------------------------
def extract_text(uploaded_file):
    """Extract text from PDF or DOCX"""
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

def analyze_resume(resume_text, jd_text=""):
    """Analyze Resume vs optional JD"""
    resume_text = resume_text.lower()
    jd_text = jd_text.lower() if jd_text else ""

    ds_keywords = [
        "python", "machine learning", "data analysis", "sql", "excel", "pandas",
        "numpy", "deep learning", "statistics", "power bi", "tableau",
        "visualization", "modeling", "ai", "communication", "teamwork",
        "data cleaning", "eda", "nlp", "classification", "regression"
    ]

    found = [kw for kw in ds_keywords if kw in resume_text]
    missing = [kw for kw in ds_keywords if kw not in found]
    ats_score = int((len(found) / len(ds_keywords)) * 100)

    jd_keywords = []
    if jd_text:
        jd_keywords = list(set(re.findall(r'\b[a-zA-Z]{4,}\b', jd_text)))

    return ats_score, found, missing, jd_keywords

def extract_projects(resume_text):
    project_patterns = [
        r'(?i)(projects?|academic projects?|personal projects?|internship projects?)[:\-]?\s*(.*)',
        r'(?i)(?:\*\*|##|###)?\s*Project\s*[:\-]?\s*(.*)'
    ]
    matches = []
    for pattern in project_patterns:
        found = re.findall(pattern, resume_text)
        for f in found:
            if isinstance(f, tuple):
                matches.append(f[1])
            else:
                matches.append(f)
    return list(set(matches))

def plot_ats(ats_score):
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.barh(["ATS Match"], [ats_score], color="#6a9efc")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score (%)")
    for i, v in enumerate([ats_score]):
        ax.text(v + 2, i, f"{v}%", va='center', fontweight='bold')
    st.pyplot(fig)

# ---------------------------------------------
# DASHBOARD LAYOUT
# ---------------------------------------------
st.markdown("<p class='big-font'>💎 Nuvora AI Job Assistant Dashboard</p>", unsafe_allow_html=True)
st.markdown("Upload your **resume** (and optional Job Description)** to see instant ATS analysis, keyword insights, and projects.**")

resume_file = st.file_uploader("📄 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
jd_file = st.file_uploader("💼 (Optional) Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

if resume_file:
    resume_text = extract_text(resume_file)
    jd_text = ""
    if jd_file:
        if jd_file.name.endswith(".txt"):
            jd_text = jd_file.read().decode("utf-8")
        else:
            jd_text = extract_text(jd_file)

    ats_score, found, missing, jd_keywords = analyze_resume(resume_text, jd_text)
    projects = extract_projects(resume_text)

    # -------------- DASHBOARD SECTIONS --------------
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-box'>📊 ATS Score<br><span style='font-size:28px;color:#004080'>{ats_score}%</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-box'>✅ Matched Keywords<br><span style='font-size:28px;color:#008000'>{len(found)}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-box'>⚠️ Missing Keywords<br><span style='font-size:28px;color:#ff3300'>{len(missing)}</span></div>", unsafe_allow_html=True)

    st.markdown("### 📈 Resume ATS Match Graph")
    plot_ats(ats_score)

    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("✅ Matched Keywords")
    st.write(", ".join(found) if found else "No keywords found.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("⚠️ Missing Keywords")
    st.write(", ".join(missing) if missing else "None 🎉 Your resume covers all key terms!")
    st.markdown("</div>", unsafe_allow_html=True)

    if jd_keywords:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("📋 Job Description Keywords")
        st.write(", ".join(jd_keywords[:40]) + " ...")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("💼 Projects Detected in Resume")
    if projects:
        for i, project in enumerate(projects, 1):
            st.write(f"**{i}.** {project.strip()}")
    else:
        st.write("No projects detected. Make sure your project section is properly labeled.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("🧠 Suggestions for Improvement")
    st.markdown("""
    - Add missing **data science tools** (like Power BI, SQL, or EDA if absent).  
    - Include **quantifiable results** in your project descriptions.  
    - Match **JD language** (use same keywords as employer).  
    - Emphasize **communication, teamwork, and analytical thinking**.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("👆 Upload your resume to generate your career dashboard.")
