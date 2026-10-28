"""ROLE 1 - JD Analytics (owner: Member 1).

Input : a job description (PDF / DOCX / TXT)
Output: {"source_type": "jd", "source_file", "company", "role", "skills": [...]}
Skills under 'Key Responsibilities' / 'What We're Looking For' get high confidence.
"""
import re
from pathlib import Path

from shared.io import read_document
from shared.taxonomy import extract_keywords, merge_skills

PRIORITY_HEADINGS = ("key responsibilities", "what we're looking for",
                     "what we are looking for", "requirements", "qualifications")
STOP_HEADINGS = re.compile(r"^(about|benefits|location|compensation|equal opportunity)")


def _priority_sections(text):
    """Return only the text under the priority headings; fall back to full text."""
    chunks, capture = [], False
    for line in text.splitlines():
        low = line.strip().lower().rstrip(":")
        if any(low.startswith(h) for h in PRIORITY_HEADINGS):
            capture = True
            continue
        if capture and STOP_HEADINGS.match(low):
            capture = False
        if capture:
            chunks.append(line)
    return "\n".join(chunks) or text


def analyze_jd(path, company="Unknown", role=None):
    text = read_document(path)
    high = extract_keywords(_priority_sections(text), confidence="high")
    low = extract_keywords(text, confidence="low")
    skills = merge_skills(high, low)

    if role is None:
        first = next((l.strip() for l in text.splitlines() if l.strip()), "")
        role = first[:80] or "Unknown"

    return {
        "source_type": "jd",
        "source_file": Path(path).name,
        "company": company,
        "role": role,
        "skills": skills,
    }
