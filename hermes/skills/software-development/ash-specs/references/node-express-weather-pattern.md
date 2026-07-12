# Node.js + Express + Free API — Quick Web App Pattern

Concrete example of building a weather web app with Node.js Express backend, Open-Meteo API (free, no key), and vanilla JS frontend. This pattern generalizes to any quick prototype that needs a backend proxy + frontend.

## Architecture

```
weather-web-app/
├── server.js            ← Express: proxy API, serve static files
├── package.json         ← single dep: express
├── Dockerfile           ← node:22-alpine, non-root user, healthcheck
├── public/
│   ├── index.html       ← SPA: search bar + results card
│   ├── style.css        ← responsive, gradient, card layout
│   └── app.js           ← fetch / render, no framework
├── tests/
│   └── test.js          ← 22 integration tests (node built-ins, no deps)
└── scripts/
    └── deploy.sh        ← docker|direct|test modes
```

## Backend Pattern

One Express server does double duty: static file serving + API proxy.

```js
const express = require('express');
const https = require('https');
const path = require('path');

const app = express();
app.use(express.static(path.join(__dirname, 'public')));

// Proxy endpoint: /api/weather?city=London
app.get('/api/weather', async (req, res) => {
  // 1. Geocode city → lat/lon via Open-Meteo Geocoding API
  // 2. Fetch current weather via Open-Meteo Forecast API
  // 3. Map WMO weather codes → human-readable conditions + emoji
  // 4. Return JSON: { city, temperature, feels_like, humidity, wind_speed, condition, emoji }
});
```

### Key Design Decisions

| Choice | Why |
|--------|-----|
| **Proxy on backend** | Keeps API calls server-side; avoids CORS issues |
| **Open-Meteo** | Free, no API key, 10k+ req/day, accurate |
| **WMO code mapping** | 256 codes → ~20 human conditions with emoji |
| **Vanilla JS frontend** | Zero build step, single HTML+CSS+JS, works on file:// or HTTP |
| **port 0 in tests** | OS picks free port, avoids conflicts; use `http.createServer` not `child_process.spawn` |
| **No framework** | No React/Vue overhead for a single-page app |

## Frontend Pattern

```js
// Single function app — no framework, no build step
const WEATHER_MAP = { 0: '☀️', 1: '🌤️', 2: '⛅', 3: '☁️', 45: '🌫️', ... };

async function fetchWeather(city) {
  const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
  const data = await res.json();
  renderWeatherCard(data);  // update DOM with { city, temperature, feels_like, ... }
}
```

States to handle: loading (spinner), success (weather card with animation), error (red banner), 404 (city not found).

## Preset City Buttons

Add quick-access buttons for common cities — shows the app works immediately without typing:

```html
<div class="preset-cities">
  <button data-city="London">London</button>
  <button data-city="Tokyo">Tokyo</button>
  ...
</div>
```

```js
document.querySelectorAll('.preset-btn').forEach(btn => {
  btn.addEventListener('click', () => fetchWeather(btn.dataset.city));
});
```

## Docker Deployment

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY server.js public/ ./public/
HEALTHCHECK --interval=30s CMD wget --spider http://localhost:3000/health
USER node
CMD ["node", "server.js"]
```

## Testing Strategy

Write integration tests that:
1. Start Express server inline (`http.createServer` with port 0) — do NOT use `child_process.spawn`
2. Use `http.get` (node built-in) — no test framework dependency
3. Test: health endpoint, valid cities, edge cases (empty, missing, nonexistent), static files
4. Output PASS/FAIL, exit 0 for all pass, 1 for any fail

See `references/server-integration-testing.md` for the inline server pattern.

## Subagent Timeout Pitfall

When delegating Node.js project setup to subagents (`delegate_task`), the subagent may timeout (default 30s) during `npm install` because npm needs to download packages over the network. Symptoms:
- Subagent returns with `status: "timeout"` after exactly 30s
- `api_calls` shows the subagent made progress (e.g., 6-9 calls) but didn't finish
- Files may be partially written

**Fallback pattern:** Build the project directly in the parent session instead of re-delegating. The subagent's partial output (even timed out) is a useful starting point — verify what exists, finish the rest yourself.

Alternatively, for future runs: increase the subagent timeout via environment variable or use the `no_agent` cron script pattern for long-running data collection.
