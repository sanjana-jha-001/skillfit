"""ROLE 4 - Talent Check (owner: Member 4).

Input : saved profile (Role 3) + company name + company skillset snapshot
Output: {"company", "skillset_gap": [...], "readiness_score": 0-100, "gap_count"}

DESIGN DECISION (document this in your report):
  candidate_level per category = min(10, 2 * sum of confidence weights),
  where high=3, medium=2, low=1. So one high-confidence skill = 6, two = 10.
  readiness_score = mean over required categories of min(candidate/required, 1) * 100.
  Each gap row also lists the evidence skills, so the result can be explained.
"""
from shared.io import load_json
from shared.taxonomy import CONFIDENCE_RANK


def list_companies(skillsets_path):
    return [c["company"] for c in load_json(skillsets_path)["companies"]]


def load_company_requirements(skillsets_path, company):
    data = load_json(skillsets_path)
    for entry in data["companies"]:
        if entry["company"].lower() == company.lower():
            return entry["requirements"]
    raise ValueError(f"Company '{company}' not found in {skillsets_path}")


def check_readiness(profile, company, skillsets_path):
    requirements = load_company_requirements(skillsets_path, company)

    totals, names = {}, {}
    for s in profile.get("skills", []):
        code = s["category_code"]
        totals[code] = totals.get(code, 0) + CONFIDENCE_RANK[s["confidence"]]
        names.setdefault(code, []).append(s["skill_name"])

    gaps, ratios = [], []
    for code, required in requirements.items():
        candidate = min(10, 2 * totals.get(code, 0))
        gaps.append({
            "category_code": code,
            "required_level": required,
            "candidate_level": candidate,
            "gap": candidate < required,
            "evidence": sorted(names.get(code, [])),
        })
        ratios.append(min(candidate / required, 1.0) if required else 1.0)

    score = round(sum(ratios) / len(ratios) * 100) if ratios else 0
    return {
        "company": company,
        "skillset_gap": gaps,
        "readiness_score": score,
        "gap_count": sum(g["gap"] for g in gaps),
    }
