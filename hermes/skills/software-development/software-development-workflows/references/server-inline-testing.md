# Inline Server Integration Testing (preferred)

## Why Inline + Random Port

The inline approach creates the HTTP server **inside the test process** using `server.listen(0)` for OS-assigned random port allocation. This avoids the main pitfalls of the child-process approach:

| Concern | Child Process (fixed port) | Inline Server (port 0) |
|---------|---------------------------|----------------------|
| Parallel test safety | Crashes on "address in use" | Fully parallel-safe |
| Startup speed | ~500ms-2s (subprocess boot) | ~10ms (in-process) |
| Zombie processes | Leaks if test crashes mid-run | None (in-process) |
| Server mod required | Needs `process.env.PORT` support | Reads files directly |

## Full Example

```javascript
/**
 * @vitest-environment node
 */
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dir = path.resolve(__dirname, '..');  // project root

let server;
let baseUrl;

// ---------------------------------------------------------------------------
// Create an HTTP server that mirrors server.js behaviour
// ---------------------------------------------------------------------------
function createTestServer() {
  return new Promise((resolve, reject) => {
    const srv = http.createServer((req, res) => {
      const filePath = path.join(dir, req.url === '/' ? 'index.html' : req.url);
      const ext = path.extname(filePath);
      const mime = {
        '.html': 'text/html',
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml',
      }[ext] || 'text/plain';

      fs.readFile(filePath, (err, data) => {
        if (err) {
          res.writeHead(404);
          res.end('Not found');
          return;
        }
        res.writeHead(200, { 'Content-Type': mime });
        res.end(data);
      });
    });

    srv.listen(0, () => {          // port 0 = OS assigns a random free port
      server = srv;
      baseUrl = `http://localhost:${srv.address().port}`;
      resolve();
    });

    srv.on('error', reject);
  });
}

beforeAll(async () => {
  await createTestServer();
}, 10000);

afterAll(() => {
  if (server) server.close();
});

// ---------------------------------------------------------------------------
// HTTP helper
// ---------------------------------------------------------------------------
function fetchFromServer(urlPath) {
  return new Promise((resolve, reject) => {
    const req = http.get(`${baseUrl}${urlPath}`, (res) => {
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

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('Static file server', () => {
  let indexHtml;

  beforeAll(async () => {
    indexHtml = await fetchFromServer('/');
  });

  it('serves index.html at / with 200', () => {
    expect(indexHtml.status).toBe(200);
    expect(indexHtml.headers['content-type']).toContain('text/html');
    expect(indexHtml.body).toContain('<!DOCTYPE html>');
  });

  it('serves JS files with correct MIME type', async () => {
    const res = await fetchFromServer('/weather.js');
    expect(res.status).toBe(200);
    expect(res.headers['content-type']).toBe('application/javascript');
  });

  it('returns 404 for non-existent files', async () => {
    const res = await fetchFromServer('/nonexistent.html');
    expect(res.status).toBe(404);
  });

  it('handles concurrent requests', async () => {
    const results = await Promise.all([
      fetchFromServer('/'),
      fetchFromServer('/app.js'),
      fetchFromServer('/index.html'),
      fetchFromServer('/nonexistent'),
      fetchFromServer('/'),
    ]);
    expect(results.map(r => r.status)).toEqual([200, 200, 200, 404, 200]);
  });

  it('/ and /index.html return identical content', async () => {
    const [root, index] = await Promise.all([
      fetchFromServer('/'),
      fetchFromServer('/index.html'),
    ]);
    expect(root.body).toBe(index.body);
  });
});
```

## What Makes a Good Server Integration Test

- **Status codes:** 200 for existing files, 404 for missing
- **MIME types:** Verify `content-type` header for `.html`, `.js`, `.css`, images
- **Content verification:** body contains expected markers (DOCTYPE, title, function names)
- **Root vs named:** `/` and `/index.html` should return identical content
- **Concurrency:** 5+ simultaneous requests via `Promise.all`
- **Edge cases:** missing assets, non-standard extensions, deep paths like `/a/b/c`

## Pitfalls

- **`server.close()` in afterAll:** Always guard with `if (server) server.close()` in case `beforeAll` failed before the server was assigned.
- **File resolution:** Use `__dirname` + `path.resolve()` to find the project root. Tests often live in a `tests/` subdirectory, so you need `path.resolve(__dirname, '..')` to reach the root.
- **Path traversal safety:** The inline server joins `req.url` directly to the project root. This is safe for testing since it mirrors the production server's behaviour. Don't add path normalization — it would defeat the test's purpose of catching path issues.
