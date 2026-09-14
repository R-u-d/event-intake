# event-intake

A small HTTP service that accepts analytics events, stores them, and hands them
back per user. FastAPI, in-memory store, no external dependencies at runtime.

## Problem

An event intake endpoint has to do three things well before it does anything else:
reject malformed input at the boundary, stay traceable when a request goes wrong,
and never lose the correlation between what a client sent and what got logged.
This service does those three and stops there.

## Decisions

**Request correlation is middleware, not endpoint code.** Every request carries an
`X-Request-Id` — propagated if the client sent one, generated otherwise. The same id
lands in the response header, in the stored event, and in every log line. One id ties
a client complaint to a stack trace.

**Validation is split in two.** Schema shape (`event` length, required `user_id`) is
Pydantic's job and returns 422. Business rules (metadata under 2 KB) return 400 with a
structured `VALIDATION_ERROR` body. Clients can tell "you sent the wrong shape" from
"we won't take this".

**Tracking and monitoring are seams, not integrations.** `track_event` and
`capture_exception` are separate modules that print structured JSON. They are shaped
like the vendor calls they stand in for, so swapping in a real one touches one file
and no tests.

**Storage is a module-level list.** Deliberate: zero setup, deterministic tests, and
the seam for a real database is the only thing that matters at this size. It does not
survive a restart and is not multi-process safe. Both are stated, neither is hidden.

**Unexpected failures return 500 and store nothing.** The catch-all around the handler
logs the exception with its request id and safe input, then returns a structured error.
A failed request leaves no partial event behind — there is a test for that.

## Status

Working. 14 tests, `ruff` clean, CI runs both on every push.

| Method | Endpoint      | Description                |
| ------ | ------------- | -------------------------- |
| POST   | `/v1/events`  | Submit an event            |
| GET    | `/v1/events`  | List events for a user     |
| GET    | `/health`     | Liveness and store size    |

### Run it

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Or with Docker:

```bash
docker build -t event-intake .
docker run -p 8000:8000 event-intake
```

API on `http://127.0.0.1:8000`, Swagger UI on `/docs`.

### Try it

```bash
curl -X POST "http://127.0.0.1:8000/v1/events" \
     -H "Content-Type: application/json" \
     -H "X-Request-Id: my-request-1" \
     -d '{"event": "button_clicked", "user_id": "u_123", "metadata": {"button": "signup"}}'
```

```json
{ "id": "evt_a8K2jd91", "accepted": true }
```

```bash
curl "http://127.0.0.1:8000/v1/events?user_id=u_123"
```

```json
[
  {
    "id": "evt_a8K2jd91",
    "received_at": "2026-02-14T12:00:00Z",
    "client_ts": "2026-02-14T12:00:00Z",
    "event": "button_clicked",
    "user_id": "u_123",
    "metadata": { "button": "signup" },
    "request_id": "my-request-1"
  }
]
```

### Test it

```bash
pytest -q
ruff check .
```

## Not built

- Persistence. The store is a list; a database goes behind `app/store.py`.
- Authentication and rate limiting. There is no trust boundary beyond schema validation.
- Asynchronous delivery. Tracking calls run inline and only log.

## Documentation

Request flow and failure modes: [ARCHITECTURE.md](ARCHITECTURE.md) ·
Test strategy and scope: [TESTING.md](TESTING.md)

## License

MIT — see [LICENSE](LICENSE).
