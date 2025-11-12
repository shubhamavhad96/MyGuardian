from typing import List, Optional
from .text_utils import tokens, ngrams, normalize
import os


def concat_passages(passages: List[dict]) -> str:
    return "\n".join(p.get("text", "") for p in passages)


def ngram_overlap_score(answer: str, passages: List[dict], n: int = 3) -> float:
    ans_toks = tokens(answer)
    if not ans_toks:
        return 0.0
    
    if len(ans_toks) < 3:
        n = 2
    if len(ans_toks) < 2:
        n = 1

    ans_ngrams = set(ngrams(ans_toks, n))
    ctx_text = concat_passages(passages)
    ctx_ngrams = set(ngrams(tokens(ctx_text), n))

    if not ans_ngrams:
        return 0.0
    overlap = ans_ngrams & ctx_ngrams
    score = len(overlap) / max(1, len(ans_ngrams))
    uni_overlap = set(ngrams(ans_toks, 1)) & set(ngrams(tokens(ctx_text), 1))
    unigram_score = len(uni_overlap) / max(1, len(set(ngrams(ans_toks, 1))))
    mixed = 0.7 * score + 0.3 * unigram_score
    return max(0.0, min(1.0, round(mixed, 4)))


def semantic_entailment_score(answer: str, passages: List[dict]) -> Optional[float]:
    if os.getenv("USE_SEMANTIC_FAITHFULNESS", "false").lower() != "true":
        return None
    
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        if not hasattr(semantic_entailment_score, "_model"):
            semantic_entailment_score._model = SentenceTransformer('all-MiniLM-L6-v2')
        
        model = semantic_entailment_score._model
        
        answer_embedding = model.encode([answer], convert_to_numpy=True)[0]
        passage_texts = [p.get("text", "") for p in passages if p.get("text")]
        if not passage_texts:
            return None
        
        passage_embeddings = model.encode(passage_texts, convert_to_numpy=True)
        
        similarities = np.dot(passage_embeddings, answer_embedding) / (
            np.linalg.norm(passage_embeddings, axis=1) * np.linalg.norm(answer_embedding)
        )
        max_sim = float(np.max(similarities))
        
        return max(0.0, min(1.0, (max_sim + 1) / 2))
    except ImportError:
        return None
    except Exception:
        return None


def blended_faithfulness_score(answer: str, passages: List[dict], use_semantic: bool = False) -> float:
    overlap_score = ngram_overlap_score(answer, passages)
    
    if use_semantic:
        semantic_score = semantic_entailment_score(answer, passages)
        if semantic_score is not None:
            return 0.6 * overlap_score + 0.4 * semantic_score
    
    return overlap_score
