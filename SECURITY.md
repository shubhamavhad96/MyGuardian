# Security Policy

## Data Handling

### PII Redaction
- All logs automatically redact PII (email, phone, SSN) using regex patterns
- Input fields are never echoed in logs
- Redaction is applied at the log sink level

### Data Retention
- **No data retention**: Request data is processed and discarded immediately
- No persistent storage of questions, answers, or passages
- Shadow mode analytics store only metadata (decision, scores, truncated text)

### Size Limits
- Maximum 50 passages per request
- Maximum 4KB per passage
- Maximum 200KB total request size
- Requests exceeding limits return 413 Payload Too Large

## API Security

### API Keys
- API keys are required by default (set via `GUARDRAIL_API_KEY`)
- Default key in docker-compose: `demo-key-change-in-production` (change in production!)
- Keys are validated on every request

### Rate Limiting
- Token bucket rate limiter using Redis
- Default: 100 requests per 60 seconds per IP
- Configurable via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SEC`
- Fails open if Redis is unavailable (logs warning)

### CORS
- CORS is disabled by default
- No cross-origin requests allowed unless explicitly configured

## Threat Model

| Threat | Mitigation | Status |
|--------|------------|--------|
| **Prompt Injection** | Heuristic detection via toxicity scoring | Implemented |
| **PII Leak** | Automatic blocking when PII detected (email, phone, SSN) | Implemented |
| **DoS via Large Payloads** | Size caps (50 passages, 4KB/passage, 200KB total) enforced via rate limiting | Implemented |
| **DoS via Rate Limits** | Token bucket rate limiting per IP (100 req/min default) | Implemented |
| **API Key Theft** | Keys required, validate on every request | Implemented |
| **Data Exfiltration** | No persistent storage, PII redaction in logs | Implemented |
| **Model Poisoning** | Input validation, size limits | Implemented |

## Reporting Security Issues

If you discover a security vulnerability, please report it via GitHub Issues with the "security" label, or email the maintainers directly.

Do not open public issues for security vulnerabilities.

## Security Best Practices

1. **Change default API key** in production
2. **Use HTTPS** in production (configure reverse proxy)
3. **Monitor rate limits** and adjust as needed
4. **Review shadow reports** regularly to identify risky queries
5. **Keep dependencies updated** (`pip install -r requirements.txt --upgrade`)

## Compliance Notes

- **GDPR**: No personal data stored; requests processed and discarded
- **HIPAA**: Not HIPAA-compliant out of the box; additional safeguards needed for PHI
- **SOC 2**: Requires additional audit logging and access controls

