# Vite CJS→ESM Interop: use-sync-external-store Case Study

## Problem

TanStack Start (SSR) app using Vite 7.3.5 with `optimizeDeps.noDiscovery: true`.
`@tanstack/react-store` imports `useSyncExternalStoreWithSelector` from `use-sync-external-store/shim/with-selector`.

This package is pure CJS (`module.exports = require(...)`) with no `"type": "module"`.
With `noDiscovery: true`, Vite doesn't auto-discover or pre-bundle it, so the browser
receives the raw CJS file — which has no ESM named exports.

**Error:**
```
Uncaught SyntaxError: The requested module '.../use-sync-external-store/shim/index.js'
does not provide an export named 'useSyncExternalStore'
```

## Dependency Chain

```
@tanstack/react-store/dist/esm/useStore.js
  → import { useSyncExternalStoreWithSelector } from "use-sync-external-store/shim/with-selector"
    → shim/with-selector.js (CJS: module.exports = require('../cjs/...'))
      → cjs/with-selector.development.js (CJS: require("use-sync-external-store/shim"))
        → shim/index.js (CJS: module.exports = require('../cjs/...'))
          → cjs/use-sync-external-store-shim.development.js (exports.useSyncExternalStore = ...)
```

## Fix Applied

1. Created `shim/index.mjs` — ESM wrapper re-exporting from React 19:
   ```js
   export { useSyncExternalStore } from 'react';
   ```

2. Created `shim/with-selector.mjs` — Clean ESM reimplementation:
   ```js
   import { useSyncExternalStore, useRef, useEffect, useMemo, useDebugValue } from 'react';
   export function useSyncExternalStoreWithSelector(...) { ... }
   ```

3. Updated `package.json` exports to point to `.mjs` files:
   ```json
   "./shim": { "default": "./shim/index.mjs" },
   "./shim/with-selector": "./shim/with-selector.mjs",
   "./shim/with-selector.js": "./shim/with-selector.mjs",
   ```

## Key Insights

- `optimizeDeps.include: ['use-sync-external-store']` **failed** because the package has
  no `"main"` field — only `"exports"`. Vite reported: `Failed to resolve dependency`.
- `optimizeDeps.include` with sub-path imports (`'use-sync-external-store/shim'`) also
  didn't produce a separate optimized dep in `.vite/deps/`.
- The `.mjs` wrapper approach bypasses the CJS→ESM converter entirely.
- React 19 has `useSyncExternalStore` built-in, so the shim's implementation is redundant.
