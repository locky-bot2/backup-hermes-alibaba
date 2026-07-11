# Spec: Weather Web App

## Goal
A clean, fast weather dashboard that shows the user current conditions, hourly and 7-day forecast for any city, with a distinctive visual identity tied to weather data itself.

## Data Model

```
Location
  - name: string
  - lat: float
  - lon: float
  - country_code: string

CurrentWeather
  - temp_c: float
  - feels_like_c: float
  - condition: string (e.g. "Partly Cloudy", "Clear", "Rain")
  - icon_url: string
  - humidity_pct: int
  - wind_kph: float
  - wind_dir: string
  - uv_index: float
  - visibility_km: float
  - last_updated: datetime

HourlyForecast
  - time: datetime (hourly slices, next 24h)
  - temp_c: float
  - condition: string
  - precip_chance_pct: int
  - icon_url: string

DailyForecast
  - date: date (next 7 days)
  - temp_high_c: float
  - temp_low_c: float
  - condition: string
  - icon_url: string
  - sunrise: time
  - sunset: time
```

## API Surface

Weatherapi.com (free tier) — no backend needed, call directly from the frontend with API key set as an environment variable or in a `.env` file.

Key endpoints:
- `GET https://api.weatherapi.com/v1/current.json?key={key}&q={city}` — current conditions
- `GET https://api.weatherapi.com/v1/forecast.json?key={key}&q={city}&days=7` — forecast (includes current + hourly + 7-day)
- `GET https://api.weatherapi.com/v1/search.json?key={key}&q={query}` — city autocomplete/search

## User Flow

1. **Landing** — User arrives at an empty page with a search bar. Prompt text: "Search for a city..."
2. **Search** — User starts typing; dropdown shows matching cities from the autocomplete API. User selects one.
3. **Dashboard loads** — Page transitions to show weather data for the selected city:
   - Hero section: city name, current temp (large), condition text + icon, "Feels like X°"
   - Details row: Humidity, Wind, UV Index, Visibility, Pressure
   - Hourly strip: horizontal scroll of next 24 hours (time, icon, temp)
   - 7-day forecast: vertical list of day name, icon, high/low temp, condition
4. **Search again** — User can search for a different city from a persistent search bar in the header.
5. **Empty/Error state** — If the API key is missing or API returns an error, show a friendly explanation and the search bar. Never show a generic blank page.

## Visual Direction (for Pikachu)

**Subject grounding:** The app is about weather — changing atmospheric conditions, clouds, precipitation, wind. The visual identity should take inspiration from meteorological instruments, weather maps, isobars, and the natural color palette of sky conditions.

**Palette suggestion:**
- Background: deep storm-blue (#0B1B2F) to sky-gradient variations depending on condition
- Text: white/ice (#E8F0F8) on dark backgrounds
- Accent: gold/amber (#F5C242) for temperature highlights, lightning accent
- Secondary: slate-300 (#94A3B8) for muted data
- Condition colors: blue tones for rain, white/grey for clouds, gold for sun

**Typography:**
- Display: a clean geometric sans-serif with character (e.g. Inter or Space Grotesk) for large temperatures and city names
- Body: system font stack for data readouts
- Numbers: tabular figures for temp values so they align neatly

**Signature element:**
The background subtly shifts gradient or shows an animated particle/cloud layer loosely reflecting the current weather condition — not a distracting animation, but a mood-setter. Or a circular temperature gauge that animates on load.

**Layout:**
Single-page, vertically scrolling. Search bar pinned at top. Hero section dominates the fold. Below it: details row, hourly scroll, 7-day list.

## Tech Stack
- Static HTML/CSS/JS (single page app, no framework — keeps it lightweight)
- Weatherapi.com for all data (free tier, 1M calls/month)
- Use CSS custom properties for the design token system
- Responsive down to 375px mobile width

## Acceptance Criteria
- [ ] Search a city name and see matching options in a dropdown
- [ ] Select a city and see: current temp, condition, feels-like, humidity, wind, UV, visibility, hourly strip (24h), 7-day forecast
- [ ] The page works and looks good on mobile (375px) through desktop (1440px)
- [ ] Error state shown when API key is missing or request fails
- [ ] Loading state shown while fetching data
- [ ] Empty state shown when no city is selected (just search bar)
- [ ] The visual design feels distinctive, not a generic template
- [ ] All fonts, colors, spacing come from a defined token system (CSS custom properties)
- [ ] Responsive design: no overflow, touch-friendly tap targets on mobile

## Non-Goals
- No backend server — fully client-side
- No user accounts or location persistence (for now)
- No radar maps or animated weather maps
- No PWA/service worker for offline (future consideration)

## Files
All in a single directory (no build step):
```
weather-app/
  index.html          — main page (structure + inline CSS + inline JS)
  README.md           — setup instructions, API key note
```