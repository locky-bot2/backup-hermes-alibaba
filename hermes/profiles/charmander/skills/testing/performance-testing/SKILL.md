---
name: performance-testing
description: "Load and performance testing with k6/Playwright"
version: 1.0.0
author: Charmander
platforms: [linux, macos]
metadata:
  charmander:
    tags: [testing, performance, load, k6]
    team: charmander
---

# Performance Testing Workflow

Load and performance testing to validate speed, scalability, and reliability under stress.

## Tooling Recommendations

### **k6** — Primary Load Testing Tool
- JavaScript-based scripting, CLI-native, low overhead
- Supports HTTP/1.1, HTTP/2, WebSocket, gRPC
- Run: `k6 run --vus 10 --duration 30s script.js`
- Use **k6-html-report** for friendly output
- Integrate with CI via `k6 cloud` or Grafana dashboards

### **Lighthouse** — Frontend Audits
- Run via CLI: `lighthouse <url> --output=html --output-path=./report.html`
- Use **Lighthouse CI** (`lhci`) for regression gates
- Tracks LCP, TBT, CLS, SI, and accessibility scores
- Automate in CI with `lighthouse-ci` GitHub Action

### **Playwright Tracing** — Debug Performance
- Enable tracing in Playwright tests:
  ```js
  await context.tracing.start({ screenshots: true, snapshots: true });
  // ... test steps ...
  await context.tracing.stop({ path: 'trace.zip' });
  ```
- Open trace viewer: `npx playwright show-trace trace.zip`
- Use to spot slow API calls, excessive re-renders, network waterfalls

### **Additional Tools**
- **autocannon** — quick HTTP benchmark (`npx autocannon -c10 -d10 <url>`)
- **WebPageTest** — free cloud-based waterfall analysis
- **Grafana k6** — real-time metrics streaming for advanced analysis

## Performance Budgets

| Metric | Budget | Source |
|--------|--------|--------|
| **LCP** (Largest Contentful Paint) | < 2.5 s | Lighthouse, Web Vitals |
| **TTI** (Time to Interactive) | < 3.5 s | Lighthouse |
| **TBT** (Total Blocking Time) | < 200 ms | Lighthouse |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Lighthouse |
| **API p95 response time** | < 500 ms | k6 |
| **Error rate** | < 1% | k6 |
| **Throughput (requests/sec)** | >= target SLA | k6 |

> Fail CI if any budget is exceeded. Store baseline in `lighthouse-budget.json` or `k6-options.js`.

## Load Testing Patterns

### 1. Smoke Test (1–2 VUs)
Validate script works and system responds.
```js
export let options = { vus: 1, duration: '1m' };
```

### 2. Load Test (target avg traffic)
Simulate expected daily traffic over 10–15 minutes.
```js
export let options = {
  stages: [
    { duration: '2m', target: 50 },   // ramp-up
    { duration: '5m', target: 50 },   // steady
    { duration: '2m', target: 0 },    // ramp-down
  ],
};
```

### 3. Stress Test (2x–5x peak)
Find breaking point — ramp until errors or degradation.
```js
export let options = {
  stages: [
    { duration: '3m', target: 100 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },
    { duration: '2m', target: 0 },
  ],
  thresholds: { http_req_failed: ['rate<0.05'] },
};
```

### 4. Soak Test (extended duration)
Detect memory leaks / resource exhaustion over 1–8 hours.
```js
export let options = {
  stages: [
    { duration: '5m', target: 50 },
    { duration: '120m', target: 50 },
    { duration: '5m', target: 0 },
  ],
};
```

### 5. Spike Test (sudden burst)
Test auto-scaling and recovery.
```js
export let options = {
  stages: [
    { duration: '30s', target: 0 },
    { duration: '10s', target: 500 },   // instant spike
    { duration: '2m', target: 500 },
    { duration: '30s', target: 0 },
  ],
};
```

## k6 Script Template

```js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');

export let options = {
  thresholds: {
    errors: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

export default function () {
  let res = http.get('https://example.com/api/health');
  check(res, { 'status is 200': (r) => r.status === 200 });
  errorRate.add(res.status !== 200);
  apiLatency.add(res.timings.duration);
  sleep(1);
}
```

## Reporting Format

Every performance test run **must** produce a structured report saved as JSON, HTML, or both.

### Required Report Fields

```json
{
  "meta": {
    "test_name": "api-load-test",
    "timestamp": "2026-07-11T12:00:00Z",
    "environment": "staging",
    "pattern": "load-test",
    "duration_sec": 600
  },
  "summary": {
    "total_requests": 30000,
    "passed": 29850,
    "failed": 150,
    "error_rate_pct": 0.5,
    "avg_rps": 50
  },
  "latency": {
    "p50_ms": 120,
    "p90_ms": 310,
    "p95_ms": 450,
    "p99_ms": 890,
    "max_ms": 2100
  },
  "budgets": {
    "p95_latency_budget": 500,
    "p95_passed": true,
    "error_rate_budget": 1.0,
    "error_rate_passed": true
  },
  "lighthouse": {
    "lcp_score": 0.92,
    "lcp_ms": 2100,
    "tti_ms": 3100,
    "cls": 0.05,
    "tbt_ms": 150,
    "performance_score": 89
  }
}
```

### Artifacts to Archive
- `k6-summary.json` — k6 JSON output
- `lighthouse-report.html` — full Lighthouse audit
- `trace.zip` — Playwright trace (if debugging a specific journey)
- `thresholds-passed.txt` — boolean summary for CI gating

## CI Integration

- Run performance tests in a dedicated staging or isolated environment
- Fail pipeline if any budget threshold is exceeded
- Store historical results (e.g., S3, InfluxDB, or a metrics store) for trend analysis
- Alert the team via Slack/email when degradation > 10% compared to last baseline

## When to Run

- Before every production release
- After infrastructure changes (scaling, migrations, deploys)
- After significant code changes (new endpoints, data-intensive features)
- Monthly soak tests for long-running stability
- On demand when Charmander or Ash flags a regression
