import os
from pathlib import Path
import fitz  # PyMuPDF
import streamlit as st
import re

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="Nuvora Offline Job Assistant", layout="wide")

# -------------------- STYLING --------------------
st.markdown("""
<style>
body { background-color: #ffffff; color: #222; }
div[data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
.card { background-color: #f7f9fc; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# -------------------- FUNCTIONS --------------------
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page in pdf_document:
        text += page.get_text()
    pdf_document.close()
    return text

def extract_projects(text):
    # Look for Projects, Internships, Experience sections
    pattern = r"(?i)(projects?|internships?|experience)\s*[:\-]?\s*(.+)"
    matches = re.findall(pattern, text)
    projects = [m[1].strip() for m in matches]
    return list(set(projects))

# -------------------- SIDEBAR NAVIGATION --------------------
st.sidebar.title("📘 Nuvora Offline Job Assistant")
page = st.sidebar.radio("Navigate", ["🏠 Home", "💼 Project Extractor"])

# -------------------- HOME PAGE --------------------
if page == "🏠 Home":
    st.title("🏠 Home")
    st.info("Offline version: Upload and view resumes without AI.")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        show_pdf(file_path)

# -------------------- PROJECT EXTRACTOR --------------------
elif page == "💼 Project Extractor":
    st.title("💼 Project Extractor (Offline)")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        show_pdf(file_path)

        if st.button("📂 Extract Projects/Experience"):
            full_text = extract_text_from_pdf(file_path)
            projects = extract_projects(full_text)
            if projects:
                st.success(f"✅ Found {len(projects)} entries:")
                for p in projects:
                    st.markdown(f"🔹 **{p}**")
            else:
                st.warning("No projects or experience sections detected.")
