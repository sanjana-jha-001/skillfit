"""ROLE 3 - Profile Builder (owner: Member 3).

Input : parsed resume (from Role 2) + optional form entries from the user
Output: candidate profile in the shared format, saved as JSON.
Everyone downstream depends on this, so keep the save/load path simple.
"""
import re

from shared.io import load_json, save_json
from shared.taxonomy import make_skill, merge_skills


def build_profile(resume, form=None):
    form = form or {}
    extra = [make_skill(s["name"], s["category"], "added in form", "high")
             for s in form.get("extra_skills", [])]
    return {
        "name": form.get("name") or resume.get("name", ""),
        "email": form.get("email", ""),
        "education": form.get("education") or resume.get("education", ""),
        "skills": merge_skills(resume.get("skills", []), extra),
        "hackathons": form.get("hackathons", []),
        "internships": form.get("internships", resume.get("experience", [])),
        "certifications": form.get("certifications", resume.get("certifications", [])),
        "preferred_roles": form.get("preferred_roles", []),
        "cv_file": resume.get("source_file", ""),
    }


def _slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "candidate"


def save_profile(profile, folder="data/profiles"):
    return save_json(profile, f"{folder}/{_slug(profile['name'])}.json")


def load_profile(path):
    return load_json(path)
