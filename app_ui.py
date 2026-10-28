"""Web interface for RADIX Talent Match (Streamlit).

Run:  streamlit run app_ui.py
"""
import json
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.talent_check import list_companies
from pipeline import run_pipeline
from shared.taxonomy import CATEGORY_CODES

SKILLSETS = "data/talent_check_company_skillsets.json"

st.set_page_config(page_title="RADIX Talent Match", layout="wide")
st.title("RADIX Talent Match")
st.caption("Check how ready a candidate is for a specific job and company.")


def save_upload(uploaded):
    folder = Path(tempfile.mkdtemp())
    path = folder / uploaded.name
    path.write_bytes(uploaded.getbuffer())
    return str(path)


def parse_extra_skills(text):
    """Lines like 'Docker, CLOUD' -> [{'name': 'docker', 'category': 'CLOUD'}]."""
    skills, errors = [], []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 2 or parts[1].upper() not in CATEGORY_CODES:
            errors.append(line)
            continue
        skills.append({"name": parts[0].lower(), "category": parts[1].upper()})
    return skills, errors


with st.sidebar:
    st.header("Target")
    company = st.selectbox("Company", list_companies(SKILLSETS))

    st.header("Candidate details (optional)")
    name = st.text_input("Name (leave blank to use resume name)")
    email = st.text_input("Email")
    extra_text = st.text_area(
        "Extra skills, one per line: skill, CATEGORY",
        placeholder="docker, CLOUD\nspringboot, COD",
    )
    preferred = st.text_input("Preferred roles (comma separated)")

col1, col2 = st.columns(2)
with col1:
    jd_file = st.file_uploader("Job description (PDF, DOCX or TXT)",
                               type=["pdf", "docx", "txt"])
with col2:
    resume_file = st.file_uploader("Resume (PDF, DOCX or TXT)",
                                   type=["pdf", "docx", "txt"])

extra_skills, bad_lines = parse_extra_skills(extra_text)
if bad_lines:
    st.warning("Could not read these lines (use 'skill, CATEGORY'): "
               + "; ".join(bad_lines))

if st.button("Run Talent Match", type="primary"):
    if not jd_file or not resume_file:
        st.error("Upload both a job description and a resume.")
    else:
        form = {
            "name": name,
            "email": email,
            "extra_skills": extra_skills,
            "preferred_roles": [r.strip() for r in preferred.split(",") if r.strip()],
        }
        with st.spinner("Analysing..."):
            result = run_pipeline(save_upload(jd_file), save_upload(resume_file),
                                  company, SKILLSETS, form=form)

        tc = result["talent_check"]
        sm = result["skill_matching"]

        m1, m2, m3 = st.columns(3)
        m1.metric("Readiness", f"{tc['readiness_score']}/100")
        m2.metric("Job match", f"{sm['match_score']}/100")
        m3.metric("Categories below target", tc["gap_count"])

        st.subheader(f"Readiness by skill category ({company})")
        gap_df = pd.DataFrame(tc["skillset_gap"]).set_index("category_code")
        st.bar_chart(gap_df[["required_level", "candidate_level"]])
        st.dataframe(gap_df[["required_level", "candidate_level", "gap"]],
                     use_container_width=True)

        left, right = st.columns(2)
        with left:
            st.subheader("Missing for this job")
            if sm["missing_skills"]:
                st.dataframe(pd.DataFrame(sm["missing_skills"]),
                             use_container_width=True, hide_index=True)
            else:
                st.success("No missing skills for this job.")
        with right:
            st.subheader("Matched for this job")
            if sm["matched_skills"]:
                st.dataframe(pd.DataFrame(sm["matched_skills"]),
                             use_container_width=True, hide_index=True)
            else:
                st.info("No matched skills.")

        with st.expander("Candidate skills found in resume"):
            st.dataframe(pd.DataFrame(result["profile"]["skills"]),
                         use_container_width=True, hide_index=True)

        st.download_button("Download full report (JSON)",
                           data=json.dumps(result, indent=2),
                           file_name="radix_report.json",
                           mime="application/json")
