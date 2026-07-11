# Cron + Telegram Weekly arXiv Digest

Real session transcript of setting up a weekly arXiv paper digest delivered to Telegram.

## User Request

"Setup cron job to pull top 5 LLM fine-tuning papers from arXiv and send every Saturday morning 8am Hsinchu Taiwan time to my Telegram. Paper title, date, and references link."

## Steps Taken

1. **Check Telegram is connected.** Search gateway logs for `telegram connected` and note the chat ID from inbound messages (`chat=1508030749`). The user's Telegram username was "Lock Abraham" with chat ID 1508030749.

2. **Run a test first.** Create a one-shot cron job:
   ```
   cronjob action=create deliver='telegram:CHAT_ID' name='Test Digest'
          prompt='Search arXiv for the 5 most recent papers about LLM fine-tuning...'
          repeat=1 schedule='1m'
   ```
   The `deliver='telegram:CHAT_ID'` setting makes the cron output go directly to the user's Telegram DM.

3. **Wait or trigger manually.** The scheduler may take 30-60s to fire a `1m` job. Use `cronjob action=run job_id=...` to force immediate execution if needed.

4. **Verify delivery.** Check agent.log for line: `delivered to telegram:CHAT_ID via live adapter`

5. **Remove test job after approval.** `cronjob action=remove job_id=...`

6. **Create the recurring job:**
   ```
   cronjob action=create
          deliver='telegram:1508030749'
          name='Weekly LLM Fine-Tuning Papers'
          prompt='Search arXiv for the most recent papers about LLM fine-tuning from the past week. Pick the top 5. For each paper include: title, submission date, a short 1-2 sentence summary of the abstract, and the arXiv link.'
          schedule='0 0 * * 6'
   ```
   Schedule `0 0 * * 6` = midnight UTC Saturday = 8:00 AM Taiwan time (UTC+8).

## User-Approved Output Format

```
1. Paper Title Here
   Published: 2026-06-11 | Link: https://arxiv.org/abs/2606.XXXXX
   One or two sentence summary of the key contribution.

2. Next Paper Title
   Published: 2026-06-10 | Link: https://arxiv.org/abs/2606.XXXXX
   Brief summary...
```

## Key Details

- Telegram chat ID: `1508030749` (user: Lock Abraham) — found in gateway logs as `chat=1508030749`
- arXiv search works well with `web_search` or `web_extract` on the arXiv search page
- For individual paper details, `web_extract(urls=["https://arxiv.org/abs/ID"])` returns structured markdown with title, date, authors, abstract
- The prompt for the cron job must be **fully self-contained** — cron runs in isolated context with no conversation history