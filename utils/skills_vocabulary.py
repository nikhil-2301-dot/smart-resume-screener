"""
A reference vocabulary of common technical/professional skills.

This is intentionally a plain, editable Python list rather than something
hidden in a database, so you can quickly extend it for your domain
(e.g. add marketing, finance, or design skills) without touching any
other code.
"""

SKILL_VOCABULARY = [
    # Programming languages
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "golang",
    "rust", "r", "matlab", "scala", "kotlin", "swift", "php", "ruby", "sql",

    # Web / frameworks
    "django", "flask", "fastapi", "react", "angular", "vue", "node.js", "nodejs",
    "express", "spring", "spring boot", "asp.net", ".net", "next.js", "streamlit",

    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow",
    "pytorch", "keras", "opencv", "spacy", "nltk", "hugging face", "transformers",
    "sentence transformers", "llm", "generative ai", "data analysis", "data science",
    "statistics", "tf-idf", "cosine similarity",

    # Databases
    "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis", "oracle",
    "elasticsearch", "cassandra", "dynamodb",

    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "jenkins", "ci/cd", "git", "github", "gitlab", "linux", "bash", "shell scripting",

    # Data viz / BI
    "plotly", "matplotlib", "seaborn", "tableau", "power bi", "excel",

    # Other common resume skills
    "rest api", "restful api", "api development", "microservices", "agile",
    "scrum", "project management", "communication", "leadership", "problem solving",
    "html", "css", "django rest framework", "graphql",
]
