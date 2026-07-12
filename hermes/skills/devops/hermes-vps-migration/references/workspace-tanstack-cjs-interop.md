# Hermes Workspace: TanStack Start Vite CJS→ESM Interop Fix

## Symptom

Blank page after `vite dev` starts successfully. Browser console shows:

```
Uncaught (in promise) SyntaxError: The requested module 
'/node_modules/.pnpm/use-sync-external-store@1.6.0_react@19.2.4/node_modules/use-sync-external-store/shim/index.js?v=ef3bb787' 
does not provide an export named 'useSyncExternalStore' 
(at useStore.js?v=ef3bb787:4:10)
```

Also possible variation with `use-sync-external-store/shim/with-selector`.

## Root Cause

Hermes Workspace uses TanStack Start (SSR React framework with Vite). The `vite.config.ts` has `optimizeDeps.noDiscovery: true`, which prevents Vite from auto-discovering deep dependencies to pre-bundle.

The `@tanstack/react-store` package imports from `use-sync-external-store/shim/with-selector`, which is a CJS package. Without pre-bundling, Vite serves the raw CJS file which doesn't have proper ESM named exports.

## Fix

Edit `vite.config.ts` → add both CJS packages to `optimizeDeps.include`:

```typescript
optimizeDeps: {
  noDiscovery: true,
  include: [
    'use-sync-external-store/shim',
    'use-sync-external-store/shim/with-selector',
  ],
  exclude: [
    'playwright',
    'playwright-core',
    'playwright-extra',
    'puppeteer-extra-plugin-stealth',
  ],
},
```

Then:
1. Kill vite: `fuser -k 3000/tcp`
2. Delete Vite cache: `rm -rf node_modules/.vite`
3. Restart with `--force`: `NODE_OPTIONS="--max-old-space-size=800" npx vite dev --host 0.0.0.0 --port 3000 --force`

## Verification

After fix:
- `curl -s http://localhost:3000 | grep -oP 'src="[^"]+"'` should show JS module references
- `curl -s http://localhost:3000/@id/virtual:tanstack-start-client-entry` should return JS content (not empty)
- The optimized deps list (`node_modules/.vite/deps/`) should include the pre-bundled version of the packages

## Affected Env

- Hermes Workspace v2.3.0 (outsourc-e/hermes-workspace)
- Node.js v22.22.3
- Vite v7.3.5
- TanStack Start / React Router
- Only occurs with `noDiscovery: true` in vite config
