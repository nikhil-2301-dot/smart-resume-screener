"""
Stages 7-10: TF-IDF + cosine similarity, skill matching, experience
matching, and the final weighted candidate ranking algorithm.

Final Score = 50% x JD Similarity + 30% x Skill Match + 20% x Experience Match
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Weights from the roadmap's core matching algorithm (Section 4)
WEIGHT_JD_SIMILARITY = 0.50
WEIGHT_SKILL_MATCH = 0.30
WEIGHT_EXPERIENCE_MATCH = 0.20


def compute_jd_similarity(jd_text: str, resume_texts: list) -> list:
    """
    Stage 7: TF-IDF + cosine similarity between the full Job Description
    and each resume's full text. Returns a similarity score in [0, 1]
    for each resume, in the same order as resume_texts.
    """
    if not resume_texts:
        return []

    corpus = [jd_text] + resume_texts
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(jd_vector, resume_vectors)[0]
    return similarities.tolist()


def compute_skill_match(required_skills: list, candidate_skills: list) -> tuple:
    """
    Stage 8: Percentage of required skills found in the candidate's resume.
    Returns (match_ratio, matched_skills, missing_skills).
    """
    if not required_skills:
        # No skills were parsed from the JD, so this component can't
        # penalise anyone; treat as neutral (perfect match).
        return 1.0, [], []

    required_set = set(s.lower() for s in required_skills)
    candidate_set = set(s.lower() for s in candidate_skills)

    matched = sorted(required_set & candidate_set)
    missing = sorted(required_set - candidate_set)

    match_ratio = len(matched) / len(required_set)
    return match_ratio, matched, missing


def compute_experience_match(required_years: float, candidate_years: float) -> float:
    """
    Stage 9: Whether the candidate meets the required experience.

    If the JD didn't specify a requirement, treat as fully met (neutral).
    If the candidate meets or exceeds the requirement, score 1.0.
    Otherwise, score proportionally (e.g. 3 years against a 5-year
    requirement scores 0.6) so partial experience still counts for something
    rather than being scored as a hard zero.
    """
    if required_years <= 0:
        return 1.0
    if candidate_years >= required_years:
        return 1.0
    return max(0.0, candidate_years / required_years)


def compute_final_score(jd_similarity: float, skill_match: float, experience_match: float) -> float:
    """Combine the three components into the final weighted percentage score."""
    score = (
        WEIGHT_JD_SIMILARITY * jd_similarity
        + WEIGHT_SKILL_MATCH * skill_match
        + WEIGHT_EXPERIENCE_MATCH * experience_match
    )
    return round(score * 100, 2)


def rank_candidates(jd_requirements: dict, candidates: list) -> list:
    """
    Run the full scoring pipeline over a list of candidate info dicts
    (as produced by info_extractor.extract_candidate_info) and return
    them sorted by final score, highest first.

    Each candidate dict is enriched in-place with:
      jd_similarity_pct, skill_match_pct, experience_match_pct,
      final_score, matched_skills, missing_skills
    """
    if not candidates:
        return []

    resume_texts = [c["raw_text"] for c in candidates]
    jd_similarities = compute_jd_similarity(jd_requirements["raw_text"], resume_texts)

    required_skills = jd_requirements["required_skills"]
    required_years = jd_requirements["required_experience_years"]

    for candidate, jd_sim in zip(candidates, jd_similarities):
        skill_ratio, matched, missing = compute_skill_match(
            required_skills, candidate["skills"]
        )
        exp_ratio = compute_experience_match(
            required_years, candidate["experience_years"]
        )
        final = compute_final_score(jd_sim, skill_ratio, exp_ratio)

        candidate["jd_similarity_pct"] = round(jd_sim * 100, 2)
        candidate["skill_match_pct"] = round(skill_ratio * 100, 2)
        candidate["experience_match_pct"] = round(exp_ratio * 100, 2)
        candidate["matched_skills"] = matched
        candidate["missing_skills"] = missing
        candidate["final_score"] = final

    return sorted(candidates, key=lambda c: c["final_score"], reverse=True)
