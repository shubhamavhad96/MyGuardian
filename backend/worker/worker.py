from app.truth import ngram_overlap_score
from app.safety import toxicity_score
from app.coverage import coverage_score
from app.policy import load_policy, route_decision
from app.repair import repair_answer
from app.tracing import setup_tracer

tracer = setup_tracer("guardrail-worker")

_POLICY = load_policy()


def evaluate_payload(payload: dict) -> dict:
    question = payload.get("question", "")
    answer = payload.get("answer", "")
    passages = payload.get("passages", []) or []

    with tracer.start_as_current_span("worker.score") as s:
        s.set_attribute("passages.count", len(passages))
        faith = ngram_overlap_score(answer, passages, n=3)
        cov, missing = coverage_score(question, passages)
        tox = toxicity_score(answer)

    scores = {
        "faithfulness": round(float(faith), 2),
        "coverage": round(float(cov), 2),
        "toxicity": round(float(tox), 2),
    }

    with tracer.start_as_current_span("worker.route") as s2:
        decision, reasons = route_decision(scores, _POLICY, missing)
        s2.set_attribute("decision", decision)

    repaired = None
    if decision == "repair":
        with tracer.start_as_current_span("worker.repair") as s3:
            s3.set_attribute("repair.retriever_mode",
                             _POLICY.repair.retriever_mode)
            repaired = repair_answer(
                question=question,
                answer=answer,
                passages=passages,
                retriever_mode=_POLICY.repair.retriever_mode,
                top_k=_POLICY.repair.top_k,
                max_sentences=_POLICY.repair.max_sentences,
                add_missing_parts=_POLICY.repair.add_missing_parts,
                add_citations=_POLICY.repair.add_citations,
                missing_parts=missing,  # Pass missing parts for checklist
            )

    return {
        "decision": decision,
        "scores": scores,
        "repaired_answer": repaired,
        "explanations": reasons,
        "meta": {"engine": "day6", "v": "day6"},
    }
