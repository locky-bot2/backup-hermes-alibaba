---
name: accessibility-testing
description: Accessibility testing with axe-core and WCAG compliance checks
author: Charmander
tags: [testing, a11y, accessibility]
team: charmander
---

# Accessibility Testing (a11y)

Skill for performing accessibility audits on web applications, enforcing WCAG 2.1 compliance, and integrating automated tooling into CI/CD pipelines.

## Tooling

### axe-core
The industry-standard accessibility testing engine. Use via:
- **@axe-core/cli** – standalone CLI for auditing single pages or crawl-based scans.
- **@axe-core/playwright** / **@axe-core/puppeteer** – programmatic injection into browser automation.
- **axe DevTools** – browser extension for interactive debugging.

```bash
# CLI example
npx axe https://example.com --exit --tags wcag2a,wcag2aa
```

### Lighthouse
Built into Chrome DevTools and ChromeDriver. Provides an accessibility score, a list of passed/failed audits, and guidance for remediation.

```bash
npx lighthouse https://example.com --only-categories=accessibility --output=json --chrome-flags="--headless"
```

### Pa11y
Lightweight, configurable CI-friendly accessibility checker with support for custom WCAG levels, HTML reporting, and action sequences (click, login, etc.).

```bash
# CLI example
npx pa11y https://example.com --standard WCAG2AA --reporter json
```

## WCAG 2.1 Levels

| Level | Description | Enforcement |
|-------|-------------|-------------|
| **A** | Minimum – must be satisfied or content is inaccessible to some users. | Baseline requirement; highest-impact issues. |
| **AA** | Recommended – removes significant barriers for most users. | Target for virtually all production sites. |
| **AAA** | Highest – improves usability for all users. | Often aspirational; not required by most regulations. |

### Key WCAG 2.1 Principles (POUR)

1. **Perceivable** – Information must be presentable to users (alt text, captions, adaptable layouts).
2. **Operable** – UI components must be usable (keyboard access, enough time, no seizures).
3. **Understandable** – Content and UI must be readable (clear language, predictable behavior, input assistance).
4. **Robust** – Content must be interpretable by a wide variety of user agents (valid markup, accessible names).

## Automated vs Manual Checks

| Aspect | Automated Checks | Manual Checks |
|--------|-----------------|---------------|
| **Scope** | Programmatic rules (axe-core ruleset, ~50+ checks) | Human judgment (usability, content clarity) |
| **Catches** | Missing alt text, color contrast, ARIA misuse, duplicate IDs, missing labels, focus order | Keyboard trap logic, screen reader flow, cognitive load, complex widget semantics |
| **False positives/negatives** | Low false positives; moderate false negatives (misses ~30% of real issues) | High accuracy but time-consuming |
| **CI integration** | Trivial (exit codes, JSON output, threshold gates) | Requires manual QA sign-off |
| **Recommended workflow** | Run **automated** on every PR, block merge on new violations | Schedule **manual** passes before each release |

## Common Violations to Catch

### Color & Contrast
- **color-contrast** – Text/background contrast ratio below 4.5:1 (AA normal) or 3:1 (AA large).
- **link-in-text-block** – Links distinguishable by more than colour alone (need underline or icon).

### Images & Non-Text Content
- **image-alt** – Missing or empty alt attributes on meaningful `<img>` tags.
- **aria-hidden-focus** – Focusable elements inside `aria-hidden="true"`.

### Forms & Labels
- **label** – Form inputs missing associated `<label>` or `aria-label`.
- **input-button-name** – Buttons or inputs without accessible names.
- **duplicate-id** – Duplicate `id` attributes break label/ARIA associations.

### ARIA & Landmarks
- **aria-allowed-attr** – ARIA attributes used on elements that don't support them.
- **aria-roles** – Invalid or misapplied ARIA roles.
- **landmark-one-main** / **region** – Missing or multiple `<main>` / banner / contentinfo landmarks.

### Keyboard & Focus
- **tabindex** – Positive `tabindex` values disrupt expected focus order.
- **scrollable-region-focusable** – Scrollable containers not keyboard-accessible.

### Structure & Semantics
- **heading-order** – Skipping heading levels (e.g., `h1` -> `h3`).
- **list** – `ul`/`ol` containing non-`li` children or vice versa.
- **html-has-lang** – `<html>` element missing a `lang` attribute.

### Document & Navigation
- **document-title** – Missing `<title>` element.
- **bypass** – Missing skip-navigation link.

## Workflow Integration

1. **PR Gate (automated)**: Run axe-core via Playwright on key routes. Exit non-zero if any violations of **Level AA**.
2. **Nightly (automated + manual)**: Lighthouse score threshold > 90; Pa11y reports archived. Manual review of flagged pages.
3. **Release Sign-off**: Full manual audit covering screen reader (NVDA/VoiceOver), keyboard-only navigation, zoom (200%), and forced-colors mode.

## References

- [WCAG 2.1 Specification](https://www.w3.org/TR/WCAG21/)
- [axe-core Rule Descriptions](https://dequeuniversity.com/rules/axe/)
- [Lighthouse Accessibility Scoring](https://developer.chrome.com/docs/lighthouse/accessibility/scoring)
- [Pa11y Documentation](https://pa11y.org/)
