---
name: github
description: Complete GitHub lifecycle: auth setup, repo management, PR workflow, code review, issues, codebase inspection, releases, CI, secrets, and GitHub Actions — all in one umbrella.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Git, Pull-Requests, Code-Review, Issues, Releases, CI, Automation, Auth]
    related_skills: [hermes-agent, plan]
---

# GitHub — Complete Workflow

This umbrella covers the full GitHub lifecycle: authentication, repo management, PRs, code review, issues, CI, releases, secrets, codebase inspection, and more. Each area has detailed references linked below.

## Quick Setup (Auth Detection)

```bash
# Determine auth method
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="curl"
  if [ -z "$GITHUB_TOKEN" ]; then
    _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"
    if [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -n "$REMOTE_URL" ]; then
  OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\\.com[:/]||; s|\\.git$||')
  OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
  REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
fi
```

## Table of Contents

1. **[Authentication](#1-authentication)** — HTTPS tokens, SSH, gh CLI
2. **[Repository Management](#2-repository-management)** — clone, create, fork, settings, releases
3. **[Pull Request Workflow](#3-pull-request-workflow)** — branch, commit, PR, CI, merge
4. **[Code Review](#4-code-review)** — local and PR review, inline comments, approve/request-changes
5. **[Issues](#5-issues)** — create, triage, label, assign, close
6. **[CI & Actions](#6-ci--actions)** — workflows, runs, logs, reruns
7. **[Secrets & Gists](#7-secrets--gists)** — GitHub Actions secrets, gists
8. **[Branch Protection](#8-branch-protection)** — API setup
9. **[Codebase Inspection](#9-codebase-inspection)** — lines of code, language breakdown
10. **[Troubleshooting & Pitfalls](#10-troubleshooting--pitfalls)** — common issues

---

## 1. Authentication

See `references/github-auth.md` for full details including SSH keys, HTTPS tokens, gh CLI auth, token discovery from .env files, and credential helpers.

**Quick decision tree:**
- `gh auth status` works → use `gh` for everything
- `gh` installed but not authed → `gh auth login` or token injection
- No `gh` → git + curl with personal access token

## 2. Repository Management

See `references/github-repo-management.md` for: cloning, creating repos, forking, repo settings, releases, actions workflow management, and gists.

**Quick reference:**

| Action | gh | curl |
|--------|-----|------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create | `gh repo create name --public --clone` | `POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `POST /repos/o/r/forks` + clone |
| Release | `gh release create v1.0` | `POST /repos/o/r/releases` |
| Workflows | `gh workflow list` | `GET /repos/o/r/actions/workflows` |

See `templates/push-existing-project.sh` for pushing an existing local directory to a new GitHub repo.

## 3. Pull Request Workflow

See `references/github-pr-workflow.md` for: branching conventions, commit messages, PR creation, CI monitoring, auto-fix loop, merging, and auto-merge via GraphQL.

**Branch naming:** `feat/`, `fix/`, `refactor/`, `docs/`, `ci/` prefixes.

**Commit format (Conventional Commits):**
```
type(scope): short description

Longer explanation.
```
Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

**PR body templates:** `templates/pr-body-feature.md`, `templates/pr-body-bugfix.md`

## 4. Code Review

See `references/github-code-review.md` for: reviewing local changes pre-push, reviewing PRs on GitHub, inline comments, formal reviews (approve/request-changes/comment), and the full review checklist (correctness, security, code quality, testing, performance, docs).

**Quick checks:**
```bash
git diff main...HEAD --stat           # scope
git diff main...HEAD | grep -n "TODO\|FIXME\|breakpoint\|debugger"  # left-behind markers
```

## 5. Issues

See `references/github-issues.md` for: creating, viewing, triaging, labeling, assigning, commenting, closing/reopening issues. Full bug report and feature request templates in `templates/bug-report.md` and `templates/feature-request.md`.

**Issue linking in PRs:**
```markdown
Closes #42
Fixes #42
Resolves #42
```

## 6. CI & Actions

**With gh:**
```bash
gh pr checks --watch              # monitor CI
gh run list --branch main         # recent runs
gh run view <RUN_ID> --log-failed # failed logs
gh run rerun <RUN_ID>             # rerun
gh workflow run ci.yml --ref main # trigger dispatch
```

**With curl:**
```bash
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=5"
```

## 7. Secrets & Gists

**Secrets (`gh secret`):**
```bash
gh secret set API_KEY --body "value"
gh secret list
gh secret delete API_KEY
```

**Gists:**
```bash
gh gist create script.py --public --desc "description"
gh gist list
```

## 8. Branch Protection

```bash
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{
    "required_status_checks": {"strict": true, "contexts": ["ci/test"]},
    "required_pull_request_reviews": {"required_approving_review_count": 1}
  }'
```

## 9. Codebase Inspection

See `references/codebase-inspection.md` for pygount-based lines-of-code analysis with language breakdowns and folder exclusion patterns.

```bash
pygount --format=summary --folders-to-skip=".git,node_modules,venv" .
```

## 10. Troubleshooting & Pitfalls

| Problem | Solution |
|---------|----------|
| `git push` asks for password | Use personal access token or SSH — GitHub disabled password auth |
| `Permission to X denied` | Token lacks `repo` scope |
| `.git/` owned by different user | `sudo chown -R user:group .git` or use plumbing workaround |
| `git init` defaults to `master`, GitHub wants `main` | `git branch -M main` before pushing |
| Token embedded in remote URL is unrecoverable | Keep token in .env, not the git config |
| execute_code env sandboxing hides GITHUB_TOKEN | Read parent env: `python3 -c "import os; print(dict(os.environ))"` |
| Branch name mismatch | `git branch -M main` |
| `gh: command not found` | Use git + curl fallback methods instead |