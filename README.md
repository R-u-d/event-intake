# 📦 Project Structure

```
event-intake/
├── app/
│   ├── main.py        # API entry point
│   ├── store.py       # In-memory storage logic
│   ├── tracking.py    # Request tracking and correlation
│   └── monitoring.py  # Monitoring hooks
├── tests/
│   └── test_main.py   # API tests
├── pytest.ini
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
└── TESTING.md
```

---

## ⚙️ Requirements
Python 3.10+
pip

### Install dependencies:

`pip install -r requirements.txt`


## ▶️ Running the Service

### Start the development server:

`uvicorn app.main:app --reload`


### The service will be available at:

API: http://127.0.0.1:8000
Interactive Docs (Swagger UI): http://127.0.0.1:8000/docs


### 📡 API Overview

| Method | Endpoint	| Description |
| ----------- | ----------- | ----------- |
| POST | /v1/events | Submit a new event |
| GET | /v1/events | Retrieve events filtered by user |


### 📥 Example Requests

#### Create Event

```bash
curl -X POST "http://127.0.0.1:8000/v1/events" \
     -H "Content-Type: application/json" \
     -H "X-Request-Id: my-request-1" \
     -d '{
           "event": "button_clicked",
           "user_id": "u_123",
           "metadata": { "button": "signup" }
         }'
```

#### Response:
```json
{
  "id": "evt_a8K2jd91",
  "accepted": true
}
```
#### Get Events for a User
```bash
curl "http://127.0.0.1:8000/v1/events?user_id=u_123"
```

#### Response:

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

---

## 🧪 Running Tests

Run the test suite:

`pytest -v`

All tests should pass.
See TESTING.md for more details.

---

## ⚖️ Design Decisions & Trade-offs

In-memory storage is used for simplicity and fast iteration
→ Not suitable for production persistence
Request IDs enable traceability across requests and systems
Modular structure allows easy replacement of components (e.g. database, logging)

---

## 🔮 Future Improvements

Replace in-memory storage with a persistent database (e.g. PostgreSQL)
Add pagination and filtering for event queries
Implement authentication and rate limiting
Introduce structured logging and metrics (e.g. Prometheus)
Support asynchronous processing (e.g. message queues

---

## 📚 Documentation

Architecture details: ARCHITECTURE.md
Testing approach: TESTING.md

---

## 📌 Summary

This project demonstrates backend engineering fundamentals including API design, validation, observability, testing, and modular service architecture. It is designed to be simple, extensible, and representative of real-world event ingestion systems.
