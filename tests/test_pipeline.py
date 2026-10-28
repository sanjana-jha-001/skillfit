from pipeline import run_pipeline

JD = "data/samples/jd_sample.txt"
R1 = "data/samples/resume_sample.txt"
R2 = "data/samples/resume_sample_2.txt"
SKILLSETS = "data/talent_check_company_skillsets.json"


def test_full_flow_returns_all_five_pieces(tmp_path):
    out = run_pipeline(JD, R1, "Google LLC", SKILLSETS, profile_dir=str(tmp_path))
    assert out["jd"]["source_type"] == "jd"
    assert out["resume"]["source_type"] == "resume"
    assert out["profile"]["skills"]
    assert 0 <= out["talent_check"]["readiness_score"] <= 100
    assert 0 <= out["skill_matching"]["match_score"] <= 100


def test_different_candidates_get_different_results(tmp_path):
    a = run_pipeline(JD, R1, "Google LLC", SKILLSETS, profile_dir=str(tmp_path))
    b = run_pipeline(JD, R2, "Google LLC", SKILLSETS, profile_dir=str(tmp_path))
    assert a["talent_check"]["readiness_score"] != b["talent_check"]["readiness_score"]
    assert a["skill_matching"]["match_score"] != b["skill_matching"]["match_score"]


def test_profile_is_saved(tmp_path):
    run_pipeline(JD, R1, "Google LLC", SKILLSETS, profile_dir=str(tmp_path))
    assert any(tmp_path.iterdir())
