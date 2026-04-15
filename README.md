# Event Intake Service

A minimal backend service for submitting and retrieving user events.

Built with FastAPI.  
Includes request validation, in-memory storage, tracking and monitoring seams, request correlation, and automated tests.

---

## Project Structure

event-intake
├── app
│ ├── main.py
│ ├── store.py
│ ├── tracking.py
│ └── monitoring.py

├── tests
│ └── test_main.py
├── pytest.ini
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
└── TESTING.md


---

## Requirements

- Python 3.10+
- pip

Install dependencies:

```bash
pip install -r requirements.txt

Run the Server

From project root:

uvicorn app.main:app --reload

Server runs at:

http://127.0.0.1:8000

Interactive API docs available at:

http://127.0.0.1:8000/docs

Example curl Commands
POST an Event

curl -X POST "http://127.0.0.1:8000/v1/events" \
     -H "Content-Type: application/json" \
     -H "X-Request-Id: my-request-1" \
     -d '{
           "event": "button_clicked",
           "user_id": "u_123",
           "metadata": { "button": "signup" }
         }'

Response:

{
  "id": "evt_a8K2jd91",
  "accepted": true
}

GET Events for a User

curl "http://127.0.0.1:8000/v1/events?user_id=u_123"

Response:

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

Run Tests

From project root:

pytest

All tests should pass.
