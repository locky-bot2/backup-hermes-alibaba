# Hermes Workspace Setup (Attach to Existing Agent)

[Hermes Workspace](https://github.com/outsourc-e/hermes-workspace) is a third-party (MIT) visual web UI for Hermes Agent — chat, terminal, memory, skills, inspector, multi-agent ops. This reference covers **attaching** it to an already-running Hermes Agent (not the Docker/one-line install paths).

## Requirements

- Node.js 22+ (check with `node --version`)
- pnpm: `sudo corepack enable pnpm`
- Hermes Agent already installed and configured
- At least 1GB free RAM (Vite + esbuild dep optimization is memory-intensive)
- **On VPS with <2GB RAM:** Add swap before starting, or esbuild gets OOM-killed

## Quick Setup

```bash
cd ~
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace

# Install deps
pnpm install

# Configure .env
cat > .env << 'EOF'
# Workspace runtime reads both HERMES_* and CLAUDE_* env vars.
# Set BOTH to be safe — different code paths may check each set.
HERMES_API_URL=http://127.0.0.1:8642
HERMES_DASHBOARD_URL=http://127.0.0.1:9120
HERMES_API_TOKEN=workspace-dev-key
CLAUDE_API_URL=http://127.0.0.1:8642
CLAUDE_DASHBOARD_URL=http://127.0.0.1:9120
CLAUDE_API_TOKEN=workspace-dev-key
EOF
```

## Enable Gateway API Server

The gateway needs `API_SERVER_ENABLED=true` to expose the API on port 8642:

```bash
echo "API_SERVER_ENABLED=true" >> ~/.hermes/.env
echo "API_SERVER_KEY=workspace-dev-key" >> ~/.hermes/.env

# Stop the systemd service (prevents auto-restart conflicts)
systemctl --user stop hermes-gateway

# Start gateway manually with API server
hermes gateway run
```

Verify:
```bash
curl http://127.0.0.1:8642/health
# → {"status": "ok", "platform": "hermes-agent"}
```

## Dashboard Port

The dashboard must be running on a reachable port. Default internal ports:
- Dashboard API: `:9119` (via nginx reverse proxy) or `:9120` (direct)
- Dashboard health: `curl http://127.0.0.1:9120/api/status`

If using nginx as reverse proxy, ensure the `proxy_pass` target is correct.

## Run Workspace

### Dev mode (hot reload):
```bash
cd ~/hermes-workspace && NODE_OPTIONS="--max-old-space-size=800" npx vite dev --host 0.0.0.0 --port 3000 --force
# → http://localhost:3000 (local) or http://<vps-ip>:3000 (remote)
```

> **Why `--force`:** Forces Vite to re-optimize dependencies from scratch, preventing stale-cache issues where virtual modules return empty or exports are missing. Essential after `.env` changes or on first launch.

### Production build + preview:
```bash
cd ~/hermes-workspace && pnpm build && npx vite preview --host 0.0.0.0 --port 3000
# → http://localhost:3000 (local) or http://<vps-ip>:3000 (remote)
```

> **Important:** Use `--host 0.0.0.0` to bind to all interfaces (needed for external access via VPS IP). Without it, the server only listens on `127.0.0.1`.

### Memory-constrained VPS workaround (< 2 GB RAM)

If `pnpm dev` crashes with esbuild "The service was stopped" error (OOM):

```bash
# 1. Add swap (required — 2GB minimum)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 2. Run with capped memory
NODE_OPTIONS="--max-old-space-size=1024" pnpm dev --host 0.0.0.0 --port 3000
```

**Why this works:** The Vite dev server spawns esbuild for dependency optimization as a child process. Without swap, the OS OOM-killer kills the child on systems with ~1.8GB RAM and ~860Mi available. Adding 2GB swap gives esbuild room to complete.

**If even with swap the build hangs**: Ensure the running Hermes gateway + dashboard + TUI aren't consuming too much RAM. Stop unnecessary background processes or limit node memory further (`--max-old-space-size=800`).

**Don't rely on `pnpm build` + `vite preview` alone** — the production build also uses esbuild and will fail identically without swap. Preview only works if the build fully completed (you'll see `dist/` or `.output/` directories).

## Verify Pairing

```bash
curl http://127.0.0.1:8642/health        # Gateway API
curl http://127.0.0.1:9119/api/status    # Dashboard API
curl http://localhost:3000/api/sessions    # Workspace sessions (after boot)
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `8642: not available` | Gateway not running with API server enabled. Check `~/.hermes/.env` has `API_SERVER_ENABLED=true` and restart gateway. |
| Dashboard shows "portable mode" | Dashboard not reachable. Start `hermes dashboard` or verify nginx proxy. |
| Workspace shows "Offline" | Refresh/reprobe the UI before starting another gateway. `curl http://localhost:3000/api/sessions` to check. |
| esbuild OOM crash | Add 2GB swap (`sudo fallocate -l 2G /swapfile && sudo swapon /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile`) and use `NODE_OPTIONS="--max-old-space-size=1024" pnpm dev --host 0.0.0.0`. Make swap permanent via fstab. |
| `curl: (7) Failed to connect` | Service not listening. Check `ss -tlnp` for the port. |
| Dashboard unreachable from workspace (`dashboard=http://127.0.0.1:9119 mode=portable`) | Nginx may block requests without the right Host header (common pattern: `server { listen 9119 default_server; return 444; }`). Fix: point `*_DASHBOARD_URL` directly at dashboard's internal port (`:9120`) instead of going through nginx. |
| Blank page (JS module returns 0 bytes) | Vite cache stale after `.env` change. Clear `node_modules/.vite` and restart with `vite dev --force`. |
| `useSyncExternalStore` export error | **Two possible causes:** 1) Stale Vite cache — `rm -rf node_modules/.vite && npx vite dev --force`. 2) Persistent error after cache clear means Vite's CJS→ESM converter failed on `use-sync-external-store/shim` (common with `optimizeDeps.noDiscovery: true`). Fix: Create proper ESM `.mjs` wrapper files that re-export from React 19 and update `package.json` exports. See full recipe below. |
| Page loads blank, JS entry returns 0 bytes | Vite cache stale after `.env` change. Clear `node_modules/.vite` and restart with `vite dev --force`. If still blank, check the Vite dep optimization didn't crash (exit 137 = OOM). |
| `vite dev` exits 137 (SIGKILL) | OOM killer. Add swap first, then restart. |

---

## CJS→ESM Shim Workaround (TanStack Start + Vite + pnpm)

When `@tanstack/react-store` imports `{ useSyncExternalStoreWithSelector }` from `use-sync-external-store/shim/with-selector`, Vite may fail to convert the CJS package to ESM, producing:

```
Uncaught SyntaxError: ... does not provide an export named 'useSyncExternalStore'
```

This happens because `use-sync-external-store` is a CJS-only package (no `"type": "module"`) and Vite's `optimizeDeps.noDiscovery: true` prevents auto-discovery.

**Fix — Create ESM wrappers:**

React 19 has `useSyncExternalStore` built-in, so the shim can just re-export from React. The `with-selector` needs a port of the actual implementation since React doesn't export `useSyncExternalStoreWithSelector`.

```bash
WS=~/hermes-workspace

# Locate the actual package directory in pnpm store
PKG=$(find "$WS/node_modules/.pnpm" -path "*/use-sync-external-store@*/node_modules/use-sync-external-store" -type d | head -1)

# 1. Create ESM wrapper for shim/index.mjs
cat > "$PKG/shim/index.mjs" << 'EOF'
export { useSyncExternalStore } from 'react';
EOF

# 2. Create ESM wrapper for shim/with-selector.mjs
# This ports the React CJS shim implementation to ESM
cat > "$PKG/shim/with-selector.mjs" << 'ESMEOF'
import { useSyncExternalStore, useRef, useEffect, useMemo, useDebugValue } from 'react';

const is = (x, y) => (x === y && (0 !== x || 1 / x === 1 / y)) || (x !== x && y !== y);
const objectIs = typeof Object.is === 'function' ? Object.is : is;

export function useSyncExternalStoreWithSelector(subscribe, getSnapshot, getServerSnapshot, selector, isEqual) {
  const instRef = useRef(null);
  if (instRef.current === null) instRef.current = { hasValue: false, value: null };
  const inst = instRef.current;
  const instRefMemo = useMemo(() => {
    let hasMemo = false, memoizedSnapshot, memoizedSelection;
    const maybeGetServerSnapshot = getServerSnapshot === undefined ? null : getServerSnapshot;
    const memoizedSelector = (nextSnapshot) => {
      if (!hasMemo) {
        hasMemo = true; memoizedSnapshot = nextSnapshot;
        const nextSelection = selector(nextSnapshot);
        if (isEqual !== undefined && inst.hasValue) {
          const cs = inst.value;
          if (isEqual(cs, nextSelection)) return (memoizedSelection = cs);
        }
        return (memoizedSelection = nextSelection);
      }
      const cs = memoizedSelection;
      if (objectIs(memoizedSnapshot, nextSnapshot)) return cs;
      const ns = selector(nextSnapshot);
      if (isEqual !== undefined && isEqual(cs, ns)) return (memoizedSnapshot = nextSnapshot), cs;
      memoizedSnapshot = nextSnapshot; return (memoizedSelection = ns);
    };
    return [
      () => memoizedSelector(getSnapshot()),
      maybeGetServerSnapshot === null ? undefined : () => memoizedSelector(maybeGetServerSnapshot()),
    ];
  }, [getSnapshot, getServerSnapshot, selector, isEqual]);
  const value = useSyncExternalStore(subscribe, instRefMemo[0], instRefMemo[1]);
  useEffect(() => { inst.hasValue = true; inst.value = value; }, [value]);
  useDebugValue(value);
  return value;
}
ESMEOF

# 3. Update package.json exports to point at .mjs files
python3 -c "
import json
with open('$PKG/package.json') as f:
    pkg = json.load(f)
pkg['exports']['\"./shim\"']['default'] = './shim/index.mjs'
pkg['exports']['\"./shim/index.js\"'] = './shim/index.mjs'
pkg['exports']['\"./shim/with-selector\"'] = './shim/with-selector.mjs'
pkg['exports']['\"./shim/with-selector.js\"'] = './shim/with-selector.mjs'
with open('$PKG/package.json', 'w') as f:
    json.dump(pkg, f, indent=2)
"

# 4. Clear cache and restart
rm -rf "$WS/node_modules/.vite"
NODE_OPTIONS="--max-old-space-size=800" npx vite dev --host 0.0.0.0 --port 3000
```

After this fix, the workspace should load without the `useSyncExternalStore` error.