import os
import base64
import json
import gc
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import re

# -------------------- LOAD ENVIRONMENT --------------------
load_dotenv()
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    st.error("❌ GENAI_API_KEY is missing in .env file.")
else:
    genai.configure(api_key=api_key)

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="Nuvora AI Job Assistant", layout="wide")

# -------------------- WHITE THEME & STYLING --------------------
st.markdown(
    """
    <style>
    body { background-color: #ffffff; color: #222; }
    div[data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
    .user-msg { background: #e8f5e9; border-radius: 8px; padding: 8px 12px; margin: 6px 0; }
    .bot-msg { background: #e3f2fd; border-radius: 8px; padding: 8px 12px; margin: 6px 0; }
    .stButton>button { background-color: #4A90E2; color: white; border-radius: 8px; border: none; padding: 0.6em 1.2em; font-weight: 500; }
    .stButton>button:hover { background-color: #3b7cd1; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- FUNCTIONS --------------------
def pdf_to_jpg(pdf_path, output_folder="pdf_images", dpi=300):
    file_paths = []
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    pdf_document = fitz.open(pdf_path)
    for i in range(len(pdf_document)):
        page = pdf_document[i]
        pix = page.get_pixmap(dpi=dpi)
        out_file = output_folder / f"page_{i+1}.jpg"
        pix.save(str(out_file))
        file_paths.append(str(out_file))
    pdf_document.close()
    return file_paths


def process_image(file_path="", prompt="", type=None):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-002")
        if type == "image":
            with Image.open(file_path) as img:
                response = model.generate_content([prompt, img])
        elif type == "text":
            response = model.generate_content([prompt, json.dumps(file_path, indent=2)])
        else:
            return {}

        if hasattr(response, 'candidates') and response.candidates:
            text = response.candidates[0].content.parts[0].text
            text = text.replace("```", "").replace("json", "")
            try:
                return json.loads(text)
            except:
                return {"response_text": text}
        return {}
    finally:
        gc.collect()


def extract_projects(text):
    pattern = r"(?i)(projects?|internships?|experience)\s*[:\-]?\s*(.+)"
    matches = re.findall(pattern, text)
    projects = [m[1].strip() for m in matches]
    return list(set(projects))


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def show_analytics():
    st.header("📊 AI Career Dashboard")
    if "extracted_data" in st.session_state and st.session_state.extracted_data:
        data = st.session_state.extracted_data
        overall_score = data.get("overall_score", 0)
        st.subheader(f"Overall Match: {overall_score}%")

        # Compact Score Bar
        fig = px.bar(
            x=[overall_score],
            y=["Resume Match"],
            orientation="h",
            text=[f"{overall_score}%"],
            color_discrete_sequence=[
                "#2ECC71" if overall_score >= 80 else "#F39C12" if overall_score >= 60 else "#E74C3C"
            ]
        )
        fig.update_traces(textposition="inside", marker_line_color="black", marker_line_width=1)
        fig.update_layout(
            xaxis=dict(range=[0, 100]),
            yaxis=dict(showticklabels=False),
            height=120,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Matched Skills
        st.subheader("✅ Matched Skills")
        matched = data.get("keyword_matching", [])
        if matched:
            cols = st.columns(5)
            for i, skill in enumerate(matched):
                with cols[i % 5]:
                    st.markdown(f"<span style='background-color:#4A90E2; color:white; padding:4px 8px; border-radius:5px;'>{skill}</span>", unsafe_allow_html=True)
        else:
            st.warning("No matched skills found.")

        # Missing Skills
        st.subheader("⚠️ Missing Skills")
        missing = data.get("missing_keywords", [])
        if missing:
            cols = st.columns(5)
            for i, skill in enumerate(missing):
                with cols[i % 5]:
                    st.markdown(f"<span style='background-color:#F39C12; color:white; padding:4px 8px; border-radius:5px;'>{skill}</span>", unsafe_allow_html=True)
        else:
            st.success("No missing skills!")

        # Suggestions
        st.subheader("💡 Improvement Suggestions")
        suggestions = data.get("suggestions", [])
        if suggestions:
            priority_data = []
            for s in suggestions:
                if "experience" in s.lower():
                    color = "#E74C3C"
                elif "skill" in s.lower():
                    color = "#F39C12"
                else:
                    color = "#2ECC71"
                priority_data.append({"Suggestion": s, "Color": color})

            for item in priority_data:
                st.markdown(f"<div style='background-color:{item['Color']}; padding:5px; border-radius:5px; color:white; margin-bottom:3px;'>{item['Suggestion']}</div>", unsafe_allow_html=True)
        else:
            st.success("No suggestions! Resume looks good ✅")
    else:
        st.info("Upload your resume and paste a job description below to see your AI Career Dashboard.")


# -------------------- SIDEBAR NAVIGATION --------------------
st.sidebar.title("📘 Nuvora AI Job Assistant")
page = st.sidebar.radio("Navigate", ["🏠 Home", "💼 Project Extractor", "🤖 Career Chatbot"])

# -------------------- MAIN HOME PAGE --------------------
if page == "🏠 Home":
    show_analytics()  # Dashboard always on top

    st.markdown("---")

    # Job Description Input
    st.subheader("📋 Job Description")
    job_description = st.text_area("Paste the job description here", height=200)

    # Resume Upload
    st.subheader("📄 Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Upload your Resume", type=["pdf"])

    if uploaded_file and job_description.strip():
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("🔍 Analyze Resume"):
            with st.spinner("Analyzing resume..."):
                # Convert PDF to images
                images = pdf_to_jpg(file_path)
                extracted_texts = []

                # Extract text from images using AI
                for img_path in images:
                    result = process_image(img_path, "Extract text from resume", type="image")
                    extracted_texts.append(result)

                # Combine with JD for analysis
                analysis_prompt = f"""
                Analyze the resume text against this job description:
                Job Description: {job_description}
                Resume Text: {extracted_texts}

                Return JSON with: overall_score, keyword_matching, missing_keywords, suggestions
                """
                final_result = process_image(file_path=extracted_texts, prompt=analysis_prompt, type="text")
                st.session_state.extracted_data = final_result

                # Refresh Dashboard
                show_analytics()

# -------------------- PROJECT EXTRACTOR --------------------
elif page == "💼 Project Extractor":
    st.title("💼 Resume Project Extractor")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        show_pdf(file_path)
        if st.button("📂 Extract Projects"):
            images = pdf_to_jpg(file_path)
            full_text = ""
            for img_path in images:
                result = process_image(img_path, "Extract plain text", "image")
                full_text += str(result)
            projects = extract_projects(full_text)
            if projects:
                st.success(f"✅ Found {len(projects)} projects:")
                for p in projects:
                    st.markdown(f"🔹 **{p}**")
            else:
                st.warning("No clear projects found in the resume.")

# -------------------- CAREER CHATBOT --------------------
elif page == "🤖 Career Chatbot":
    st.title("🤖 AI Career Chat Assistant")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    user_input = st.text_input("You:", key="user_input")
    if user_input:
        with st.spinner("AI thinking..."):
            model = genai.GenerativeModel("gemini-1.5-flash-002")
            history = "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in st.session_state.chat_history])
            prompt = f"You are a career coach AI.\nHistory:\n{history}\nUser query: {user_input}"
            response = model.generate_content(prompt)
            reply = response.candidates[0].content.parts[0].text if hasattr(response, "candidates") else "Sorry, I couldn’t process that."
            st.session_state.chat_history.append({"user": user_input, "bot": reply})

    for chat in st.session_state.chat_history[::-1]:
        st.markdown(f"<div class='user-msg'>👩‍💼 You: {chat['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='bot-msg'>🤖 {chat['bot']}</div>", unsafe_allow_html=True)
