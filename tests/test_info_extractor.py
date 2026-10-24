from utils.info_extractor import (
    extract_candidate_info,
    extract_education,
    extract_email,
    extract_experience_years,
    extract_name,
    extract_phone,
    extract_skills,
)

RESUME = """Priya Nair
priya.nair@example.com | +91 98765 43210
Backend developer with 4.5 years of experience.
Skills: Python, Django, PostgreSQL, Docker, C++
B.Tech in Computer Science
"""


def test_email():
    assert extract_email(RESUME) == "priya.nair@example.com"
    assert extract_email("no email here") == ""


def test_phone_full_number_kept():
    assert extract_phone(RESUME) == "+91 98765 43210"


def test_phone_ignores_year_ranges_and_short_numbers():
    assert extract_phone("2019 - 2023") == ""
    assert extract_phone("Page 12") == ""


def test_name_is_first_plain_line():
    assert extract_name(RESUME) == "Priya Nair"


def test_name_skips_header_words():
    assert extract_name("Resume\nAnita Rao\nanita@x.com") == "Anita Rao"


def test_name_unknown_when_nothing_fits():
    assert extract_name("") == "Unknown"


def test_skills_found_and_sorted():
    skills = extract_skills(RESUME)
    assert {"python", "django", "postgresql", "docker", "c++"} <= set(skills)
    assert skills == sorted(skills)


def test_skill_word_boundaries():
    # "java" must not match inside "javascript"
    assert "java" not in extract_skills("I know JavaScript well")
    assert "javascript" in extract_skills("I know JavaScript well")


def test_education_lines():
    assert extract_education(RESUME) == ["B.Tech in Computer Science"]


def test_experience_takes_max():
    assert extract_experience_years("2 years at A, then 5+ years total") == 5.0
    assert extract_experience_years("4.5 years of experience") == 4.5
    assert extract_experience_years("fresher") == 0.0


def test_full_candidate_dict_has_all_keys():
    info = extract_candidate_info(RESUME)
    for key in ("name", "email", "phone", "skills", "education",
                "experience_years", "raw_text"):
        assert key in info
