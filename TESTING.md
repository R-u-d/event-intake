# Event Intake Service – Testing

## Test Strategy

Tests are written using pytest and validate behavior at the HTTP layer using FastAPI's TestClient.

The in-memory store is reset between tests to ensure isolation.

---

## What Is Tested

1. Successful POST /v1/events:
   - Returns 200
   - Returns event ID
   - accepted = true
   - Event is persisted

2. Metadata size validation:
   - Returns 400
   - Error code = VALIDATION_ERROR
   - Event not persisted

3. GET /v1/events:
   - Filters by user_id
   - Sorted descending by received_at
   - Respects limit parameter

4. Request ID propagation:
   - Custom X-Request-Id header is preserved
   - Stored event contains request_id

5. Internal error handling:
   - Deliberate failure ("explode")
   - Returns 500 INTERNAL_ERROR
   - Error captured by monitoring
   - Event not stored

6. Schema validation:
   - Event name below the 3-character minimum returns 422
   - Missing user_id returns 422
   - GET without user_id returns 422
   - Nothing is persisted in any of these cases

7. Query isolation:
   - An unknown user_id returns an empty list, not a 404
   - One user's events never appear in another user's list

8. Size limit boundary:
   - Metadata serialising to exactly 2028 characters is still accepted
   - The rejection path is covered separately (case 2)

9. Health endpoint:
   - Returns 200 and the current number of stored events

---

## Out of Scope

- Concurrency and multi-worker safety
- Persistent storage durability
- External tracking vendor reliability
- Authentication / rate limiting
- Load or performance testing

---

## Future Improvements

- Replace in-memory store with database (e.g., PostgreSQL)
- Introduce asynchronous queue for tracking
- Add structured logging framework
- Add coverage reporting to the existing CI pipeline
- Property-based tests for the metadata size boundary
