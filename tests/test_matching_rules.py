from modules.skill_matching import match_skills
from shared.taxonomy import canonical_name, extract_keywords, merge_skills


def names(skills):
    return {s["skill_name"] for s in skills}


def test_aliases_map_to_canonical_names():
    assert canonical_name("Postgres") == "postgresql"
    assert canonical_name("ML") == "machine learning"
    assert canonical_name("Google Cloud") == "gcp"


def test_extraction_uses_whole_words_only():
    found = names(extract_keywords("I write JavaScript daily."))
    assert "javascript" in found
    assert "java" not in found


def test_postgres_alias_also_credits_sql():
    found = names(extract_keywords("Built services on Postgres."))
    assert {"postgresql", "sql"} <= found


def test_javascript_does_not_match_java():
    jd = {"source_file": "jd.txt", "skills": [
        {"skill_name": "java", "category_code": "COD"}]}
    result = match_skills([{"skill_name": "javascript", "category_code": "COD"}], jd)
    assert result["match_score"] == 0


def test_alias_matches_in_skill_matching():
    jd = {"source_file": "jd.txt", "skills": [
        {"skill_name": "postgresql", "category_code": "SQL"}]}
    result = match_skills([{"skill_name": "Postgres", "category_code": "SQL"}], jd)
    assert result["match_score"] == 100


def test_merge_keeps_highest_confidence():
    low = [{"skill_name": "git", "category_code": "SWE", "evidence": "", "confidence": "low"}]
    high = [{"skill_name": "git", "category_code": "SWE", "evidence": "", "confidence": "high"}]
    merged = merge_skills(low, high)
    assert len(merged) == 1 and merged[0]["confidence"] == "high"
