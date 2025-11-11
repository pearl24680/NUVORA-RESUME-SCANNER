import os
import base64
import json
import gc
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF
import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Optional: AI integration
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GENAI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        AI_ENABLED = True
    else:
        AI_ENABLED = False
except ImportError:
    AI_ENABLED = False

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="Nuvora AI Job Assistant", layout="wide")

# -------------------- WHITE THEME & STYLING --------------------
st.markdown("""
<style>
body { background-color: #ffffff; color: #222; }
div[data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
.card { background-color: #f7f9fc; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; }
.skill-badge { background-color: #4A90E2; color: white; padding: 4px 8px; border-radius: 5px; margin:2px; display:inline-block; }
.missing-badge { background-color: #F39C12; color: white; padding: 4px 8px; border-radius: 5px; margin:2px; display:inline-block; }
.suggestion-badge { background-color: #2ECC71; color: white; padding: 4px 8px; border-radius: 5px; margin:2px; display:inline-block; }
</style>
""", unsafe_allow_html=True)

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
    if not AI_ENABLED:
        return {}  # AI features disabled
    import google.generativeai as genai
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
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------
def show_dashboard():
    st.header("📊 AI Career Dashboard")
    if not AI_ENABLED:
        st.warning("⚠️ AI features are disabled. Set GENAI_API_KEY in your .env to enable resume analysis and career insights.")
        return
    if "extracted_data" in st.session_state and st.session_state.extracted_data:
        data = st.session_state.extracted_data
        overall_score = data.get("overall_score", 0)
        matched = data.get("keyword_matching", [])
        missing = data.get("missing_keywords", [])
        suggestions = data.get("suggestions", [])
        col1, col2, col3 = st.columns([1,2,2])
        with col1:
            st.markdown('<div class="card" style="text-align:center;"><h3>Overall Score</h3></div>', unsafe_allow_html=True)
            fig = px.bar(
                x=[overall_score], y=["Resume Match"],
                orientation="h", text=[f"{overall_score}%"],
                color_discrete_sequence=["#2ECC71" if overall_score>=80 else "#F39C12" if overall_score>=60 else "#E74C3C"]
            )
            fig.update_traces(textposition="inside")
            fig.update_layout(xaxis=dict(range=[0,100]), height=150, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown('<div class="card"><h4>✅ Matched Skills</h4></div>', unsafe_allow_html=True)
            if matched:
                for skill in matched: st.markdown(f'<span class="skill-badge">{skill}</span>', unsafe_allow_html=True)
            else: st.warning("No matched skills!")
        with col3:
            st.markdown('<div class="card"><h4>⚠️ Missing Skills</h4></div>', unsafe_allow_html=True)
            if missing:
                for skill in missing: st.markdown(f'<span class="missing-badge">{skill}</span>', unsafe_allow_html=True)
            else: st.success("No missing skills!")
        if suggestions:
            st.markdown('<div class="card"><h4>💡 Suggestions</h4></div>', unsafe_allow_html=True)
            for s in suggestions: st.markdown(f'<span class="suggestion-badge">{s}</span>', unsafe_allow_html=True)
    else:
        st.info("Upload resume and paste a job description below to see the dashboard.")

# -------------------- SIDEBAR NAVIGATION --------------------
st.sidebar.title("📘 Nuvora AI Job Assistant")
page = st.sidebar.radio("Navigate", ["🏠 Home", "💼 Project Extractor", "🤖 Career Chatbot"])

# -------------------- MAIN HOME PAGE --------------------
if page=="🏠 Home":
    show_dashboard()
    st.markdown("---")
    st.subheader("📋 Job Description")
    job_description = st.text_area("Paste the job description here", height=200)
    st.subheader("📄 Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Upload your Resume", type=["pdf"])
    if uploaded_file and job_description.strip():
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        if st.button("🔍 Analyze Resume"):
            if not AI_ENABLED:
                st.warning("⚠️ AI is disabled. Set GENAI_API_KEY to enable analysis.")
            else:
                with st.spinner("Analyzing resume..."):
                    images = pdf_to_jpg(file_path)
                    extracted_texts = []
                    for img_path in images:
                        result = process_image(img_path, "Extract text from resume", type="image")
                        extracted_texts.append(result)
                    prompt = f"""
                    Analyze resume text vs job description: {job_description}
                    Resume Text: {extracted_texts}
                    Return JSON: overall_score, keyword_matching, missing_keywords, suggestions
                    """
                    final_result = process_image(file_path=extracted_texts, prompt=prompt, type="text")
                    st.session_state.extracted_data = final_result
                    show_dashboard()

# -------------------- PROJECT EXTRACTOR --------------------
elif page=="💼 Project Extractor":
    st.title("💼 Resume Project Extractor")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        show_pdf(file_path)
        if st.button("📂 Extract Projects"):
            images = pdf_to_jpg(file_path)
            full_text = ""
            for img_path in images:
                result = process_image(img_path, "Extract plain text", "image") if AI_ENABLED else ""
                full_text += str(result)
            projects = extract_projects(full_text)
            if projects:
                st.success(f"✅ Found {len(projects)} projects:")
                for p in projects: st.markdown(f"🔹 **{p}**")
            else:
                st.warning("No clear projects found.")

# -------------------- CAREER CHATBOT --------------------
elif page=="🤖 Career Chatbot":
    st.title("🤖 AI Career Chat Assistant")
    if not AI_ENABLED:
        st.warning("⚠️ AI Chatbot disabled. Set GENAI_API_KEY to enable AI responses.")
    else:
        if "chat_history" not in st.session_state: st.session_state.chat_history=[]
        user_input = st.text_input("You:", key="user_input")
        if user_input:
            with st.spinner("AI thinking..."):
                model = genai.GenerativeModel("gemini-1.5-flash-002")
                history = "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in st.session_state.chat_history])
                prompt = f"You are a career coach AI.\nHistory:\n{history}\nUser query: {user_input}"
                response = model.generate_content(prompt)
                reply = response.candidates[0].content.parts[0].text if hasattr(response,"candidates") else "Sorry, I couldn’t process that."
                st.session_state.chat_history.append({"user": user_input, "bot": reply})
        for chat in st.session_state.chat_history[::-1]:
            st.markdown(f"👩‍💼 You: {chat['user']}")
            st.markdown(f"🤖 {chat['bot']}")
