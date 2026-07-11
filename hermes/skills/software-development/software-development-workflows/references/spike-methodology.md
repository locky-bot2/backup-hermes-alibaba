# Spike — Throwaway Experiments for Feasibility Validation

Use when validating an idea before committing to a real build. Spikes are disposable by design.

## Core Loop

```
decompose → research → build → verdict
```

## Step 1: Decompose

Break the idea into 2-5 independent feasibility questions. Each is one spike:

| # | Spike | Validates | Risk |
|---|-------|-----------|------|
| 001 | websocket-streaming | Client receives chunks <100ms | High |
| 002a | pdf-parse-pdfjs | Structured text extractable | Medium |
| 002b | pdf-parse-camelot | Structured text extractable | Medium |

Order by risk — the spike most likely to kill the idea runs first.

## Step 2: Research (before building)

1. Surface competing approaches as a table
2. Pick one, state why
3. Skip research for pure logic with no external deps

## Step 3: Build

One directory per spike: `spikes/NNN-descriptive-name/README.md + code`

Bias toward something the user can interact with: CLI with observable output > minimal HTML page > web server > unit test.

**Depth over speed.** Never declare "it works" after one happy-path run. Test edge cases.

## Step 4: Verdict

In each spike's README.md:

- **VALIDATED** — core question answered yes, with evidence
- **PARTIAL** — works under constraints X, Y, Z
- **INVALIDATED** — doesn't work (this is still a successful spike)

Include: what worked, what didn't, surprises, recommendation for real build.

**Comparison spikes:** Build variants back-to-back, then write a head-to-head comparison table.

## Pitfalls
- Spikes that take 2 days to "clean up for production" were bad spikes
- Keep code throwaway — hardcode everything, no complex package management