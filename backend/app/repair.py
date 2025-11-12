import re
from typing import List, Dict
from .coverage import decompose
from .retrieval import top_ids, pick_passages
from .text_utils import normalize

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _first_sentences(text: str, n: int) -> List[str]:
    sents = _SENT_SPLIT.split(text.strip())
    return [s for s in sents if s][:n]


def _format_citation(p: Dict) -> str:
    src = p.get("source") or "src"
    pid = p.get("id") or "p"
    return f"[{src}:{pid}]"


def summarize_from_passages(passages: List[Dict], max_sentences: int, add_citations: bool) -> str:
    chosen: List[str] = []
    for p in passages:
        sents = _first_sentences(p.get("text", ""), max(
            1, max_sentences - len(chosen)))
        for s in sents:
            if not s:
                continue
            if add_citations:
                s = f"{s} {_format_citation(p)}"
            chosen.append(s)
            if len(chosen) >= max_sentences:
                break
        if len(chosen) >= max_sentences:
            break
    return " ".join(chosen).strip()


def repair_answer(
    question: str,
    answer: str,
    passages: List[Dict],
    retriever_mode: str = "hybrid",
    top_k: int = 3,
    max_sentences: int = 4,
    add_missing_parts: bool = True,
    add_citations: bool = True,
    missing_parts: List[str] = None,
) -> str:
    # Pull general support
    ids_q = top_ids(question, passages, retriever_mode, top_k)
    support = pick_passages(passages, ids_q)

    augment: List[Dict] = []
    missing_list = missing_parts or []
    if add_missing_parts:
        subs = decompose(question)
        ans_norm = normalize(answer)
        for sub in subs:
            if sub not in ans_norm:
                missing_list.append(sub)
                ids_sub = top_ids(sub, passages, retriever_mode,
                                  max(1, top_k // 2) or 1)
                augment.extend(pick_passages(passages, ids_sub))

    merged = support + augment
    if not merged:
        return answer

    stitched = summarize_from_passages(
        merged, max_sentences=max_sentences, add_citations=add_citations)

    if stitched and stitched not in answer:
        repair_section = ["\n\n**Auto-repair applied:**\n"]
        
        if missing_list:
            repair_section.append("**Missing parts identified:**\n")
            for part in missing_list[:5]:
                repair_section.append(f"  • {part}\n")
            repair_section.append("\n")
        
        repair_section.append("**Added grounded content:**\n")
        repair_section.append(stitched)
        repair_section.append("\n\n*Why this changed: Answer was missing key information from sources. Added relevant passages with citations.*")
        
        return (answer.rstrip() + "".join(repair_section)).strip()
    return answer
