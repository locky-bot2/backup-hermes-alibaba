---
name: containerization
description: "Build multi-stage Dockerfiles and deploy to Cloud Run / Kubernetes"
version: 1.0.0
author: Squirtle
platforms: [linux, macos]
metadata:
  squirtle:
    tags: [docker, container, deployment]
    team: squirtle
---

# Containerization Workflow

Package applications into production-ready containers.

## Multi-Stage Dockerfile Pattern

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Best Practices

- Use distroless or slim base images where possible
- Pin base image versions (no `:latest`)
- Minimize layers (combine RUN commands)
- Run as non-root user
- Add HEALTHCHECK instruction
- Label with `maintainer`, `version`, `git-commit`

## Deployment Targets

- **Cloud Run** — for stateless HTTP services
- **Kubernetes** — for stateful or complex deployments
- Deploy after Ash merges the PR