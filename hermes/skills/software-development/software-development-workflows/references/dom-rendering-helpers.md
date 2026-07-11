# DOM Rendering Helper Patterns

## The IIFE Problem

In vanilla HTML/CSS/JS apps, rendering logic is often inside an IIFE within a `<script>` tag:

```html
<script type="module">
  import { parseLocation } from './weather.js';
  (function() {
    'use strict';
    function renderDashboard(data) {
      const location = parseLocation(data);
      document.getElementById('hero-city').textContent = location.name;
      // ...
    }
  })();
</script>
```

These functions **cannot be imported** by tests. The solution: mirror the rendering logic as test helpers.

## Pattern: Duplicate, Don't Extract

Create helper functions in the test file that mirror the app's rendering logic exactly:

```javascript
// Test helper — mirrors index.html's showView
function showView(viewId) {
  document.querySelectorAll('.state-view').forEach((v) => v.classList.remove('active'));
  document.getElementById(viewId).classList.add('active');
}

// Test helper — mirrors index.html's showError
function showError(title, message) {
  document.getElementById('error-title').textContent = title;
  document.getElementById('error-message').textContent = message;
  showView('state-error');
}

// Test helper — mirrors index.html's renderDashboard
function renderDashboard(data) {
  const location = parseLocation(data);
  const current = parseCurrentWeather(data);
  // ... exact same DOM operations as the app
  showView('state-dashboard');
}

// DOM selector helper (same as $ in index.html)
const $ = (id) => document.getElementById(id);
```

The helpers:
- Use the **same parsing functions** (`parseLocation`, `parseCurrentWeather`) from `weather.js`
- Perform the **same DOM operations** as the app
- Call the **same state transition functions**

This ensures the test validates real integration between parsing and display, not just isolated function behavior.

## DOM Setup Function

Create a `setupDOM()` function that initializes the full app DOM structure before each test:

```javascript
function setupDOM() {
  document.body.innerHTML = `
    <div id="app">
      <!-- Header with search -->
      <div class="header">
        <div class="logo">Atmo<span>.</span></div>
        <input id="search-input" />
        <div id="search-dropdown" class="search-dropdown"></div>
      </div>

      <!-- State: Empty (active by default) -->
      <div id="state-empty" class="state-view active">...</div>

      <!-- State: Loading -->
      <div id="state-loading" class="state-view">...</div>

      <!-- State: Error -->
      <div id="state-error" class="state-view">
        <h2 id="error-title">Default</h2>
        <p id="error-message">...</p>
        <button id="retry-btn">Try Again</button>
      </div>

      <!-- State: Dashboard -->
      <div id="state-dashboard" class="state-view">
        <h1 id="hero-city">—</h1>
        <div id="hero-temp">--<span class="hero-temp-unit">°C</span></div>
        <div id="hero-feels">Feels like —°</div>
        <img id="hero-icon" />
        <span id="hero-condition-text">—</span>
        <div id="hero-updated">—</div>
        <span id="detail-humidity">--</span>
        <span id="detail-wind">--</span>
        <span id="detail-uv">--</span>
        <span id="detail-visibility">--</span>
        <span id="detail-pressure">--</span>
        <div id="hourly-strip"></div>
        <div id="daily-list"></div>
      </div>
    </div>
  `;
}
```

Then use in `beforeEach`:

```javascript
beforeEach(() => {
  setupDOM();
});
```

## What to Assert

### State Views

```javascript
expect($('state-loading').classList.contains('active')).toBe(true);
expect($('state-empty').classList.contains('active')).toBe(false);
```

### Text Content

```javascript
expect($('hero-city').textContent).toBe('Tokyo');
expect($('hero-temp').innerHTML).toContain('°C');
expect($('detail-humidity').textContent).toBe('65');
```

### Attributes

```javascript
expect($('hero-icon').src).toContain('cdn.weatherapi.com');
expect($('hero-icon').alt).toBe('Partly Cloudy');
```

### List Rendering

```javascript
// Hourly cards
const cards = $('hourly-strip').querySelectorAll('.hourly-card');
expect(cards.length).toBeGreaterThan(0);
expect(cards[0].querySelector('.hourly-temp').textContent).toContain('°');

// Daily rows
const rows = $('daily-list').querySelectorAll('.daily-row');
expect(rows.length).toBe(2);
expect(rows[0].querySelector('.daily-high').textContent).toBe('25°');
```

### Dropdown

```javascript
renderSearchResults(results);
expect($('search-dropdown').classList.contains('open')).toBe(true);
const items = $('search-dropdown').querySelectorAll('.search-dropdown-item');
expect(items.length).toBe(3);
expect(items[0].dataset.city).toBe('Tokyo');
```

## Pitfalls

1. **InnerHTML vs textContent:** Use `innerHTML` when the element contains child elements (like `<span>°C</span>`), use `textContent` for plain text.

2. **Number formatting:** The app may use `Math.round()` on values before displaying. Round assertions accordingly: `expect(temp).toBe('13')` for `Math.round(12.6)`.

3. **Dynamic date-dependent values:** `formatDayName()` returns "Today" or "Tomorrow" based on the current date. Assert against patterns, not exact strings.

4. **Empty states:** Always test empty list rendering (0 items should produce empty innerHTML, not error).

5. **Mock data completeness:** Your mock API response must include all fields the app's rendering functions reference. Missing fields cause runtime errors, not graceful degradation.