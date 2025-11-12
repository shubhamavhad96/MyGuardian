from typing import List, Dict, Tuple
import re
from .text_utils import normalize, tokens
from .retrieval import fused_rank

_SPLIT = re.compile(
    r"[;,.?]| and | or | & | versus | vs | with | without ", re.I)


def decompose(question: str) -> List[str]:
    q = normalize(question)
    parts = [p.strip() for p in _SPLIT.split(q)]
    parts = [p for p in parts if len(p.split()) >= 2]
    seen = set()
    uniq = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq or [q]


def subq_supported(subq: str, passages: List[Dict], min_overlap_tokens: int = 1) -> Tuple[bool, int]:
    if not passages:
        return False, 0
    top_ids = fused_rank(subq, passages, top_k=3)
    subq_toks = set(tokens(subq))
    best_overlap = 0
    for idx in top_ids:
        if idx >= len(passages):
            continue
        pas = passages[idx].get("text", "")
        tok = set(tokens(pas))
        overlap = len(subq_toks & tok)
        best_overlap = max(best_overlap, overlap)
        if overlap >= min_overlap_tokens:
            return True, overlap
    return False, best_overlap


def coverage_score(question: str, passages: List[Dict]) -> Tuple[float, List[str]]:
    subs = decompose(question)
    if not subs:
        return 1.0, []

    covered = 0
    missing: List[str] = []
    for s in subs:
        ok, _ = subq_supported(s, passages)
        if ok:
            covered += 1
        else:
            missing.append(s)

    score = round(covered / max(1, len(subs)), 4)
    return score, missing
