When diagnosing Hermes issues through the API server, execute_code is blocked by approvals.mode: manual. The approval prompt goes to the user via API but their response doesn't unblock the pending call. Use file-only tools (read_file, search_files, web_extract) for diagnosis, then give the user exact terminal commands to run, or suggest they temporarily run `hermes config set approvals.mode off` to let diagnostics run. Never retry execute_code more than 2 times.
§
Hermes Workspace (outsourc-e/hermes-workspace) is a visual web UI for Hermes Agent — chat, memory, skills, terminal, multi-agent ops. Points at :8642 (gateway) + :9120 (dashboard direct, not :9119 nginx). Uses CLAUDE_API_URL/CLAUDE_DASHBOARD_URL env vars. Vite dev mode needs >1.8GB RAM.
§
When execute_code or skill tools hit approval/permission walls, give the user the exact terminal command to run rather than retrying the tool multiple times. User prefers self-service when automation hits limits.
§
Subagent delegation pattern: subagents (via delegate_task) CAN write files but CANNOT run terminal commands or execute_code. For any task requiring shell execution (git push, npm build, deploy scripts), the subagent writes a self-contained script via write_file, then the parent agent runs it (bash script.sh). This is a fundamental tool constraint, not an environment issue. Pass the 'terminal' + 'file' toolsets to subagents so they can write scripts.
§
Cron Telegram delivery: use deliver='telegram:CHAT_ID' (chat ID from gateway logs). Schedule UTC: Taiwan UTC+8 Sat 8am = '0 0 * * 6'. Test with repeat=1 + '1m' before recurring. Always remove test jobs. Cron prompts must be fully self-contained.
§
Backup: github.com/locky-bot2/backup-hermes-alibaba (Alibaba VPS). Local clone at /home/admin/backup-hermes-alibaba/. Cron job "Hermes VPS Weekly Backup - Alibaba" (id: 8155942596b5): Sun 00:00 UTC, script=backup.sh, workdir=/home/admin/backup-hermes-alibaba, no_agent=True. GITHUB_TOKEN in ~/.bashrc + ~/.git-credentials.