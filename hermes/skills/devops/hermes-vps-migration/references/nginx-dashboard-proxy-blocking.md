# Nginx Host Header Blocking: Dashboard Behind Proxy

## Context

Hermes dashboard runs on port 9120. In production setups, it's common to proxy it through nginx on port 9119 with hostname-based routing.

If nginx has a `default_server` block that returns `444` (close connection without response), any request without a matching `Host` header gets silently dropped.

## Symptom

Hermes Workspace starts but logs:
```
[gateway] Failed to fetch dashboard token: fetch failed
[gateway] gateway=http://127.0.0.1:8642 dashboard=http://127.0.0.1:9119 mode=portable
```

Workspace runs in "portable mode" — chat works but sessions, skills, config are unavailable.

## Why It Happens

When the Workspace Node.js server fetches `http://127.0.0.1:9119`, it sends `Host: 127.0.0.1:9119`. If nginx only accepts `Host: pre.alibabacloud-workbench.com`, it hits the `default_server return 444` block.

## Fix

Point the dashboard URL directly at the backend, bypassing nginx:

```
CLAUDE_DASHBOARD_URL=http://127.0.0.1:9120
HERMES_DASHBOARD_URL=http://127.0.0.1:9120
```

Or modify nginx config to accept direct requests:
```nginx
server {
    listen 127.0.0.1:9119;  # listen only on localhost
    # no default_server — direct requests from local services work
    proxy_pass http://127.0.0.1:9120;
}
```

## Detection

```bash
# Fails (through nginx with host restriction):
curl -s http://127.0.0.1:9119/api/status

# Works (direct):
curl -s http://127.0.0.1:9120/api/status
```
