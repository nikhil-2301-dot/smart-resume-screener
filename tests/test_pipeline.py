"""End-to-end check on the bundled sample data."""
from pathlib import Path

from utils.info_extractor import extract_candidate_info
from utils.jd_extractor import extract_jd_requirements
from utils.matcher import rank_candidates
from utils.text_extract import extract_text

SAMPLES = Path(__file__).resolve().parent.parent / "sample_data"


def test_sample_pipeline_ranks_backend_dev_first():
    jd = (SAMPLES / "sample_jd.txt").read_text()
    req = extract_jd_requirements(jd)
    candidates = []
    for f in sorted(SAMPLES.glob("*.docx")):
        info = extract_candidate_info(extract_text(f.name, f.read_bytes()))
        info["source_file"] = f.name
        candidates.append(info)

    ranked = rank_candidates(req, candidates)
    assert len(ranked) == 3
    assert ranked[0]["name"] == "Aarav Sharma"
    scores = [c["final_score"] for c in ranked]
    assert scores == sorted(scores, reverse=True)
