from typing import List, Tuple, Dict
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from .text_utils import normalize, tokens


def _prep_corpus(passages: List[Dict]) -> Tuple[List[str], List[List[str]]]:
    docs = [normalize(p.get("text", "")) for p in passages]
    tok_docs = [tokens(d) for d in docs]
    return docs, tok_docs


def bm25_scores(query: str, passages: List[Dict]) -> List[Tuple[int, float]]:
    docs, tok_docs = _prep_corpus(passages)
    bm25 = BM25Okapi(tok_docs)
    qtok = tokens(normalize(query))
    scores = bm25.get_scores(qtok)
    order = np.argsort(scores)[::-1]
    return [(int(i), float(scores[i])) for i in order]


def tfidf_scores(query: str, passages: List[Dict]) -> List[Tuple[int, float]]:
    docs, _ = _prep_corpus(passages)
    if len(docs) == 0:
        return []
    vec = TfidfVectorizer(
        lowercase=False, preprocessor=lambda x: x, tokenizer=lambda x: x.split())
    X = vec.fit_transform([d for d in docs])
    q = normalize(query)
    qv = vec.transform([q])
    sims = (X @ qv.T).toarray().ravel()
    order = np.argsort(sims)[::-1]
    return [(int(i), float(sims[i])) for i in order]


def rrf_fuse(ranklists: List[List[int]], k: int = 60) -> Dict[int, float]:
    fused: Dict[int, float] = {}
    for rl in ranklists:
        for rank, doc_id in enumerate(rl, start=1):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank)
    return fused


def fused_rank(query: str, passages: List[Dict], top_k: int = 5) -> List[int]:
    if not passages:
        return []
    bm = bm25_scores(query, passages)
    tf = tfidf_scores(query, passages)

    bm_ids = [i for i, _ in bm]
    tf_ids = [i for i, _ in tf]

    fused = rrf_fuse([bm_ids, tf_ids], k=60)
    order = sorted(fused.items(), key=lambda x: x[1], reverse=True)
    return [idx for idx, _ in order[:top_k]]


def bm25_top_ids(query: str, passages: List[Dict], top_k: int = 5) -> List[int]:
    return [i for i, _ in bm25_scores(query, passages)[:top_k]]


def tfidf_top_ids(query: str, passages: List[Dict], top_k: int = 5) -> List[int]:
    return [i for i, _ in tfidf_scores(query, passages)[:top_k]]


def top_ids(query: str, passages: List[Dict], mode: str = "hybrid", top_k: int = 5) -> List[int]:
    mode = (mode or "hybrid").lower()
    if mode == "bm25":
        return bm25_top_ids(query, passages, top_k)
    if mode == "tfidf":
        return tfidf_top_ids(query, passages, top_k)
    return fused_rank(query, passages, top_k)


def pick_passages(passages: List[Dict], ids: List[int]) -> List[Dict]:
    out = []
    for i in ids:
        if 0 <= i < len(passages):
            out.append(passages[i])
    return out
