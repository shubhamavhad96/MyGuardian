import time
from typing import Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from redis import Redis
from rq import Queue
from app.config import settings

REQUESTS = Counter(
    "guardrail_requests_total",
    "Total /evaluate requests completed",
    ["decision"]
)

FAILURES = Counter(
    "guardrail_failures_total",
    "Total /evaluate failures",
    ["reason"]
)

LATENCY = Histogram(
    "guardrail_eval_latency_seconds",
    "Latency for full evaluate path (API enqueue -> result)",
    buckets=(0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 2.0, 5.0)
)

JOBS_IN_PROGRESS = Gauge(
    "guardrail_worker_jobs_in_progress",
    "Current RQ jobs in progress on 'eval' queue",
)

SHADOW_REQUESTS = Counter(
    "guardrail_shadow_requests_total",
    "Total /evaluate requests in shadow mode",
    ["decision"]
)

SHADOW_LATENCY = Histogram(
    "guardrail_shadow_eval_latency_seconds",
    "Latency for shadow mode evaluations",
    buckets=(0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 2.0, 5.0)
)

SHADOW_DISAGREEMENT = Counter(
    "guardrail_shadow_disagreements_total",
    "Total disagreements between shadow and enforce mode",
    ["shadow_decision", "enforce_decision"]
)


def metrics_endpoint() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class LatencyTimer:
    def __enter__(self):
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.duration = time.perf_counter() - self._t0


def sample_rq_gauges():
    try:
        r = Redis.from_url(settings.REDIS_URL)
        q = Queue("eval", connection=r)
        queued = len(q.jobs)
        JOBS_IN_PROGRESS.set(queued)
    except Exception as e:
        FAILURES.labels(reason="rq_stats_error").inc()
