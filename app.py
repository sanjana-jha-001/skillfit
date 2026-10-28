"""Command-line entry point for the integrated RADIX Talent Match tool.

Example:
  python app.py --jd data/samples/jd_sample.txt \
                --resume data/samples/resume_sample.txt \
                --company "Google LLC"
"""
import argparse

from pipeline import run_pipeline
from shared.io import save_json


def main():
    p = argparse.ArgumentParser(description="RADIX Talent Match")
    p.add_argument("--jd", required=True, help="job description file")
    p.add_argument("--resume", required=True, help="resume file")
    p.add_argument("--company", required=True, help="company name from the snapshot")
    p.add_argument("--skillsets", default="data/talent_check_company_skillsets.json")
    p.add_argument("--out", default="outputs/report.json")
    args = p.parse_args()

    result = run_pipeline(args.jd, args.resume, args.company, args.skillsets)
    save_json(result, args.out)

    tc = result["talent_check"]
    sm = result["skill_matching"]
    print(f"Candidate : {result['profile']['name']}")
    print(f"Company   : {args.company}")
    print(f"Readiness : {tc['readiness_score']}/100")
    print(f"JD match  : {sm['match_score']}/100")
    print(f"Missing   : {', '.join(s['skill_name'] for s in sm['missing_skills']) or 'none'}")
    print(f"Report    : {args.out}")


if __name__ == "__main__":
    main()
