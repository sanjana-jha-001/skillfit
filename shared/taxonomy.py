"""Shared contract: the 12 RADIX skill categories, the skill record shape,
keyword dictionary, aliases and implied skills.

Every module imports from here so all five pieces speak the same JSON.
"""
import re

CATEGORY_CODES = ["DSA", "COD", "OOD", "APTI", "COMM", "AI", "CLOUD",
                  "SQL", "SWE", "SYSD", "NETW", "OS", "OTHER"]

# Canonical skill name -> category_code.
KEYWORDS = {
    "python": "COD", "java": "COD", "c++": "COD", "javascript": "COD",
    "typescript": "COD", "react": "COD", "node.js": "COD", "fastapi": "COD",
    "flask": "COD", "django": "COD", "pandas": "COD", "numpy": "COD",
    "data structures": "DSA", "algorithms": "DSA", "dynamic programming": "DSA",
    "object-oriented": "OOD", "oop": "OOD", "design patterns": "OOD",
    "aptitude": "APTI", "quantitative aptitude": "APTI",
    "communication": "COMM", "presentation": "COMM", "teamwork": "COMM",
    "stakeholder": "COMM",
    "machine learning": "AI", "deep learning": "AI", "nlp": "AI", "llm": "AI",
    "langchain": "AI", "pytorch": "AI", "tensorflow": "AI",
    "scikit-learn": "AI", "generative ai": "AI",
    "aws": "CLOUD", "azure": "CLOUD", "gcp": "CLOUD", "docker": "CLOUD",
    "kubernetes": "CLOUD", "cloud": "CLOUD",
    "sql": "SQL", "postgresql": "SQL", "mysql": "SQL", "supabase": "SQL",
    "database": "SQL", "power bi": "OTHER", "excel": "OTHER",
    "statistics": "APTI",
    "software engineering": "SWE", "agile": "SWE", "scrum": "SWE", "git": "SWE",
    "unit testing": "SWE", "ci/cd": "SWE",
    "system design": "SYSD", "distributed systems": "SYSD", "scalability": "SYSD",
    "networking": "NETW", "tcp/ip": "NETW", "http": "NETW", "dns": "NETW",
    "operating system": "OS", "linux": "OS", "multithreading": "OS",
    "concurrency": "OS",
}

# Alternative spellings -> canonical name. Matched as whole words.
ALIASES = {
    "postgres": "postgresql", "postgre sql": "postgresql",
    "ml": "machine learning", "js": "javascript", "ts": "typescript",
    "k8s": "kubernetes", "google cloud": "gcp", "google cloud platform": "gcp",
    "amazon web services": "aws", "amazon aws": "aws",
    "data structure": "data structures", "dsa": "data structures",
    "ci cd": "ci/cd", "unit tests": "unit testing",
    "oops": "object-oriented", "oo design": "object-oriented",
    "generative ai": "generative ai", "gen ai": "generative ai",
    "powerbi": "power bi", "power-bi": "power bi",
}

# If a skill is found, these related skills are also credited (lower evidence).
IMPLIES = {
    "postgresql": ["sql"], "mysql": ["sql"], "supabase": ["sql"],
    "pytorch": ["machine learning"], "tensorflow": ["machine learning"],
    "scikit-learn": ["machine learning"], "langchain": ["llm"],
    "fastapi": ["python"], "flask": ["python"], "django": ["python"],
    "pandas": ["python"], "numpy": ["python"],
}

CONFIDENCE_RANK = {"high": 3, "medium": 2, "low": 1}


def normalize(name):
    return re.sub(r"\s+", " ", name.strip().lower())


def canonical_name(name):
    n = normalize(name)
    return ALIASES.get(n, n)


def make_skill(name, category, evidence, confidence="medium"):
    """Build one skill record in the shared format."""
    assert category in CATEGORY_CODES, f"unknown category {category}"
    return {
        "skill_name": name,
        "category_code": category,
        "evidence": evidence[:200],
        "confidence": confidence,
    }


def _pattern(term):
    return re.compile(r"(?<![\w+#.])" + re.escape(term) + r"(?![\w+#])",
                      re.IGNORECASE)


def extract_keywords(text, confidence="medium"):
    """Find skills in text (keywords and aliases, whole words only).

    Returns one skill record per canonical skill, plus implied skills.
    """
    terms = {kw: kw for kw in KEYWORDS}
    terms.update(ALIASES)

    found, seen = [], set()
    lines = text.splitlines()
    for term, canon in terms.items():
        pat = _pattern(term)
        for line in lines:
            if pat.search(line):
                if canon not in seen:
                    seen.add(canon)
                    found.append(make_skill(canon, KEYWORDS[canon],
                                            line.strip(), confidence))
                break

    for skill in list(found):
        for implied in IMPLIES.get(skill["skill_name"], []):
            if implied not in seen and implied in KEYWORDS:
                seen.add(implied)
                found.append(make_skill(implied, KEYWORDS[implied],
                                        f"implied by {skill['skill_name']}",
                                        confidence))
    return found


def merge_skills(*lists):
    """Combine skill lists, keeping one entry per skill (the most confident)."""
    best = {}
    for skills in lists:
        for s in skills:
            key = canonical_name(s["skill_name"])
            current = best.get(key)
            if current is None or (CONFIDENCE_RANK[s["confidence"]]
                                   > CONFIDENCE_RANK[current["confidence"]]):
                best[key] = s
    return list(best.values())
