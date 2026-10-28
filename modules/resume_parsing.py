"""ROLE 2 - Resume Parsing (owner: Member 2).

Input : a resume (PDF / DOCX / TXT)
Output: {"source_type": "resume", "source_file", "name", "education", "skills",
         "projects", "experience", "certifications"}
Tolerant of layout variation: sections are detected by heading words, and
skills are also searched in the rest of the text at low confidence.
"""
from pathlib import Path

from shared.io import read_document
from shared.taxonomy import extract_keywords, merge_skills

SECTION_HEADINGS = {"education", "experience", "projects", "skills",
                    "certifications", "hackathons", "internships"}


def _split_sections(text):
    sections, current = {}, "header"
    for line in text.splitlines():
        key = line.strip().lower().rstrip(":")
        if key in SECTION_HEADINGS:
            current = key
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def _lines(block):
    return [l.strip().lstrip("-•* ").strip() for l in block.splitlines() if l.strip()]


def parse_resume(path, name=None):
    text = read_document(path)
    sec = _split_sections(text)

    core_text = "\n".join(sec.get(k, "") for k in ("skills", "projects", "experience"))
    high = extract_keywords(core_text, confidence="high")
    low = extract_keywords(text, confidence="low")

    if name is None:
        name = next((l.strip() for l in text.splitlines() if l.strip()), "Unknown")

    return {
        "source_type": "resume",
        "source_file": Path(path).name,
        "name": name,
        "education": " ".join(_lines(sec.get("education", ""))),
        "skills": merge_skills(high, low),
        "projects": _lines(sec.get("projects", "")),
        "experience": _lines(sec.get("experience", "")),
        "certifications": _lines(sec.get("certifications", "")),
    }
