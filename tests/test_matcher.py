import pytest

from utils.matcher import (
    compute_experience_match,
    compute_final_score,
    compute_jd_similarity,
    compute_skill_match,
    rank_candidates,
)


def test_skill_match_partial():
    ratio, matched, missing = compute_skill_match(
        ["python", "django", "docker", "aws"], ["Python", "Docker"]
    )
    assert ratio == pytest.approx(0.5)
    assert matched == ["docker", "python"]
    assert missing == ["aws", "django"]


def test_skill_match_neutral_when_jd_has_no_skills():
    assert compute_skill_match([], ["python"]) == (1.0, [], [])


def test_experience_match_cases():
    assert compute_experience_match(0, 0) == 1.0
    assert compute_experience_match(5, 7) == 1.0
    assert compute_experience_match(5, 3) == pytest.approx(0.6)
    assert compute_experience_match(5, 0) == 0.0


def test_final_score_weights():
    assert compute_final_score(1, 1, 1) == 100.0
    assert compute_final_score(0, 0, 0) == 0.0
    # 0.5*1 + 0.3*0 + 0.2*0 = 50%
    assert compute_final_score(1, 0, 0) == 50.0


def test_jd_similarity_prefers_relevant_resume():
    jd = "python django postgresql backend developer"
    relevant = "backend developer skilled in python django and postgresql"
    irrelevant = "graphic designer expert in photoshop and illustration"
    sims = compute_jd_similarity(jd, [relevant, irrelevant])
    assert sims[0] > sims[1]
    assert compute_jd_similarity(jd, []) == []


def test_rank_candidates_orders_best_first():
    jd_req = {
        "raw_text": "python django developer with 3 years experience",
        "required_skills": ["python", "django"],
        "required_experience_years": 3.0,
    }
    strong = {"name": "Strong", "skills": ["python", "django"], "experience_years": 5.0,
              "raw_text": "python django developer with 5 years experience"}
    weak = {"name": "Weak", "skills": [], "experience_years": 0.0,
            "raw_text": "marketing manager with social media campaigns"}
    ranked = rank_candidates(jd_req, [weak, strong])
    assert [c["name"] for c in ranked] == ["Strong", "Weak"]
    assert ranked[0]["final_score"] > ranked[1]["final_score"]
    assert ranked[1]["missing_skills"] == ["django", "python"]


def test_rank_candidates_empty():
    assert rank_candidates({"raw_text": "", "required_skills": [],
                            "required_experience_years": 0}, []) == []
