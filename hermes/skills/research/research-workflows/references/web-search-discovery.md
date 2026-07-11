# Web-Search-First arXiv Discovery

The arXiv REST API (export.arxiv.org) is great for precise queries, but for **discovering trending / hot papers from a specific time window (e.g. "past week")**, `web_search` often outperforms it — the API's XML output requires parsing and doesn't naturally reveal impact or topical relevance, while web search surfaces papers by recency and cross‑index signals.

## When to Use

- **Time-windowed queries:** "LLM fine-tuning papers from the past week"
- **Trending/high‑impact discovery:** you want papers people are talking about, not just matching keyword cold
- **One‑off research:** you don't want to write XML parsing, pagination, or date‑filter boilerplate
- **Topic discovery:** you're not sure of the exact arXiv category to target

## Workflow

### Step 1 — Broad Discovery

Start with a few broad web searches to surface candidate papers:

```
web_search(query="arxiv LLM fine-tuning papers 2026 June")
web_search(query="arxiv new 'fine-tuning' large language model June 2026")
```

Key query patterns that work well (tested June 2026):
- `arxiv <topic> <YYYY> <MM>` — broad temporal probe
- `arxiv <YYYYMM> fine-tuning LLM` — arXiv‑ID‑aware search (IDs encode YYMM)
- `site:arxiv.org 2606 "fine-tuning" LLM` — restricts to arXiv, June IDs
- `arxiv 2606.12 "fine-tuning" OR "SFT" OR "LoRA" LLM` — targets specific day range

Use multiple parallel queries to cover different angles (categories, keywords, recency).

### Step 2 — Extract Individual Paper Details

Once you have candidate arXiv IDs, get clean abstracts from each paper's page:

```
web_extract(urls=["https://arxiv.org/abs/2606.11206", "https://arxiv.org/abs/2606.13680"])
```

The extraction returns structured markdown with title, authors, submission date, full abstract, subjects, and comments. This is more readable than the API's raw XML.

### Step 3 — Verify Dates and Filter

arXiv IDs use YYMM format (e.g. 2606 = June 2026). Some papers may have been submitted earlier and only cross‑listed / updated recently. Check the actual `submitted` date from the extracted page — not just the arXiv ID prefix — to confirm it's within your target window.

### Step 4 — Compile and Format

Number the papers 1–N. For each include:

```
N. Full Paper Title
   Submitted: YYYY-MM-DD | Link: https://arxiv.org/abs/XXXX.XXXXX
   1-2 sentence summary of the key contribution from the abstract.
```

For cron‑job delivery, the prompt must be **fully self‑contained** — the cron context has no memory of previous conversations.

## Pitfalls

- **Search engine timeliness:** Web search indexes may lag a few hours behind arXiv submissions. For same‑day papers, prefer the API or `arxiv.org/list/cs.LG/recent`.
- **False positives from broader queries:** Papers about fine-tuning *anything* (segmentation models, diffusion models) will appear. Filter by checking subjects (cs.LG, cs.CL, cs.AI) or title context.
- **Version drift:** A paper may have been submitted earlier (v1 in April) but only received its 2606 ID in June via cross‑listing. The arXiv ID prefix (2606) is the *announcement* month, not the *submission* month. Always check the submission history line.
- **Cross‑listing duplicates:** The same paper may appear in cs.LG and cs.CL searches. Deduplicate by arXiv ID.
- **Rate limits:** web_search and web_extract are typically limited to 5–10 results per call. Batch multiple queries if you need broader coverage.
