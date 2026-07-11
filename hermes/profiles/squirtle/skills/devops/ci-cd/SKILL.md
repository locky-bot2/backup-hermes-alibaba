---
name: ci-cd
description: "Set up GitHub Actions CI/CD pipelines for build, test, deploy"
version: 1.0.0
author: Squirtle
platforms: [linux, macos]
metadata:
  squirtle:
    tags: [github-actions, ci, cd, pipeline]
    team: squirtle
---

# CI/CD Pipeline Workflow

Set up GitHub Actions to automate build → test → deploy.

## Pipeline Stages

### On PR (pre-merge)
```
lint → build → unit tests → integration tests
```
Runs on every PR. Blocks merge on failure.

### On Merge to Main (post-merge)
```
build → docker build → push to registry → deploy
```
Triggers automatically when Ash merges.

## GitHub Actions Workflow Template

```yaml
name: CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=src

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          # docker build & push
          # gcloud run deploy or kubectl apply
```

## Pipeline Rules

- Tests must pass before deploy
- Build once, promote the same artifact through environments
- Tag docker images with git commit SHA
- Notify Ash on failure