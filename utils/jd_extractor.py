"""
Stage 5 & 6: Enter and process the Job Description, and extract the
required skills and required years of experience from it.
"""
from .info_extractor import extract_experience_years, extract_skills
from .skills_vocabulary import SKILL_VOCABULARY


def extract_jd_requirements(jd_text: str, vocabulary=None) -> dict:
    """
    Parse a raw Job Description string into structured requirements:
    the required skills (matched against the skill vocabulary) and the
    minimum years of experience requested.
    """
    vocabulary = vocabulary or SKILL_VOCABULARY
    required_skills = extract_skills(jd_text, vocabulary)
    required_experience = extract_experience_years(jd_text)

    return {
        "required_skills": required_skills,
        "required_experience_years": required_experience,
        "raw_text": jd_text,
    }
