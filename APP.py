# -------------------------------
# TESTING & VALIDATION MODULE
# -------------------------------
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_fscore_support
from scipy.stats import spearmanr
import streamlit as st

st.markdown("---")
st.header("🧪 Testing & Validation")

st.write("""
This panel runs basic validation tests on the resume scanner:
- Skill extraction: precision / recall / F1 against labeled skills (synthetic examples here).  
- Matching model: Spearman rank correlation between predicted match % and ground-truth relevance scores.  
You can replace synthetic examples with your labeled dataset (CSV) for real evaluation.
""")

# ----- Example / Synthetic Test Data -----
st.subheader("1) Run synthetic tests (quick demo)")
if st.button("Run Demo Validation"):

    # Example JD (ground truth requirements)
    demo_jd = """Looking for Data Analyst with expertise in Python, SQL, Power BI, data visualization, pandas and numpy. Excellent communication skills required."""
    # Synthetic candidate resumes (text) and labeled skills (what we expect to extract)
    synthetic_resumes = [
        {
            "name": "alice_resume.txt",
            "text": "Experienced Data Analyst skilled in Python, pandas, numpy, created dashboards using Power BI and Tableau. Strong communication.",
            "labeled_skills": ["Python", "Pandas", "Numpy", "Power BI", "Tableau", "Communication"],
            # ground-truth relevance from 0-100 (how good a fit)
            "gt_relevance": 92
        },
        {
            "name": "bob_resume.txt",
            "text": "SQL developer with strong SQL knowledge, ETL pipelines, some experience in Excel and dashboards.",
            "labeled_skills": ["SQL", "Excel"],
            "gt_relevance": 65
        },
        {
            "name": "carol_resume.txt",
            "text": "Machine learning intern; worked with TensorFlow and Keras, research on deep learning. Limited dashboard experience.",
            "labeled_skills": ["TensorFlow", "Keras", "Deep Learning"],
            "gt_relevance": 55
        },
        {
            "name": "dave_resume.txt",
            "text": "Business analyst: Power BI dashboards, business reporting, stakeholder communication and SQL basics.",
            "labeled_skills": ["Power BI", "Communication", "SQL"],
            "gt_relevance": 78
        }
    ]

    # Run extraction + similarity for each synthetic resume
    rows = []
    pred_scores = []
    gt_scores = []
    all_gt_skills = []
    all_pred_skills = []

    for item in synthetic_resumes:
        text = item["text"].lower()
        pred_skills = extract_skills(text)  # uses your app function
        match_pct = calculate_similarity(demo_jd.lower(), text)  # uses your app function

        rows.append({
            "Resume": item["name"],
            "Pred Skills": ", ".join(pred_skills) if pred_skills else "None",
            "GT Skills": ", ".join(item["labeled_skills"]),
            "Pred Match %": match_pct,
            "GT Relevance": item["gt_relevance"]
        })

        # For skill evaluation, map both to lowercase sets
        gt_set = set([s.lower() for s in item["labeled_skills"]])
        pred_set = set([s.lower() for s in pred_skills])
        all_gt_skills.append(gt_set)
        all_pred_skills.append(pred_set)

        pred_scores.append(match_pct)
        gt_scores.append(item["gt_relevance"])

    result_df = pd.DataFrame(rows)
    st.subheader("Demo Results Table")
    st.dataframe(result_df, use_container_width=True)

    # ----- Skill Extraction Metrics (micro-averaged) -----
    # We compute precision/recall/F1 by treating all skills across resumes as independent tokens
    # Build global lists for each occurrence
    y_true = []
    y_pred = []
    # collect union of skill tokens observed in GT across resumes
    skill_vocab = sorted(list(set().union(*all_gt_skills, *all_pred_skills)))
    # For each resume, for each skill in vocab, mark 1/0 presence
    for gt, pred in zip(all_gt_skills, all_pred_skills):
        for skill in skill_vocab:
            y_true.append(1 if skill in gt else 0)
            y_pred.append(1 if skill in pred else 0)

    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='micro', zero_division=0)
    st.subheader("Skill Extraction Metrics (micro-averaged)")
    st.write(f"- Precision: **{precision:.2f}**")
    st.write(f"- Recall: **{recall:.2f}**")
    st.write(f"- F1-score: **{f1:.2f}**")

    # ----- Matching Model Metric: Spearman Rank Correlation -----
    # Compare predicted match % ranking vs ground-truth relevance ranking
    if len(pred_scores) >= 2:
        spearman_corr, spearman_p = spearmanr(pred_scores, gt_scores)
        st.subheader("Matching Model Correlation")
        st.write(f"- Spearman correlation: **{spearman_corr:.3f}** (p = {spearman_p:.3f})")
        st.write("- Interpretation: a value close to 1 indicates predicted match % preserves the ground-truth ranking well.")
    else:
        st.info("Not enough samples for Spearman correlation.")

    # ----- Plots -----
    st.subheader("Visuals")
    fig, ax = plt.subplots()
    names = result_df["Resume"].tolist()
    pred_vals = result_df["Pred Match %"].tolist()
    gt_vals = result_df["GT Relevance"].tolist()
    x = np.arange(len(names))
    width = 0.35
    ax.bar(x - width/2, pred_vals, width, label='Predicted Match %')
    ax.bar(x + width/2, gt_vals, width, label='GT Relevance')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=30)
    ax.set_ylabel("Score")
    ax.set_title("Predicted Match % vs Ground Truth Relevance")
    ax.legend()
    st.pyplot(fig)

    # Skill frequency chart (predicted)
    st.subheader("Skill Frequency (Predicted across resumes)")
    # flatten predicted skills
    flat_pred = [s for sset in all_pred_skills for s in sset]
    if flat_pred:
        freq = pd.Series(list(flat_pred)).value_counts()
        fig2, ax2 = plt.subplots()
        ax2.bar(freq.index.astype(str), freq.values)
        ax2.set_title("Predicted Skill Frequency")
        ax2.set_ylabel("Count")
        ax2.set_xticklabels(freq.index.astype(str), rotation=45, ha='right')
        st.pyplot(fig2)
    else:
        st.write("No predicted skills to show frequency for.")

    # ----- Downloadable CSV report -----
    csv_bytes = result_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Demo Validation CSV", data=csv_bytes, file_name="nuvora_demo_validation.csv", mime="text/csv")

# ----- Upload labeled dataset for real validation -----
st.subheader("2) Upload labeled CSV for evaluation (optional)")
st.write("CSV should have columns: `resume_name`, `resume_text`, `gt_skills` (comma-separated), `gt_relevance` (0-100).")
uploaded_csv = st.file_uploader("Upload labeled CSV (optional)", type=["csv"])

if uploaded_csv is not None:
    labeled_df = pd.read_csv(uploaded_csv)
    st.write("Preview of uploaded labeled data:")
    st.dataframe(labeled_df.head(), use_container_width=True)

    if st.button("Run Validation on Uploaded Data"):
        required_cols = {"resume_name", "resume_text", "gt_skills", "gt_relevance"}
        if not required_cols.issubset(set(labeled_df.columns.str.lower())):
            st.error(f"CSV must contain columns: {required_cols}")
        else:
            # Normalize column names to lower for safety
            labeled_df.columns = [c.lower() for c in labeled_df.columns]

            rows = []
            pred_scores = []
            gt_scores = []
            all_gt_skills = []
            all_pred_skills = []

            for _, r in labeled_df.iterrows():
                name = r['resume_name']
                text = str(r['resume_text']).lower()
                gt_skills = [s.strip().lower() for s in str(r['gt_skills']).split(",") if s.strip()]
                gt_relevance = float(r['gt_relevance'])

                pred_skills = extract_skills(text)
                pred_match = calculate_similarity(str(job_description).lower() if job_description else text, text)

                rows.append({
                    "Resume": name,
                    "Pred Skills": ", ".join(pred_skills) if pred_skills else "None",
                    "GT Skills": ", ".join(gt_skills),
                    "Pred Match %": pred_match,
                    "GT Relevance": gt_relevance
                })

                all_gt_skills.append(set(gt_skills))
                all_pred_skills.append(set([s.lower() for s in pred_skills]))
                pred_scores.append(pred_match)
                gt_scores.append(gt_relevance)

            out_df = pd.DataFrame(rows)
            st.subheader("Validation Results")
            st.dataframe(out_df, use_container_width=True)

            # Skill metrics
            skill_vocab = sorted(list(set().union(*all_gt_skills, *all_pred_skills)))
            y_true = []
            y_pred = []
            for gt, pred in zip(all_gt_skills, all_pred_skills):
                for skill in skill_vocab:
                    y_true.append(1 if skill in gt else 0)
                    y_pred.append(1 if skill in pred else 0)

            precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='micro', zero_division=0)
            st.write("**Skill Extraction Metrics (micro)**")
            st.write(f"- Precision: **{precision:.3f}**")
            st.write(f"- Recall: **{recall:.3f}**")
            st.write(f"- F1: **{f1:.3f}**")

            # Spearman correlation
            if len(pred_scores) >= 2:
                spearman_corr, spearman_p = spearmanr(pred_scores, gt_scores)
                st.write("**Matching Model Correlation**")
                st.write(f"- Spearman correlation: **{spearman_corr:.3f}** (p={spearman_p:.3f})")
            else:
                st.info("Not enough samples for correlation.")

            # Download report
            csv_bytes = out_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Validation Report CSV", data=csv_bytes, file_name="nuvora_validation_report.csv", mime="text/csv")
