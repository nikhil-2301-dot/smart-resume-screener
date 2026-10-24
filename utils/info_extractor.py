"""
Stage 4: Extract name, email, phone, skills, education and experience
from raw resume text.

These are rule-based / regex heuristics deliberately kept simple and
transparent for the MVP, as recommended in the roadmap. They can later
be swapped out for a proper NER model (e.g. spaCy) without changing
the rest of the app.
"""
import re
from .skills_vocabulary import SKILL_VOCABULARY

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"(?<!\w)\+?\(?\d[\d\s().-]{6,}\d(?!\w)")
# Year ranges such as "2019 - 2023" look like phone numbers but aren't
DATE_RANGE_REGEX = re.compile(r"^\s*(19|20)\d{2}\s*[-\u2013]\s*((19|20)\d{2}|present)\s*$", re.IGNORECASE)

# Matches things like "5 years", "5+ years", "5.5 years of experience"
EXPERIENCE_REGEX = re.compile(
    r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)\b", re.IGNORECASE
)

EDUCATION_KEYWORDS = [
    "b.tech", "btech", "b.e.", "bachelor", "bsc", "b.sc", "m.tech", "mtech",
    "master", "msc", "m.sc", "mba", "phd", "ph.d", "diploma", "b.com", "bca",
    "mca", "associate degree", "high school",
]


def extract_email(text: str) -> str:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    for match in PHONE_REGEX.finditer(text):
        candidate = match.group(0)
        if DATE_RANGE_REGEX.match(candidate):
            continue
        digits = re.sub(r"\D", "", candidate)
        # A real phone number typically has 7-13 digits; this filters out
        # stray short number matches (e.g. page numbers, list bullets).
        if 7 <= len(digits) <= 13:
            return candidate.strip()
    return ""


def extract_name(text: str) -> str:
    """
    Heuristic: the candidate's name is usually the first non-empty line
    that isn't an email/phone and doesn't contain typical resume-header
    words. This works well for most single-column resumes.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    header_blacklist = {
        "resume", "curriculum vitae", "cv", "profile", "contact", "summary",
    }
    for line in lines[:8]:
        lower = line.lower()
        if EMAIL_REGEX.search(line) or PHONE_REGEX.search(line):
            continue
        if lower in header_blacklist:
            continue
        word_count = len(line.split())
        if 1 <= word_count <= 5 and not any(char.isdigit() for char in line):
            return line
    return "Unknown"


def extract_skills(text: str, vocabulary=None) -> list:
    """Return the list of vocabulary skills that appear in the resume text."""
    vocabulary = vocabulary or SKILL_VOCABULARY
    text_lower = text.lower()
    found = []
    for skill in vocabulary:
        pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill) + r"(?![a-zA-Z0-9+#])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_education(text: str) -> list:
    """Return lines that mention a recognizable education/degree keyword."""
    found = []
    for line in text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue
        lower = line_stripped.lower()
        if any(keyword in lower for keyword in EDUCATION_KEYWORDS):
            found.append(line_stripped)
    return found


def extract_experience_years(text: str) -> float:
    """
    Return the maximum number of years of experience mentioned in the text.
    Picking the max (rather than the first) tends to be more robust because
    resumes often restate total experience in a summary section using the
    highest, most complete figure.
    """
    matches = EXPERIENCE_REGEX.findall(text)
    years = [float(m) for m in matches]
    return max(years) if years else 0.0


def extract_candidate_info(text: str) -> dict:
    """Run all extractors and return a single structured dict for a candidate."""
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience_years": extract_experience_years(text),
        "raw_text": text,
    }
