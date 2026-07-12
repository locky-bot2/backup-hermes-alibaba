---
name: backup-dr
description: "Backup strategies and disaster recovery planning for production infrastructure"
version: 1.0.0
author: Squirtle
platforms: [linux, macos]
metadata:
  squirtle:
    tags: [backup, disaster-recovery, data]
    team: squirtle
---

# Backup & Disaster Recovery

## The 3-2-1 Rule

> **3** copies of data, on **2** different media, with **1** copy off-site.

## Backup Strategies

| Type | Frequency | Retention | Use Case |
|------|-----------|-----------|----------|
| Full | Weekly | 3 months | Complete restore baseline |
| Incremental | Daily | 1 month | Changes since last backup |
| Differential | Daily | 2 weeks | Changes since last full |
| Point-in-time | Continuous | 7 days | Database rollback (WAL/Binlog) |

## Database Backup Patterns

- **PostgreSQL**: `pg_dump` (logical) or WAL archiving (physical, PITR)
- **MySQL**: `mysqldump` or binary log replication
- **SQLite**: `VACUUM INTO` for live backups
- **MongoDB**: `mongodump` or oplog replay

## Backup Automation

```bash
# Example cron: daily backup at 2am
0 2 * * * /usr/local/bin/backup.sh --type incremental --retention 30

# Verify backup integrity
backup.sh --verify /backups/latest
```

## DR Testing Schedule

| Test | Frequency | What to Verify |
|------|-----------|----------------|
| File restore | Monthly | Can we restore a single file? |
| DB restore | Quarterly | Data integrity after restore |
| Full DR | Yearly | Spin up entire stack from backup |

## Restore Verification

- Always verify: checksum → extract → integrity check → sample query
- Time your restores (RTO — Recovery Time Objective)
- Log restore results for audit trail
