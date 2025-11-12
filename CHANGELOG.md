# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-12

### Added

- **Core Guardrail System**
  - Three-metric evaluation: faithfulness (n-gram overlap), coverage (question decomposition), toxicity (PII/profanity)
  - Automatic repair with citations and missing parts
  - Block unsafe content (PII, profanity)
  - Policy-driven routing (allow/repair/block)

- **API Endpoints**
  - `POST /evaluate` - Main evaluation endpoint
  - `GET /health` - Health check
  - `GET /metrics` - Prometheus metrics
  - `GET /version` - Version information (git SHA, policy hash, build time)
  - `GET /reports/shadow-today` - Daily shadow mode report

- **Shadow Mode**
  - Dry-run mode via `GUARDRAIL_MODE=shadow`
  - Shadow metrics: `guardrail_shadow_requests_total`, `guardrail_shadow_eval_latency_seconds`
  - Disagreement tracking: `guardrail_shadow_disagreements_total`
  - Daily shadow reports with top queries that would have been blocked/repaired

- **Evaluation & Benchmarking**
  - 100-case benchmark CSV across health, finance, general knowledge
  - Markdown report generation: `python eval/run_eval.py --report md`
  - Domain breakdown and policy preset comparison
  - Metrics: hallucination rate, faithfulness@threshold, coverage@threshold

- **Integrations**
  - LangChain `GuardrailRunnable` for easy chain integration
  - TypeScript/OpenAI integration examples
  - Drop-in wrappers for LLM calls

- **Semantic Faithfulness (Optional)**
  - Sentence-transformers support via `USE_SEMANTIC_FAITHFULNESS=true`
  - Blended scoring: 0.6 * ngram + 0.4 * semantic
  - Graceful fallback to n-gram if semantic unavailable

- **Smart Repair**
  - Checklist-style reasoning with bullet points
  - Missing parts identification
  - "Why this changed" summary
  - Human-readable format with citations

- **Security & Compliance**
  - API key authentication (required by default)
  - Rate limiting (100 req/min per IP)
  - Input limits (50 passages, 4KB/passage, 200KB total)
  - PII redaction in all logs
  - No persistent data storage
  - Threat model documentation

- **Monitoring & Observability**
  - Prometheus metrics (requests, latency, failures, queue depth)
  - Jaeger distributed tracing
  - Grafana dashboard support
  - Shadow mode analytics

- **Packaging**
  - Python package (`rag-guardrail`) with setup.py
  - TypeScript SDK (`@myguardian/sdk`)
  - Docker images
  - Helm chart support

- **Documentation**
  - Comprehensive README with quickstart
  - SECURITY.md with threat model
  - CONTRIBUTING.md with guidelines
  - CODE_OF_CONDUCT.md
  - Integration examples
  - API documentation

### Changed

- Policy thresholds tuned for better paraphrase handling (faithfulness_min: 0.15, coverage_min: 0.60)
- Toxicity threshold lowered to 0.04 to catch emails (email score is 0.04)
- Repair now includes checklist-style reasoning

### Fixed

- Toxicity check now uses `>=` instead of `>` to properly catch threshold values
- PII redaction applied consistently across all log sinks
- CSV parsing handles JSON-encoded passages correctly

### Performance

- **SLO Targets:**
  - p95 Latency: < 500ms (verified with Prometheus)
  - Eval Pass Rate: ≥36/50 cases (72%)
  - Availability: 99.9% target (monitor with Prometheus)

### Security

- API keys required by default in docker-compose
- Rate limiting enabled by default
- Input size limits enforced (413 on violation)
- PII never logged (automatic redaction)
- No data retention (requests processed and discarded)

