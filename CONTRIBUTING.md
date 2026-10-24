# Contributing

Thanks for wanting to help! The setup is quick.

```bash
git clone https://github.com/<your-username>/smart-resume-screener.git
cd smart-resume-screener
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
streamlit run app.py
```

## Guidelines

- Keep the extraction logic simple and explainable. Rules and regex are on purpose.
- Add or update a test in `tests/` for every behaviour change.
- Run `ruff check .` and `pytest` before opening a pull request.
- Never commit real resumes or any personal data. Use `sample_data/` instead.
- To support a new skill, just add it to `utils/skills_vocabulary.py`.
