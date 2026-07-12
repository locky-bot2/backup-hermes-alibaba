---
name: monitoring
description: "Observability stack setup: metrics, logging, tracing, and alerting"
version: 1.0.0
author: Squirtle
platforms: [linux, macos]
metadata:
  squirtle:
    tags: [monitoring, observability, prometheus, grafana]
    team: squirtle
---

# Monitoring & Observability

## Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics | Prometheus | Time-series collection |
| Dashboards | Grafana | Visualization + alerting |
| Logging | Structured JSON → stdout | Centralized log aggregation |
| Tracing | OpenTelemetry | Distributed request tracing |
| Uptime | Health check endpoints | Liveness/readiness probes |

## Health Check Endpoints

```
GET /health      → {"status": "ok"}                          # Liveness
GET /health/ready → {"status": "ok", "deps": {"db": "ok"}}   # Readiness
```

- Always return 200 for healthy, 5xx for unhealthy
- Readiness checks downstream dependencies (DB, cache, API)
- Include version and uptime metadata

## Structured Logging Pattern

```json
{"level": "info", "ts": "2026-07-11T10:00:00Z", "msg": "request completed",
 "method": "GET", "path": "/api/users", "status": 200, "duration_ms": 45,
 "request_id": "abc-123", "user_id": "u-456"}
```

- Always include: level, timestamp, message, request_id
- Never log sensitive data (PII, tokens, passwords)
- Use structured format (JSON), not free-text

## Alerting Rules

- P0: Service down — notify immediately
- P1: Latency > 1s p99 — notify within 5min
- P2: Error rate > 1% — notify within 15min
- P3: Disk > 80% — daily digest

## Cost Monitoring

- Tag all resources (project, team, environment)
- Set budget alerts at 50%, 80%, 100%
- Review unused resources monthly
