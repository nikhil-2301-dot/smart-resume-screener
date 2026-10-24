from utils.jd_extractor import extract_jd_requirements


def test_extracts_skills_and_years():
    jd = "Looking for 3+ years of Python and Django experience with Docker."
    req = extract_jd_requirements(jd)
    assert {"python", "django", "docker"} <= set(req["required_skills"])
    assert req["required_experience_years"] == 3.0
    assert req["raw_text"] == jd


def test_empty_jd():
    req = extract_jd_requirements("")
    assert req["required_skills"] == []
    assert req["required_experience_years"] == 0.0
