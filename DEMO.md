# MyGuardian Demo Guide

6 shell commands to reproduce all features and results.

## Prerequisites

```bash
# Ensure Docker is running
docker --version

# Ensure ports are free: 8000, 9090, 16686, 6379
```

## Step 1: Start Everything

```bash
cd backend
docker compose up --build
```

Wait for all services to start (check logs: `docker compose logs -f`).

**Services:**
- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Jaeger: http://localhost:16686

## Step 2: Test Basic Evaluation

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are side-effects of metformin?",
    "answer": "Common side-effects include nausea and diarrhea.",
    "passages": [
      {"id":"p1","text":"Common side-effects are nausea and diarrhea.","source":"med-guide"}
    ]
  }' | jq
```

**Expected:** `{"decision": "allow", "scores": {...}, ...}`

## Step 3: Test PII Blocking

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How to contact support?",
    "answer": "Email me at user@example.com or call 202-555-0132.",
    "passages": [{"id":"p1","text":"Use official channels.","source":"policy"}]
  }' | jq
```

**Expected:** `{"decision": "block", "explanations": ["Toxic/PII content detected"]}`

## Step 4: Run Load Test (Verify SLO)

```bash
# In a new terminal
cd backend
source .venv/bin/activate
locust -f locustfile.py --host=http://localhost:8000
```

**Then:**
1. Open http://localhost:8089
2. Set: 50 users, spawn rate 10
3. Start test
4. Check p95 latency < 0.5s

**Or scale workers:**
```bash
docker compose up --scale worker=3 -d
```

## Step 5: View Traces in Jaeger

```bash
# Make a few requests first
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/evaluate \
    -H "Content-Type: application/json" \
    -d '{"question":"Test","answer":"Test","passages":[{"id":"p1","text":"Test","source":"test"}]}' > /dev/null
done

# Open Jaeger UI
open http://localhost:16686
# Select "guardrail-api" or "guardrail-worker"
# Click "Find Traces"
# View span details
```

**Expected:** See spans like:
- `evaluate.request`
- `evaluate.enqueue`
- `worker.score`
- `worker.route`
- `worker.repair` (if decision=repair)

## Step 6: Run Eval Harness

```bash
cd backend
source .venv/bin/activate

# Generate cases (if needed)
python eval/generate_cases.py

# Run evaluation
python eval/run_eval.py
```

**Expected Output:**
```
=== Eval Summary ===
Total: 50, Passed: 45+, Failed: <5
Decisions: {'allow': X, 'repair': Y, 'block': Z}
Faithfulness avg=0.XX
Coverage     avg=0.XX
Toxicity     avg=0.XX
```

## Step 7: View Metrics (Prometheus)

```bash
# Open Prometheus
open http://localhost:9090

# Try these queries:
# 1. Request rate by decision:
#    sum(rate(guardrail_requests_total[5m])) by (decision)

# 2. p95 latency:
#    histogram_quantile(0.95, sum(rate(guardrail_eval_latency_seconds_bucket[5m])) by (le))

# 3. Failure rate:
#    sum(rate(guardrail_failures_total[5m])) by (reason)
```

## Step 8: Import Grafana Dashboard (Optional)

1. Start Grafana (add to docker-compose.yml if needed)
2. Create Prometheus data source: `http://prometheus:9090`
3. Import `ops/grafana-dashboard-prom.json`
4. View pre-built panels

## Quick Verification Checklist

- Health endpoint returns `{"ok": true}`
- ALLOW case returns `decision: "allow"`
- BLOCK case returns `decision: "block"` with PII explanation
- Jaeger shows traces with spans
- Prometheus scrapes metrics
- p95 latency < 0.5s under load
- Eval harness: 45+/50 cases pass

## Troubleshooting

**Worker not processing jobs:**
```bash
docker compose logs worker
# Check Redis connection
docker compose exec api redis-cli -h redis ping
```

**Metrics not showing:**
```bash
curl http://localhost:8000/metrics | grep guardrail
# Should show counters and histograms
```

**Traces not appearing:**
```bash
# Check Jaeger is running
docker compose ps jaeger
# Check OTLP endpoint in logs
docker compose logs api | grep OTLP
```

## Next Steps

- Tune `policy.yaml` based on your use case
- Add your own test cases to `eval/seed.jsonl`
- Customize repair behavior in `policy.yaml`
- Set up alerts in Prometheus (see `ops/alerts.yml`)

