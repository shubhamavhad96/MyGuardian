import re
from typing import Any, Dict

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(
    r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_pii(text: str) -> str:
    text = EMAIL_RE.sub("[EMAIL_REDACTED]", text)
    text = PHONE_RE.sub("[PHONE_REDACTED]", text)
    text = SSN_RE.sub("[SSN_REDACTED]", text)
    return text


def safe_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    safe = {}
    for key, value in data.items():
        if isinstance(value, str):
            safe[key] = redact_pii(value)
        elif isinstance(value, dict):
            safe[key] = safe_log_data(value)
        elif isinstance(value, list):
            safe[key] = [
                safe_log_data(item) if isinstance(item, dict)
                else redact_pii(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            safe[key] = value
    return safe
