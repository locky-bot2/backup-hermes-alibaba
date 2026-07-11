---
name: research-workflows
description: Academic paper discovery (arXiv + Semantic Scholar), persistent knowledge base building (Karpathy-style LLM wiki), and RSS/blog feed monitoring (blogwatcher) — all in one research umbrella.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, arxiv, papers, knowledge-base, wiki, rss, blog-monitoring]
    related_skills: [software-development-workflows, ocr-and-documents]
---

# Research Workflows

This umbrella covers three complementary research activities: finding academic papers, building a persistent knowledge base, and monitoring blogs/RSS feeds.

## Table of Contents

1. **[arXiv Paper Discovery](#1-arxiv-paper-discovery)** — search and retrieve papers via API
2. **[LLM Wiki Knowledge Base](#2-llm-wiki-knowledge-base)** — persistent, interlinked markdown wiki
3. **[Blogwatcher RSS Monitoring](#3-blogwatcher-rss-monitoring)** — track blog and feed updates

---

## 1. arXiv Paper Discovery

See `references/arxiv-paper-discovery.md` for full API reference.

**Quick commands:**
```bash
# Search
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5"

# Get specific paper metadata
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300"

# Read abstract
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Read full paper (PDF → markdown)
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Helper script (uses Python stdlib, no dependencies)
python scripts/search_arxiv.py "transformer attention" --max 10 --sort date
```

**Semantic Scholar** (citations, related papers, author profiles):
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,citationCount"
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=GRPO&limit=5"
```

**Rate limits:** arXiv ~1 req/3s, Semantic Scholar 1 req/s (100/s with API key).

---

## 2. LLM Wiki Knowledge Base

See `references/llm-wiki-knowledge-base.md` for the full methodology.

Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Build a persistent, interlinked markdown knowledge base.

### Architecture

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, tag taxonomy
├── index.md            # Content catalog with one-line summaries
├── log.md              # Chronological action log
├── raw/                # Layer 1: Immutable source material
├── entities/           # Layer 2: Entity pages
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
└── queries/            # Layer 2: Filed query results
```

Location: `$WIKI_PATH` env var (default: `~/wiki`). Works with Obsidian ([[wikilinks]], Dataview queries).

### Core Operations

| Operation | Action |
|-----------|--------|
| **Ingest** | Capture source → discuss takeaways → check existing pages → write/update → update index + log |
| **Query** | Read index → search for relevant pages → synthesize answer → file valuable ones |
| **Lint** | Orphans → broken wikilinks → index completeness → frontmatter → stale content → contradictions → tag audit |

### When to Use

Create a wiki page when entity/concept appears in 2+ sources or is central to one source. Don't create pages for passing mentions.

---

## 3. Blogwatcher RSS Monitoring

See `references/blogwatcher-rss.md` for full command reference.

**Installation:**
```bash
# Binary (Linux amd64)
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli
```

**Quick commands:**
```bash
blogwatcher-cli add "Blog Name" https://example.com
blogwatcher-cli scan
blogwatcher-cli articles
blogwatcher-cli read-all --yes
blogwatcher-cli blogs
```

**Features:** Auto-discovers RSS/Atom feeds, HTML scraping fallback, OPML import, read/unread management.