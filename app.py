"""
Smart Resume Screening and Candidate Ranking Tool
--------------------------------------------------
MVP dashboard (Stages 1-11 of the roadmap):

PDF/DOCX upload -> text extraction -> Job Description input ->
TF-IDF similarity -> skill matching -> experience matching ->
weighted score -> ranking -> Streamlit dashboard.

Run with:
    streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.text_extract import extract_text
from utils.info_extractor import extract_candidate_info
from utils.jd_extractor import extract_jd_requirements
from utils.matcher import rank_candidates

st.set_page_config(
    page_title="Smart Resume Screening Tool",
    page_icon="🧑‍💼",
    layout="wide",
)


SAMPLE_DIR = Path(__file__).parent / "sample_data"


class LocalFile:
    """Tiny stand-in for an uploaded file so bundled samples use the same code path."""

    def __init__(self, path: Path):
        self.name = path.name
        self._path = path

    def read(self) -> bytes:
        return self._path.read_bytes()


def load_sample_jd() -> str:
    return (SAMPLE_DIR / "sample_jd.txt").read_text(encoding="utf-8")


def load_sample_resumes() -> list:
    return [LocalFile(p) for p in sorted(SAMPLE_DIR.glob("*.docx"))]


def init_session_state():
    if "candidates" not in st.session_state:
        st.session_state.candidates = []
    if "jd_requirements" not in st.session_state:
        st.session_state.jd_requirements = None
    if "errors" not in st.session_state:
        st.session_state.errors = []


def sidebar_inputs():
    st.sidebar.header("1. Job Description")
    jd_text = st.sidebar.text_area(
        "Paste the Job Description here",
        height=220,
        placeholder="e.g. We are looking for a Python backend developer with "
        "5+ years of experience in Django, REST APIs, and PostgreSQL...",
    )

    st.sidebar.header("2. Candidate Resumes")
    uploaded_files = st.sidebar.file_uploader(
        "Upload PDF or DOCX resumes (multiple allowed)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
    )

    use_sample = st.sidebar.checkbox(
        "Use sample data (demo)",
        help="Adds a sample Job Description and 3 sample resumes so you can "
        "try the tool instantly.",
    )

    run_button = st.sidebar.button("Run Screening & Rank Candidates", type="primary")

    return jd_text, uploaded_files, run_button, use_sample


def process_candidates(uploaded_files):
    candidates = []
    errors = []
    for uploaded_file in uploaded_files:
        try:
            file_bytes = uploaded_file.read()
            text = extract_text(uploaded_file.name, file_bytes)
            if not text.strip():
                errors.append(f"{uploaded_file.name}: no extractable text found.")
                continue
            info = extract_candidate_info(text)
            info["source_file"] = uploaded_file.name
            candidates.append(info)
        except Exception as exc:
            errors.append(f"{uploaded_file.name}: {exc}")
    return candidates, errors


def render_summary_table(ranked_candidates):
    rows = []
    for rank, c in enumerate(ranked_candidates, start=1):
        rows.append({
            "Rank": rank,
            "Name": c["name"],
            "File": c["source_file"],
            "Final Score (%)": c["final_score"],
            "JD Similarity (%)": c["jd_similarity_pct"],
            "Skill Match (%)": c["skill_match_pct"],
            "Experience Match (%)": c["experience_match_pct"],
            "Experience (yrs)": c["experience_years"],
            "Email": c["email"],
            "Phone": c["phone"],
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)
    return df


def render_score_chart(ranked_candidates):
    df = pd.DataFrame([
        {"Candidate": c["name"], "Final Score": c["final_score"]}
        for c in ranked_candidates
    ])
    fig = px.bar(
        df, x="Candidate", y="Final Score",
        title="Candidate Ranking - Final Score (%)",
        text="Final Score",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, width="stretch")


def render_breakdown_chart(ranked_candidates):
    rows = []
    for c in ranked_candidates:
        rows.append({"Candidate": c["name"], "Component": "JD Similarity", "Score": c["jd_similarity_pct"]})
        rows.append({"Candidate": c["name"], "Component": "Skill Match", "Score": c["skill_match_pct"]})
        rows.append({"Candidate": c["name"], "Component": "Experience Match", "Score": c["experience_match_pct"]})
    df = pd.DataFrame(rows)
    fig = px.bar(
        df, x="Candidate", y="Score", color="Component",
        barmode="group", title="Score Breakdown by Component",
    )
    st.plotly_chart(fig, width="stretch")


def render_candidate_details(ranked_candidates):
    st.subheader("Candidate Details")
    for rank, c in enumerate(ranked_candidates, start=1):
        with st.expander(f"#{rank} - {c['name']} ({c['final_score']}%)"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Email:** {c['email'] or 'Not found'}")
                st.markdown(f"**Phone:** {c['phone'] or 'Not found'}")
                st.markdown(f"**Experience:** {c['experience_years']} years")
                if c["education"]:
                    st.markdown("**Education:**")
                    for line in c["education"]:
                        st.markdown(f"- {line}")
            with col2:
                st.markdown(f"**Matched Skills ({len(c['matched_skills'])}):**")
                st.write(", ".join(c["matched_skills"]) or "None")
                st.markdown(f"**Missing Skills ({len(c['missing_skills'])}):**")
                st.write(", ".join(c["missing_skills"]) or "None")


def render_export_buttons(df: pd.DataFrame):
    st.subheader("Export Results")
    col1, col2 = st.columns(2)
    with col1:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download as CSV", data=csv_data,
            file_name="candidate_ranking.csv", mime="text/csv",
        )
    with col2:
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Ranking")
        st.download_button(
            "Download as Excel", data=buffer.getvalue(),
            file_name="candidate_ranking.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def main():
    init_session_state()
    st.title("🧑‍💼 Smart Resume Screening and Candidate Ranking Tool")
    st.caption(
        "Upload a Job Description and candidate resumes to automatically "
        "extract, score, and rank candidates."
    )

    jd_text, uploaded_files, run_button, use_sample = sidebar_inputs()

    if run_button:
        if use_sample:
            jd_text = (jd_text or "").strip() or load_sample_jd()
            uploaded_files = list(uploaded_files or []) + load_sample_resumes()

        if not jd_text or not jd_text.strip():
            st.error("Please paste a Job Description before running the screening.")
            return
        if not uploaded_files:
            st.error("Please upload at least one resume (PDF or DOCX).")
            return

        with st.spinner("Extracting text and scoring candidates..."):
            candidates, errors = process_candidates(uploaded_files)
            jd_requirements = extract_jd_requirements(jd_text)
            ranked = rank_candidates(jd_requirements, candidates)

            st.session_state.candidates = ranked
            st.session_state.jd_requirements = jd_requirements
            st.session_state.errors = errors

    if st.session_state.jd_requirements:
        jd_req = st.session_state.jd_requirements
        with st.expander("Parsed Job Requirements", expanded=False):
            st.markdown(f"**Required skills detected:** {', '.join(jd_req['required_skills']) or 'None detected'}")
            st.markdown(f"**Required experience:** {jd_req['required_experience_years']} years")

    if st.session_state.get("errors"):
        for err in st.session_state.errors:
            st.warning(err)

    if st.session_state.candidates:
        ranked = st.session_state.candidates
        st.success(f"Ranked {len(ranked)} candidate(s).")

        df = render_summary_table(ranked)
        render_score_chart(ranked)
        render_breakdown_chart(ranked)
        render_candidate_details(ranked)
        render_export_buttons(df)
    else:
        st.info("Paste a Job Description, upload resumes, and click **Run Screening & Rank Candidates** to begin.")


if __name__ == "__main__":
    main()
