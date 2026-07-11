# Authoring In-Repo Skills (Hermes-Agent Project)

When contributing to the Hermes Agent repo itself (not your personal `~/.hermes/skills/`), skills live under `skills/<category>/<name>/SKILL.md`. Use `write_file` + `git add` — NOT `skill_manage(action='create')` which targets user-local skills.

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`.

- File starts with `---` as first bytes (no leading blank line or BOM)
- Closes with `\n---\n` before the body
- `name` field ≤ 64 chars, lowercase + hyphens
- `description` field ≤ 1024 chars, starts with "Use when ..."
- Non-empty body after closing `---`

```yaml
---
name: my-skill-name
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill]
---
```

`version` / `author` / `license` / `metadata` are peer conventions, not validator-enforced.

## Size Limits

- Description: ≤ 1024 chars (enforced)
- Full SKILL.md: ≤ 100,000 chars (~36k tokens)
- Target 8-14k chars. Over 20k → split into `references/*.md`

## Directory Placement

```
skills/<category>/<name>/SKILL.md
```

Existing categories: `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `email`, `github`, `media`, `mlops/*`, `note-taking`, `productivity`, `research`, `smart-home`, `social-media`, `software-development`. Pick the closest; don't invent new ones casually.

## Peer-Matched Structure

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections>
- Quick-reference tables
- Code blocks with exact commands
- Hermes-specific recipes

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications
```

## Workflow

1. Survey peers in target category with `ls skills/<category>/`
2. Validate locally:
   ```python
   import yaml, re, pathlib
   c = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert c.startswith("---")
   m = re.search(r'\n---\s*\n', c[3:])
   fm = yaml.safe_load(c[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024 and len(c) <= 100_000
   ```
3. `git add skills/<category>/<name>/ && git commit`

## Cross-Referencing

`metadata.hermes.related_skills` unions both `skills/` (in-repo) and `~/.hermes/skills/` at load time. Prefer only in-repo references from in-repo skills so they resolve for other clones.

## Editing Existing In-Repo Skills

- Small fix → `skill_manage(action='patch')` works on in-repo skills
- Major rewrite → `write_file` the whole SKILL.md
- Supporting files → `write_file` to `references/`, `templates/`, or `scripts/`

## Pitfalls

1. **`skill_manage(action='create')` writes to `~/.hermes/skills/`, not the repo tree.** Use `write_file` for in-repo creation.
2. **Leading whitespace before `---`** fails the `startswith("---")` check.
3. **Current session won't see the new skill** — the loader is cached at session start.
4. **Duplicating peers** — always survey existing skills in the category first.