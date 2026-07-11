# Weather App — Serving & Smoke Test Commands

Concrete example of web app testing for the Atmo weather dashboard built by Pikachu.

## File Layout

```
/opt/data/weather-app/
  index.html          — single-page app (1076 lines, inline CSS + JS)
  weather.js          — 10 pure functions (ES module exports)
  package.json        — vitest config
  tests/
    weather.test.js   — 27 unit tests
  setup.sh            — git init + commit script
```

## Serve (ES modules need HTTP)

```bash
cd /opt/data/weather-app
python3 -m http.server 8080
```

Then browse to http://localhost:8080. Do NOT open via `file://` — Chromium blocks ES module imports on file:// protocol.

## Run Unit Tests

```bash
cd /opt/data/weather-app
npm install
npm test                    # vitest run
npm run test:coverage       # vitest run --coverage
```

## What to Smoke-Test

1. **Empty state** — page loads with search bar + API key field. Background is deep storm-blue.
2. **API key persistence** — type a key, click Save, refresh page. Key should be saved to localStorage.
3. **Search autocomplete** — type "Tokyo", wait 300ms debounce, dropdown appears with matching cities.
4. **Dashboard render** — select a city. Hero shows: city name, temperature (large), condition icon + text, "Feels like X°".
5. **Details grid** — humidity %, wind kph + direction, UV index, visibility km, pressure mb.
6. **Hourly strip** — horizontal scroll of next ~24 hours: time label, icon, temp.
7. **7-day forecast** — vertical list: day name (Today/Tomorrow/Mon), date (Jun 14), icon, high/low.
8. **Error state** — invalid API key should show friendly error with retry button.
9. **Search again** — search bar stays visible, can search a different city.
10. **Console** — `browser_console()` should show no JS errors.