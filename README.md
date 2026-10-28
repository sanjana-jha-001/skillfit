# RADIX Talent Match

Checks how ready a candidate is for a specific job and company. Built from five role
modules connected by one pipeline, with a web interface and a command-line interface.

## Ownership

| Role | File | Owner |
|---|---|---|
| 1. JD Analytics | `modules/jd_analytics.py` | Member 1 |
| 2. Resume Parsing | `modules/resume_parsing.py` | Member 2 |
| 3. Profile Builder | `modules/profile_builder.py` | Member 3 |
| 4. Talent Check | `modules/talent_check.py` | Member 4 |
| 5. Skill Matching | `modules/skill_matching.py` | Member 5 |
| Scrum Master | `pipeline.py`, `app.py`, `app_ui.py`, `tests/` | Scrum Master |
| Shared contract | `shared/taxonomy.py`, `shared/io.py` | Whole team |

## Install

```bash
pip install -r requirements.txt
```

## Run the web app (recommended for the demo)

```bash
streamlit run app_ui.py
```

Opens in the browser. Upload a JD and a resume, pick a company, and click
**Run Talent Match**.

## Run the command line

```bash
python app.py --jd data/samples/jd_sample.txt --resume data/samples/resume_sample.txt --company "Google LLC"
```

## Run the tests

```bash
pytest
```

## Sample data

`data/samples/` holds sample JDs and resumes written for testing. The hackathon's official
files are not included; add them to this folder and use them in the app.

## Matching rules (summary)

- Aliases are converted to canonical names (for example `postgres` -> `postgresql`, `ML` -> `machine learning`).
- Whole words only, so `java` does not match `javascript`.
- Some skills imply related skills (for example `postgresql` also counts as `sql`).
- Typos are allowed for names of 4+ characters only.

## Limitations

- Extraction is dictionary-based, not LLM-based. The dictionary can be extended in `shared/taxonomy.py`.
- Company skill levels in `data/talent_check_company_skillsets.json` are sample values until the facilitator's file is used.
