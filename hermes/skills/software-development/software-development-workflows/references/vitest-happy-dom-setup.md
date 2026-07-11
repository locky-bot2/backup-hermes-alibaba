# Vitest + happy-dom Setup

## Installing Dependencies

```bash
# Install vitest and happy-dom
npm install --save-dev vitest happy-dom

# Optional: coverage
npm install --save-dev @vitest/coverage-v8
```

## vitest.config.js

```javascript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',          // default env (for unit + server tests)
    include: ['tests/**/*.test.js'],
    coverage: {
      reporter: ['text', 'text-summary'],
      include: ['weather.js'],     // or your source files
    },
    testTimeout: 30000,            // generous timeout for server process
    hookTimeout: 30000,            // generous timeout for beforeAll/afterAll
  },
});
```

## Per-File Environment Selection

Use a docblock comment at the top of each test file to set its environment:

```javascript
/**
 * @vitest-environment happy-dom
 *
 * DOM Integration Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
```

- The `@vitest-environment` annotation MUST be the first line inside a comment block
- Unit/server tests stay in the default `node` environment (no annotation needed)
- Only DOM tests need `happy-dom`

## Happy DOM Limitations

| Feature | Status | Workaround |
|---------|--------|-----------|
| `localStorage` | Not available by default | Mock it with `vi.fn()` (see pattern below) |
| `fetch` | Not available by default | Mock with `vi.fn()` |
| Canvas/SVG | Limited support | Works for basic `getContext('2d')`, skip pixel-level assertions |
| `requestAnimationFrame` | Not available | Use `setTimeout(0)` or mock it |
| Navigation/URL | Limited | Test URL construction separately |
| Layout/style | No computed styles | Test `classList` and attribute values instead |

## Mocking localStorage

```javascript
beforeEach(() => {
  const store = {};
  window.localStorage = {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => { store[key] = String(value); }),
    removeItem: vi.fn((key) => { delete store[key]; }),
    clear: vi.fn(() => { Object.keys(store).forEach(k => delete store[k]; }); }),
  };
});
```

## Running Tests

```bash
# Run all tests
npm test                         # or: npx vitest run

# Run specific files
npx vitest run tests/server.integration.test.js tests/dom.integration.test.js

# Run with verbose output
npx vitest run --reporter=verbose

# Watch mode
npm run test:watch               # or: npx vitest

# Coverage
npm run test:coverage            # or: npx vitest run --coverage
```

## package.json Scripts

```json
{
  "type": "module",
  "scripts": {
    "test": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:watch": "vitest"
  }
}
```