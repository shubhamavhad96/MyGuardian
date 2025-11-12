import re

# Very small, conservative list for demo. Expand later.
PROFANE = {"damn", "shit", "bastard"}  # demo only

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(
    r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def toxicity_score(text: str) -> float:
    score = 0.0
    if EMAIL_RE.search(text):
        score += 0.04
    if PHONE_RE.search(text):
        score += 0.04
    if SSN_RE.search(text):
        score += 0.08
    if any(bad in text.lower() for bad in PROFANE):
        score += 0.04
    return min(1.0, round(score, 4))
