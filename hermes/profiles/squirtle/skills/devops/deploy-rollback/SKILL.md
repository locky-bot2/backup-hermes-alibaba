---
name: deploy-rollback
description: "Deploy to production and verify health checks, roll back on failure"
version: 1.0.0
author: Squirtle
platforms: [linux, macos]
metadata:
  squirtle:
    tags: [deploy, rollback, health-check]
    team: squirtle
---

# Deploy & Rollback Workflow

Deploy after Ash merges, verify it's healthy, roll back if it's not.

## Deployment Steps

1. **Pull latest** — `git checkout main && git pull`
2. **Build** — compile / bundle / build the artifact
3. **Docker image** — build multi-stage image with commit SHA tag
4. **Push** — push image to container registry
5. **Deploy** — `gcloud run deploy` or `kubectl apply` or `helm upgrade`
6. **Wait** — allow time for pods/services to start
7. **Verify** — run health check against the new deployment

## Health Checks

- HTTP 200 on health endpoint (`/health` or `/ready`)
- Response time under 2 seconds
- Database connection established
- No 5xx errors in the first 60 seconds post-deploy

## Rollback Trigger

Roll back immediately if any health check fails.

## Rollback Steps

1. **Identify previous healthy version** — last working image SHA
2. **Deploy the previous version** — `gcloud run deploy --image=<previous-sha>`
3. **Verify** — run health checks again
4. **Flag Ash** — report what went wrong and what was rolled back

## Reporting

```
Deploy Complete
===============
Version:    [commit SHA]
Target:     [environment]
Health:     [pass / fail]
Rollback:   [yes / no]

Details:
[any errors or observations]
```