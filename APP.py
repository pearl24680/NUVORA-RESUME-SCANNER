import streamlit as st
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader
import pandas as pd
import tempfile

# -------------------------------
# Data Science Keywords
# -------------------------------
DATA_SCIENCE_KEYWORDS = [
    'Python', 'R', 'SQL', 'Pandas', 'NumPy', 'Scikit-learn', 
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 
    'Data Analysis', 'Data Visualization', 'Matplotlib', 'Seaborn', 
    'Statistics', 'Regression', 'Classification', 'Clustering', 'NLP'
]

# -------------------------------
# Functions
# -------------------------------
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_file.seek(0)
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return text.lower()

def compute_ats_score(resume_text):
    matches = [kw for kw in DATA_SCIENCE_KEYWORDS if kw.lower() in resume_text]
    missing = [kw for kw in DATA_SCIENCE_KEYWORDS if kw.lower() not in resume_text]
    ats_score = round(len(matches) / len(DATA_SCIENCE_KEYWORDS) * 100, 2)
    return ats_score, matches, missing

def generate_bar_graph(matches, missing):
    labels = ['Matched Keywords', 'Missing Keywords']
    values = [len(matches), len(missing)]

    plt.figure(figsize=(6,4))
    plt.bar(labels, values, color=['green','red'])
    plt.title('Resume Keyword Matching')
    plt.ylabel('Number of Keywords')
    plt.tight_layout()
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name)
    plt.close()
    return temp_file.name

def generate_pie_chart(ats_score):
    labels = ['Selection Chance', 'Remaining']
    values = [ats_score, 100 - ats_score]

    plt.figure(figsize=(5,5))
    plt.pie(values, labels=labels, colors=['green','lightgrey'], autopct='%1.1f%%', startangle=90)
    plt.title('Chances of Selection')
    plt.tight_layout()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name)
    plt.close()
    return temp_file.name

def suggest_resume_content(missing_keywords):
    return [f"Include '{kw}' in your resume." for kw in missing_keywords]

# -------------------------------
# Streamlit App
# -------------------------------
st.set_page_config(layout="wide")
st.title("Data Science Resume Analyzer & ATS Score")

resume_file = st.file_uploader("Upload Resume (PDF)", type=['pdf'])
job_description = st.text_area("Paste Job Description here (Optional)")

if resume_file:
    resume_text = extract_text_from_pdf(resume_file)
    ats_score, matches, missing = compute_ats_score(resume_text)

    # ---------------- Bar Graph ----------------
    st.subheader("Keyword Matching Graph")
    bar_graph_path = generate_bar_graph(matches, missing)
    st.image(bar_graph_path)

    # ---------------- Pie Chart ----------------
    st.subheader("Chances of Selection")
    pie_chart_path = generate_pie_chart(ats_score)
    st.image(pie_chart_path)

    # ---------------- ATS Score ----------------
    st.subheader("ATS Score")
    st.progress(int(ats_score))
    st.write(f"Your ATS score is: **{ats_score}%**")

    # ---------------- Matched & Missing Keywords ----------------
    st.subheader("Matched Keywords")
    st.write(", ".join(matches) if matches else "No keywords matched.")

    st.subheader("Missing Keywords / Suggestions")
    suggestions = suggest_resume_content(missing)
    for s in suggestions:
        st.write(f"- {s}")

    # ---------------- Summary Table ----------------
    st.subheader("Keyword Summary Table")
    summary_df = pd.DataFrame({
        'Keyword': DATA_SCIENCE_KEYWORDS,
        'Status': ['Matched' if kw in matches else 'Missing' for kw in DATA_SCIENCE_KEYWORDS]
    })
    st.dataframe(summary_df)

    if job_description:
        st.subheader("Additional Notes")
        st.write("Job description provided; ATS score is based on standard Data Science keywords.")

