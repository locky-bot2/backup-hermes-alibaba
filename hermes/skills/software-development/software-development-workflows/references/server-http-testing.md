# Server HTTP Testing with Child Process

## Pattern: Spawn Server on Test Port

The cleanest approach for testing a Node.js HTTP server is to:
1. Patch the server to accept `process.env.PORT`
2. Spawn it as a child process on a unique test port
3. Use Node's built-in `http` module to make real HTTP requests
4. Kill the process in `afterAll`

## Server Patching

Before spawning, the server must accept a configurable port:

```javascript
// server.js (BEFORE)
var port = 8080;

// server.js (AFTER)
var port = process.env.PORT || 8080;
```

This is the only change needed to make the server testable. It doesn't affect production (defaults to 8080).

## Full Test Structure

```javascript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import http from 'http';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, '..');
const TEST_PORT = 8765; // Avoid 8080 (default) to prevent conflicts

let serverProcess;

beforeAll(async () => {
  serverProcess = spawn('node', [path.join(PROJECT_ROOT, 'server.js')], {
    cwd: PROJECT_ROOT,
    env: { ...process.env, PORT: String(TEST_PORT) },
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Server start timeout')), 5000);
    const onData = (data) => {
      if (data.toString().includes('Server running')) {
        clearTimeout(timeout);
        resolve();
      }
    };
    serverProcess.stdout.on('data', onData);
    serverProcess.stderr.on('data', onData);
    serverProcess.on('error', (err) => {
      clearTimeout(timeout);
      reject(err);
    });
  });
}, 10000); // Timeout for the entire beforeAll

afterAll(() => {
  if (serverProcess && !serverProcess.killed) {
    serverProcess.kill();
  }
});
```

## HTTP Request Helper

```javascript
function fetchFromServer(urlPath) {
  return new Promise((resolve, reject) => {
    const req = http.get(`http://localhost:${TEST_PORT}${urlPath}`, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          body: data,
        });
      });
    });
    req.on('error', reject);
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Request timed out'));
    });
  });
}
```

## What to Test

| Test | What It Verifies |
|------|-----------------|
| `GET /` → 200 | Root serves index.html |
| `GET /index.html` → 200 + `text/html` | HTML files served correctly |
| `GET /app.js` → 200 + `application/javascript` | JS files with correct MIME |
| `GET /nonexistent.html` → 404 | Non-existent files return 404 |
| `GET /random/path` → 404 | Random paths return 404 |
| 5 concurrent requests | Server handles `Promise.all` without crashing |

## Pitfalls

1. **Port already in use:** If `TEST_PORT` is occupied, the test will hang. Always check that your test port isn't used by other services. Consider making it configurable: `const TEST_PORT = process.env.TEST_PORT || 8765;`

2. **Server not killed:** If the test crashes before `afterAll`, the server process lingers. Use `serverProcess.kill()` with a catch, or track the PID for manual cleanup.

3. **Path resolution:** When both the test file and server.js are in different directories, use `__dirname` + `path.resolve()` to find server.js relative to the test file.

4. **Timeout:** `beforeAll` needs a timeout at least as long as the server startup wait (5s startup + buffer = 10s `beforeAll` timeout). Set `hookTimeout: 30000` in vitest config.

5. **Port env in spawn:** Always spread `...process.env` when setting custom env so PATH and other essential vars are preserved: `{ ...process.env, PORT: String(TEST_PORT) }`.