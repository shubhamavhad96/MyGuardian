import re
from typing import List

_ws = re.compile(r"\s+")
_punct = re.compile(r"[^\w\s]")


def normalize(text: str) -> str:
    text = text.lower()
    text = _punct.sub(" ", text)
    text = _ws.sub(" ", text).strip()
    return text


def tokens(text: str) -> List[str]:
    return normalize(text).split()


def ngrams(tok: List[str], n: int) -> List[str]:
    if n <= 1:
        return tok[:]
    return [" ".join(tok[i:i+n]) for i in range(0, max(0, len(tok)-n+1))]
