# API Mocking Patterns for Web App Integration Tests

## Mocking fetch (or any async network call)

Since integration tests should **not make real network requests**, mock the fetch-like function with `vi.fn()`:

```javascript
// In test
let mockFetch;

beforeEach(() => {
  mockFetch = vi.fn();
});

// Test success path
it('renders dashboard on success', async () => {
  mockFetch.mockResolvedValue(mockApiResponse);
  await loadWeather('Tokyo', 'test-key', mockFetch);

  expect($('state-dashboard').classList.contains('active')).toBe(true);
  expect($('hero-city').textContent).toBe('Tokyo');
});

// Test failure path
it('shows error on network failure', async () => {
  mockFetch.mockRejectedValue(new Error('Network failure'));
  await loadWeather('Tokyo', 'test-key', mockFetch);

  expect($('state-error').classList.contains('active')).toBe(true);
  expect($('error-message').textContent).toBe('Network failure');
});
```

## URL Verification

Verify the mock was called with the correct API URL:

```javascript
it('calls the correct API endpoint', async () => {
  mockFetch.mockResolvedValue(mockApiResponse);
  await loadWeather('London', 'abc123', mockFetch);

  expect(mockFetch).toHaveBeenCalledTimes(1);
  const url = mockFetch.mock.calls[0][0];
  expect(url).toContain('api.weatherapi.com');
  expect(url).toContain('forecast.json');
  expect(url).toContain('key=abc123');
  expect(url).toContain('q=London');
  expect(url).toContain('days=7');
});
```

## Minimal Mock Structure

The `loadWeather` test helper should accept a mock fetch function:

```javascript
async function loadWeather(city, apiKey, mockFetchFn) {
  // Guard: no API key
  if (!apiKey) {
    showError('API Key Required', 'Please enter your API key.');
    return;
  }

  showView('state-loading');
  try {
    const url = buildUrl(apiKey, 'forecast.json', { q: city, days: 7 });
    const data = await mockFetchFn(url);  // ← mockable
    renderDashboard(data);
  } catch (err) {
    showError('Unable to Load Weather', err.message);
  }
}
```

The mock fetch is injected as a parameter, making it testable without hitting real APIs.

## What to Test in Async Flows

| Scenario | Expected Behavior |
|----------|------------------|
| Successful API response | Dashboard renders with parsed data |
| Network error | Error state with descriptive message |
| HTTP 400/401/403 | Error state with API error message |
| Empty/truncated response | Error state (parse failure is caught) |
| Missing API key | Error state shown immediately, no fetch called |
| Loading state visibility | Loading state shown BEFORE await completes |

## Testing Loading State Timing

To verify the loading state appears before data arrives:

```javascript
it('shows loading state before data arrives', async () => {
  // Create a promise that never resolves
  const neverResolving = new Promise(() => {});
  mockFetch.mockReturnValue(neverResolving);

  // Start load but don't await
  const promise = loadWeather('Tokyo', 'test-key', mockFetch);

  // Loading state is already active
  expect($('state-loading').classList.contains('active')).toBe(true);
  expect($('state-empty').classList.contains('active')).toBe(false);

  // Clean up
  promise.catch(() => {});
});
```

## Search Autocomplete Mocking

For search endpoints:

```javascript
const searchResults = [
  { name: 'Tokyo', region: 'Tokyo', country: 'Japan' },
  { name: 'London', region: 'City of London', country: 'United Kingdom' },
];

it('returns autocomplete results', async () => {
  mockFetch.mockResolvedValue(searchResults);
  const results = await searchCities('Tok', 'test-key', mockFetch);
  expect(results.length).toBe(2);
  expect(results[0].name).toBe('Tokyo');
});

it('skips short queries', async () => {
  const results = await searchCities('T', 'test-key', mockFetch);
  expect(results).toEqual([]);
  expect(mockFetch).not.toHaveBeenCalled();
});
```

## Pitfalls

1. **Mock doesn't reset between tests:** Always create fresh mocks in `beforeEach`, not in the describe block.

2. **Mock vs real behavior:** The mock should return data in the **exact shape** the real API returns. Use the same fixture data in unit tests and integration tests.

3. **Rejected promises behave differently from thrown errors:** Use `mockRejectedValue()` not `mockImplementation(() => { throw ... })` to match async function behavior.

4. **Don't mock the URL builder:** `buildUrl()` from `weather.js` is part of the integration. Mock the network call, not the URL construction. This verifies the full flow: URL building → network call → response parsing → DOM update.

5. **Test the no-API-key guard:** This is a critical edge case that should show an error immediately without attempting a fetch. Verify the mock was NOT called in this case.