# Provider Model Name Troubleshooting

## The Vendor-Prefix Problem

OpenRouter and similar aggregators use a `provider/model` naming convention (e.g., `deepseek/deepseek-v4-flash`, `anthropic/claude-sonnet-4`, `openai/gpt-4o`). When you switch to a direct provider API, **the vendor prefix must be stripped**.

### Correct model names by provider type

| Provider type | Example model | Correct for... |
|--------------|---------------|----------------|
| Aggregator (OpenRouter) | `deepseek/deepseek-v4-flash` | openrouter |
| Direct API | `deepseek-v4-flash` | deepseek |
| Direct API | `claude-sonnet-4` | anthropic |
| Direct API | `gpt-4o` | openai |

### How it breaks

With `model.default: deepseek/deepseek-v4-flash` and `model.provider: deepseek`:
- `hermes doctor` warns about vendor-prefixed model with non-aggregator provider
- Gateway fails with: "RuntimeError: No LLM provider configured"
- The error message is misleading — the provider exists and is configured, the model name is just wrong

### Fix

```bash
# 1. Run doctor --fix to clean up stale root-level keys first
hermes doctor --fix

# 2. Strip the vendor prefix from main config
sed -i 's|  default: deepseek/|  default: |' ~/.hermes/config.yaml

# 3. Same for all profile configs
for p in ~/.hermes/profiles/*/config.yaml; do
  sed -i 's|^model: deepseek/|model: |' "$p"
done

# 4. Update base_url for the direct provider
hermes config set model.base_url https://api.deepseek.com

# 5. Restart gateway
hermes gateway restart
```

### Same pattern for other providers

| Old (OpenRouter format) | New (Direct format) | Direct provider |
|------------------------|--------------------|-----------------|
| `anthropic/claude-sonnet-4` | `claude-sonnet-4` | `anthropic` |
| `openai/gpt-4o` | `gpt-4o` | `openai` |
| `google/gemini-2.5-pro` | `gemini-2.5-pro` | `google` |

### Diagnosis

If the gateway connects but agent calls fail with "No LLM provider configured", run:

```bash
hermes doctor | grep "vendor-prefixed"
```
