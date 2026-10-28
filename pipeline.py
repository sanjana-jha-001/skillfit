"""INTEGRATION - connects the five modules into one flow.

Pick JD > Parse resume > Build profile > Run Talent Check > Run Skill Matching
"""
from modules.jd_analytics import analyze_jd
from modules.resume_parsing import parse_resume
from modules.profile_builder import build_profile, save_profile
from modules.talent_check import check_readiness
from modules.skill_matching import match_skills


def run_pipeline(jd_path, resume_path, company, skillsets_path,
                 form=None, profile_dir="data/profiles"):
    jd = analyze_jd(jd_path, company=company)                        # Role 1
    resume = parse_resume(resume_path)                               # Role 2
    profile = build_profile(resume, form)                            # Role 3
    save_profile(profile, profile_dir)
    talent = check_readiness(profile, company, skillsets_path)       # Role 4
    match = match_skills(profile["skills"], jd)                      # Role 5
    return {
        "jd": jd,
        "resume": resume,
        "profile": profile,
        "talent_check": talent,
        "skill_matching": match,
    }
