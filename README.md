# Hermes Agent Backup - Alibaba VPS

Auto-backup of Hermes Agent running on Alibaba Cloud VPS.

## Contents
- `config.yaml` - Main configuration
- `SOUL.md` - Agent persona
- `hermes/` - Full Hermes home directory
  - `profiles/` - Subagent profiles (charmander, pikachu, squirtle)
  - `memories/` - USER.md, MEMORY.md
  - `skills/` - All skills
  - `cron/` - Cron job configs
  - `sessions/` - Session history
  - `scripts/` - Custom scripts
  - `state.db` - Session database
  - `kanban.db` - Kanban board
  - `gateway_state.json` - Gateway state

## Cron Schedule
- Weekly: Sunday 00:00 UTC

## Restore
```bash
git clone https://github.com/locky-bot2/backup-hermes-alibaba.git
cp backup-hermes-alibaba/hermes/* ~/.hermes/ -r
cp backup-hermes-alibaba/config.yaml ~/.hermes/config.yaml
```
