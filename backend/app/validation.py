from fastapi import HTTPException
from typing import List, Dict

MAX_PASSAGES = 50
MAX_PASSAGE_SIZE_BYTES = 4 * 1024
MAX_TOTAL_SIZE_BYTES = 200 * 1024


def validate_request(passages: List[Dict], question: str, answer: str) -> None:
    if len(passages) > MAX_PASSAGES:
        raise HTTPException(
            status_code=413,
            detail=f"Too many passages: {len(passages)} > {MAX_PASSAGES}"
        )

    total_size = len(question.encode('utf-8')) + len(answer.encode('utf-8'))
    for i, passage in enumerate(passages):
        text = passage.get("text", "")
        passage_size = len(text.encode('utf-8'))

        if passage_size > MAX_PASSAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Passage {i} exceeds size limit: {passage_size} > {MAX_PASSAGE_SIZE_BYTES} bytes"
            )

        total_size += passage_size

    if total_size > MAX_TOTAL_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Total request size exceeds limit: {total_size} > {MAX_TOTAL_SIZE_BYTES} bytes"
        )
