"""ROLE 5 - Skill Matching (owner: Member 5).

Input : candidate skills (from profile) + one JD result (from Role 1)
Output: {"jd_source_file", "match_score", "matched_skills", "missing_skills"}

Matching rules:
  1. Names are converted to canonical form first (aliases like "postgres" -> "postgresql").
  2. Exact canonical match counts.
  3. Typos are allowed only for names of 4+ characters (similarity >= 0.88).
  4. Substrings are NOT matched, so "java" does not match "javascript".
"""
from difflib import SequenceMatcher

from shared.taxonomy import canonical_name


def _same_skill(a, b):
    a, b = canonical_name(a), canonical_name(b)
    if a == b:
        return True
    if min(len(a), len(b)) >= 4:
        return SequenceMatcher(None, a, b).ratio() >= 0.88
    return False


def match_skills(candidate_skills, jd_result):
    matched, missing = [], []
    for req in jd_result["skills"]:
        hit = next((c for c in candidate_skills
                    if _same_skill(req["skill_name"], c["skill_name"])), None)
        row = {"skill_name": req["skill_name"], "category_code": req["category_code"]}
        if hit:
            matched.append({**row, "matched_to": hit["skill_name"]})
        else:
            missing.append(row)

    total = len(jd_result["skills"])
    score = round(len(matched) / total * 100) if total else 0
    return {
        "jd_source_file": jd_result["source_file"],
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
    }
