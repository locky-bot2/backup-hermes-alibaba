# Kanban Tool Diagnostics

## Problem: kanban_create / kanban_list tools don't appear

The kanban lifecycle tools (create, complete, block, comment, list, etc.) are gated by
`_check_kanban_mode()` in `tools/kanban_tools.py`. They only appear when one of these
conditions is true:

1. **`HERMES_KANBAN_TASK`** env var is set — true for dispatcher-spawned workers
2. **`"kanban"` in `toolsets`** in config.yaml — must be explicitly enabled for normal sessions

## Diagnostic steps

### 1. Check which tools are visible

```
hermes tools list | grep kanban
```

Empty output means the gating check_fn is blocking everything.

### 2. Check the config's toolset list

Read `config.yaml` in the user's HERMES_HOME:

```
hermes config show | grep toolsets
```

Or read the config file directly. The relevant key is the top-level `toolsets:` list.
If `"kanban"` is absent, that's the root cause.

### 3. Check profile toolset inheritance

The check reads `cfg.get("toolsets", [])` — the profile-level toolsets list, not
platform-specific toolset mappings. Profile-level toolsets are shared across all
platforms; platform_toolsets only controls which toolsets are *enabled* per platform
but the check_fn doesn't look there.

## Fix: Enable the kanban toolset

```
hermes tools enable kanban
```

Then start a new session (`/reset` in chat, or exit and re-run `hermes`). Tool
changes do NOT take effect mid-conversation.

## CLI fallback path

The CLI command `hermes kanban create` bypasses the tool gating entirely — it calls
the database directly. Even if the tools are invisible in a chat session, the CLI
path still works:

```
hermes kanban create "My task title" --assignee profile-name
```

The CLI auto-initializes the DB on every invocation (init_db is idempotent), so no
separate `hermes kanban init` step is needed.

## Key source locations

| File | Purpose |
|------|---------|
| `tools/kanban_tools.py` | Tool definitions, schemas, check_fn, tool handler |
| `hermes_cli/kanban.py` | CLI subcommand parser and handlers |
| `hermes_cli/kanban_db.py` | Database layer: create_task, connect, schema |
| `hermes_cli/kanban_diagnostics.py` | Diagnostic utilities |

## Key env vars

| Env var | Purpose |
|---------|---------|
| `HERMES_KANBAN_TASK` | Set by dispatcher — gates tool visibility for workers |
| `HERMES_KANBAN_BOARD` | Pins the active board for the duration of a command |
| `HERMES_KANBAN_HOME` | Overrides kanban DB root directory |
| `HERMES_KANBAN_DB` | Hardcoded DB path override |
| `HERMES_PROFILE` | The current profile name; stamped as `created_by` on tasks |
| `HERMES_TENANT` | Default tenant namespace when not explicitly set on task creation |