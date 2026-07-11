# Server Integration Testing Patterns

Resilient patterns for verifying Node.js static servers and DOM-heavy frontends in sandboxed environments (Hermes subagents, delegate_task children).

## Key Principle: Avoid child_process.spawn for Test Servers

`child_process.spawn` with stdio piping can time out in sandboxed Vitest environments because the spawned process's stdout may not flush before the parent timeout fires. Instead, start the server **inline** in the test file using http.createServer directly.

### Inline Server Pattern (works every time)

```js
import http from 'http';
import fs from 'fs';
import path from 'path';

let server;
let baseUrl;

function createTestServer() {
  const dir = path.resolve(__dirname, '..'); // project root
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
        if (err) { res.writeHead(404); res.end('Not found'); return; }
        res.writeHead(200, { 'Content-Type': mime });
        res.end(data);
      });
    });
    srv.listen(0, () => { // port 0 = OS picks a free port
      server = srv;
      baseUrl = `http://localhost:${srv.address().port}`;
      resolve();
    });
    srv.on('error', reject);
  });
}

beforeAll(async () => { await createTestServer(); }, 10000);
afterAll(() => { if (server) server.close(); });
```

Key details:
- `port: 0` lets the OS allocate a free port, avoiding conflicts
- Test helper functions should reference `baseUrl`, not a hardcoded port
- `beforeAll` timeout of 10s is generous; the server is usually ready in <100ms

## Known happy-dom Quirks

### img.src Resolves Empty Attributes

In happy-dom (used via `@vitest-environment happy-dom`), an `<img src="">` element's `.src` property returns `"http://localhost:3000/"` instead of `""`. The browser's `URL` resolver treats the empty string as the base URL.

**Fix:** Use `.getAttribute('src')` to read the raw attribute value.

```js
// WRONG — resolves to 'http://localhost:3000/' in happy-dom
expect($('hero-icon').src).toBe('');

// CORRECT — reads the literal attribute
expect($('hero-icon').getAttribute('src')).toBe('');
```

### Multi-line Code Pattern Matching

When testing for patterns in inline `<script>` content, code that spans multiple lines won't match single-line `find()` predicates.

Example: `addEventListener('blur', ...)` and `setTimeout(...)` are on adjacent lines:

```js
el.searchInput.addEventListener('blur', () => {
    setTimeout(() => el.searchDropdown.classList.remove('open'), 200);
```

A test looking for a line containing BOTH 'blur' and 'setTimeout' will always miss.

**Fix:** Search for the two concepts on separate lines, or search each line independently.

```js
const blurLine = lines.find(l => l.includes('blur'));
const timeoutLine = lines.find(l => l.includes('200') && l.includes('classList.remove'));
expect(blurLine).toBeTruthy();
expect(timeoutLine).toBeTruthy();
expect(timeoutLine).toContain('200');
```

## Verification Checklist for Charmander's Test Output

When Charmander writes integration tests, after running the suite, check for these known-fragile patterns before declaring success:

1. Does any test use `child_process.spawn`? -> Replace with inline server pattern
2. Does any test use `element.src` to check for empty src? -> Replace with `getAttribute('src')`
3. Does any test try to match two concepts on the same line that span multiple lines? -> Split the match
4. Does any test hardcode a port number? -> Replace with `port: 0` + `baseUrl` variable
5. Does the test clean up its server in `afterAll`? -> Verify `server.close()` is called