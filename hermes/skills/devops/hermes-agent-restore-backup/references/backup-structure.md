# Backup Structure Reference

This document describes the structure of the `locky-bot2/hermes-backup` repository restored on 2026-07-11.

## Root Files

| File | Purpose | Size |
|------|---------|------|
| `config.yaml` | Main Hermes Agent configuration | 14.6 KB |
| `config.yaml.bak-20260612T235908Z` | Previous config backup | 64 KB |
| `kanban.db` | Kanban task database | 114.6 KB |
| `response_store.db` | Response cache database | 20.4 KB |
| `response_store.db-shm` | SQLite shared memory | 32 KB |
| `response_store.db-wal` | SQLite write-ahead log | 0 bytes |
| `models_dev_cache.json` | Model provider cache | 2.3 MB |
| `gateway_state.json` | Gateway connection state | 506 bytes |
| `channel_directory.json` | Channel mapping | 724 bytes |
| `workspace-sessions.json` | Workspace session tracking | 417 bytes |
| `SOUL.md` | Agent identity document | 536 bytes |

## Directories

| Directory | Contents |
|-----------|----------|
| `profiles/` | Subagent profile configurations |
| `sessions/` | Chat session history JSON files |
| `memories/` | User memories and profile data |
| `cron/` | Scheduled cron job configurations |
| `scripts/` | Custom shell/Python scripts |
| `skills/` | Personal and shared skills |
| `plugins/` | Plugin configurations |
| `.hermes/` | Agent-installed configuration (scripts) |
| `webui-mvp/` | Web UI development files |

## Profile Structure

Each profile directory contains:

```
profiles/<name>/
├── config.yaml          # Profile-specific config
└── skills/              # Profile-specific skills (optional)
    └── <skill-name>/
        └── SKILL.md
```

## Profile Details from This Backup

### charmander (QA/Test Specialist)
- **Model**: deepseek/deepseek-v4-flash
- **Provider**: openrouter
- **Purpose**: Integration and E2E testing
- **Focus**: Write tests that catch what unit tests miss

### pikachu (Software Developer)
- **Model**: deepseek/deepseek-v4-flash
- **Provider**: (empty - uses default)
- **Purpose**: Code implementation
- **Focus**: Production code with 80%+ test coverage
- **Workflow**: Branch → PR →Ash reviews

### squirtle (DevOps Engineer)
- **Model**: deepseek/deepseek-v4-flash
- **Provider**: openrouter
- **Purpose**: Deployment and infrastructure
- **Focus**: Docker, Cloud Run, K8s, CI/CD

## Session Files

Session files are named `session_<timestamp>_<hash>.json` and include:
- Full conversation history
- Tool calls and results
- Session metadata

## Memory Files

- `USER.md` - User profile information
- `MEMORY.md` - General knowledge and facts

## Cron Jobs

 Stored in `jobs.json` with:
- Schedule configuration
- Associated skills
- Task prompts

## Notes

- This backup was created from a working Hermes Agent installation
- No `.env` file is included (contains sensitive credentials)
- No `auth.json` is included (contains API keys)
- The `hermes-agent` application itself is not included
- Database files are SQLite with separate `-shm` and `-wal` files

## Real-World Backup Artifacts

Backup repos may also contain items that are NOT Hermes config but were swept up by a whole-home-directory backup:

### HOME Dotfiles at Root Level

Files like `.bash_logout`, `.bashrc`, `.profile`, `.gitignore`, `.install_method`, `.scratch_tip_shown` at the backup root are HOME directory artifacts — not `~/.hermes/` items. They appear when the backup script ran something like `tar -czf` on the entire `~/` directory. Copy them to `~/` if restoring a full environment, otherwise skip.

### `.hermes/` Subdirectory

A `.hermes/` subdirectory inside the backup root (path: `.hermes/scripts/weather-app-finish.sh`) corresponds to `~/.hermes/.hermes/` on the original server — a nested directory within the Hermes config home, not a duplicate of the main config. Usually contains agent-installed scripts only.

### Skill Reorganization Across Versions

Some skills in older backups may map to different paths in newer Hermes versions:
- `github/github/` → split into `github/github-auth/`, `github/github-pr-workflow/`, `github/github-code-review/`, etc.
- `autonomous-ai-agents/autonomous-coding-agents/` → individual `claude-code/`, `codex/`, `opencode/`
