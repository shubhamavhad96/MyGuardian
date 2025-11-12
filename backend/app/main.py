from fastapi import FastAPI, HTTPException, Request, Header, Depends
from rq.job import Job
from .schemas import EvaluateRequest, EvaluateResponse
from .config import settings
from .queue import q
from .metrics import LATENCY, REQUESTS, FAILURES, SHADOW_REQUESTS, SHADOW_LATENCY, SHADOW_DISAGREEMENT, metrics_endpoint, LatencyTimer, sample_rq_gauges
from .tracing import setup_tracer
from .validation import validate_request
from .auth import verify_api_key, rate_limit
from .logging_utils import safe_log_data
from .version import get_version_info
from .shadow_analytics import get_shadow_tracker
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
import logging
import os
import uuid

logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Guardrail API", version="0.1-day6")
tracer = setup_tracer("guardrail-api")
FastAPIInstrumentor.instrument_app(app)

GUARDRAIL_MODE = os.getenv("GUARDRAIL_MODE", "enforce").lower()


@app.get("/health")
def health():
    sample_rq_gauges()
    return {"ok": True}


@app.get("/version")
def version():
    return get_version_info()


@app.get("/reports/shadow-today")
def shadow_report_today(request: Request, api_key: str = Header(None, alias="X-API-Key")):
    verify_api_key(api_key)
    tracker = get_shadow_tracker()
    return tracker.generate_daily_report()


@app.get("/metrics")
def metrics():
    return metrics_endpoint()


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(
    req: EvaluateRequest,
    request: Request,
    api_key: str = Header(None, alias="X-API-Key"),
    x_request_id: str = Header(None, alias="X-Request-ID")
):
    request_id = x_request_id or str(uuid.uuid4())
    
    verify_api_key(api_key)
    rate_limit_result = rate_limit(request.client.host if request.client else "unknown")
    if rate_limit_result:
        return rate_limit_result
    validate_request(req.passages, req.question, req.answer)

    with LatencyTimer() as T, tracer.start_as_current_span("evaluate.request") as span:
        span.set_attribute("request.id", request_id)
        span.set_attribute("question.len", len(req.question or ""))
        span.set_attribute("answer.len", len(req.answer or ""))
        span.set_attribute("passages.count", len(req.passages or []))
        span.set_attribute("mode", GUARDRAIL_MODE)

        try:
            with tracer.start_as_current_span("evaluate.enqueue"):
                job: Job = q.enqueue(
                    "worker.worker.evaluate_payload", req.model_dump())
        except Exception:
            FAILURES.labels(reason="enqueue_error").inc()
            span.record_exception(Exception("enqueue_error"))
            raise HTTPException(status_code=500, detail="Failed to enqueue")

        timeout = settings.EVAL_TIMEOUT_SEC
        import time
        for _ in range(timeout * 10):
            job.refresh()
            if job.is_finished:
                result = job.result
                resp = EvaluateResponse(**result)
                
                original_decision = resp.decision
                if GUARDRAIL_MODE == "shadow":
                    SHADOW_REQUESTS.labels(decision=original_decision).inc()
                    SHADOW_LATENCY.observe(T.duration)
                    tracker = get_shadow_tracker()
                    tracker.record(
                        question=req.question,
                        answer=req.answer,
                        shadow_decision=original_decision,
                        scores=resp.scores.model_dump(),
                        question_len=len(req.question),
                        answer_len=len(req.answer),
                    )
                    if original_decision != "allow":
                        SHADOW_DISAGREEMENT.labels(
                            shadow_decision=original_decision,
                            enforce_decision="allow"
                        ).inc()
                    logger.info(f"Shadow mode: would have returned {original_decision}, but allowing")
                    resp.decision = "allow"
                else:
                    REQUESTS.labels(decision=resp.decision).inc()
                    LATENCY.observe(T.duration)

                safe_data = safe_log_data({
                    "decision": resp.decision,
                    "original_decision": original_decision if GUARDRAIL_MODE == "shadow" else None,
                    "scores": resp.scores.model_dump(),
                    "question_len": len(req.question),
                    "answer_len": len(req.answer),
                    "mode": GUARDRAIL_MODE,
                    "request_id": request_id,
                })
                logger.info(f"Evaluation complete: {safe_data}")

                with tracer.start_as_current_span("evaluate.finish") as s2:
                    s2.set_attribute("decision", resp.decision)
                    s2.set_attribute("faithfulness", resp.scores.faithfulness)
                    s2.set_attribute("coverage", resp.scores.coverage)
                    s2.set_attribute("toxicity", resp.scores.toxicity)
                    s2.set_attribute("mode", GUARDRAIL_MODE)
                    if GUARDRAIL_MODE == "shadow":
                        s2.set_attribute("shadow_decision", original_decision)
                
                return resp
            if job.is_failed:
                FAILURES.labels(reason="worker_job_failed").inc()
                span.record_exception(Exception("worker_job_failed"))
                if GUARDRAIL_MODE != "shadow":
                    LATENCY.observe(T.duration)
                raise HTTPException(
                    status_code=500, detail="Worker job failed")
            time.sleep(0.1)

    FAILURES.labels(reason="timeout").inc()
    span.record_exception(Exception("timeout"))
    if GUARDRAIL_MODE != "shadow":
        LATENCY.observe(T.duration)
    raise HTTPException(status_code=504, detail="Evaluation timed out")
