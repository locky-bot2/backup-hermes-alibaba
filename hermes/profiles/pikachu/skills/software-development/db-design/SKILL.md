---
name: db-design
description: "Database design patterns, schema best practices, and query optimization"
version: 1.0.0
author: Pikachu
platforms: [linux, macos]
metadata:
  pikachu:
    tags: [database, schema, sql]
    team: pikachu
---

# Database Design

## Normalization Principles

- **1NF**: Atomic columns, no repeating groups
- **2NF**: No partial dependencies on composite keys
- **3NF**: No transitive dependencies
- Denormalize only when query performance requires it (document trade-off)

## Indexing Strategy

| Index Type | When to Use |
|------------|-------------|
| B-tree | Default, equality + range queries |
| Hash | Equality lookups only |
| GIN | Array/JSON search (PostgreSQL) |
| Composite | Multi-column filters (order matters) |
| Partial | Filtered subset of rows |
| Covering | Include all queried columns (index-only scan) |

**Rules:**
- Index foreign keys and frequent WHERE columns
- Avoid over-indexing (write penalty)
- Use `EXPLAIN ANALYZE` to verify index usage
- Monitor slow query log

## Migration Patterns

```sql
-- Always test up AND down
-- 001_create_users.sql
-- 002_add_email_index.sql
-- 003_add_profile_trigger.sql
```

- One migration per logical change
- Test rollback before deploying
- Never edit a released migration — write a new one
- Use transactions for atomicity

## SQL vs NoSQL Decision Guide

| Use SQL When | Use NoSQL When |
|---|---|
| Relational data with joins | Simple key-value lookups |
| ACID transactions required | High-velocity writes |
| Complex queries and reporting | Flexible/evolving schemas |
| Strong consistency needed | Eventual consistency acceptable |

## Performance Checklist

- [ ] `EXPLAIN ANALYZE` on all queries
- [ ] Missing indexes identified
- [ ] No SELECT * in production code
- [ ] Pagination uses cursor-based (preferred) or offset
- [ ] N+1 query pattern eliminated
