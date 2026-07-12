---
name: api-testing
description: "API integration testing with SuperTest and contract testing"
version: 1.0.0
author: Charmander
platforms: [linux, macos]
metadata:
  charmander:
    tags: [testing, api, integration]
    team: charmander
---

# API Testing

Test REST and GraphQL endpoints for correctness, reliability, and contract fidelity.

## Tooling

| Tool | Use Case |
|------|----------|
| **SuperTest** | HTTP assertion testing alongside Jest/Vitest |
| **Postman / Newman** | Collection-based testing, CI runner |
| **Pact** | Consumer-driven contract testing |
| **MSW (Mock Service Worker)** | HTTP mocking for frontend tests |

## Test Patterns

### REST Endpoint Test

```js
const request = require('supertest')
const app = require('../app')

describe('GET /api/users', () => {
  it('returns paginated users', async () => {
    const res = await request(app)
      .get('/api/users')
      .query({ page: 1, limit: 10 })
      .set('Authorization', `Bearer ${token}`)
    
    expect(res.status).toBe(200)
    expect(res.body.data).toHaveLength(10)
    expect(res.body.pagination).toMatchObject({
      page: 1, totalPages: expect.any(Number)
    })
  })
})
```

### Auth Testing

- Test with valid token, expired token, malformed token, no token
- Verify proper 401/403 responses
- Test role-based access (admin vs user endpoints)

### Error Handling

- Validate error response shape: `{ error: string, code: string, details?: any }`
- Test 400 (bad input), 404 (not found), 409 (conflict), 422 (validation), 429 (rate limit)
- Ensure stack traces are never exposed in production

### Contract Testing (Pact)

1. Consumer defines expected interactions
2. Pact generates contract file
3. Provider verifies against contract
4. CI gate breaks if contract changes

## Checklist

- [ ] Happy path returns 200 with correct shape
- [ ] Validation errors return 4xx with clear messages
- [ ] Auth required endpoints reject unauthenticated
- [ ] Pagination works (page, limit, total, next/prev)
- [ ] Rate limiting tested (429 responses)
- [ ] Idempotency for PUT/DELETE
- [ ] Contract test passing
