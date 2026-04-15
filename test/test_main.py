import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.store import events


client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_store_before_test():
    events.clear()

# Test #1
def test_valid_event_accepted():
    payload = {
        "event": "button_clicked",
        "user_id": "u_123",
        "metadata": {"button": "signup"}
    }

    response = client.post("/v1/events", json=payload)

    data = response.json()

    assert response.status_code == 200
    assert data["accepted"] is True
    assert data["id"].startswith("evt_")

# Test #2
def test_metadata_too_large_rejected():
    large_metadata = {"data": "x" * 3000}

    payload = {
        "event": "button_clicked",
        "user_id": "u_123",
        "metadata": large_metadata
    }

    response = client.post("/v1/events", json=payload)
    data = response.json()

    assert response.status_code == 400
    assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"

# Test #3
def test_get_events_ordering_and_limit():
    # create multiple events for same user
    user_id = "u_order_test"

    for i in range(3):
        payload = {
            "event": f"event_{i}",
            "user_id": user_id
        }
        client.post("/v1/events", json=payload)

    # Fetch with limit=2
    response = client.get(f"/v1/events?user_id={user_id}&limit=2")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    # Most recent first: last created should be first
    assert data[0]["event"] == "event_2"
    assert data[1]["event"] == "event_1"


# Test #4
def test_request_id_provided():
    headers = {"X-Request-Id": "test-123"}
    payload = {
        "event": "button_clicked",
        "user_id": "u_reqid"
    }

    response = client.post("/v1/events", json=payload, headers=headers)

    # Check response header
    assert response.headers["X-request-Id"] == "test-123"

    # Check event stored in memory has same request_id
    assert events[-1]["request_id"] == "test-123"


# Test #5
def test_request_id_generated():
    payload = {
        "event": "button-clicked",
        "user_id": "u_reqid2"
    }

    response = client.post("/v1/events", json=payload)
    data = response.json()

    # Server should generate a non-empty request_id
    generated_id = response.headers.get("X-Request-Id")
    assert generated_id is not None
    assert generated_id != ""

    # Stored event matches the generated ID
    assert events[-1]["request_id"] == generated_id


# Test 6 Deliberate test
def test_deliberate_error_explode(monkeypatch):
    payload = {"event": "explode", "user_id": "u_err"}

    # Capture FANCYLOG output
    logged = {}
    def fake_print(prefix, log_json):
        if prefix == "FANCYLOG":
            logged["data"] = log_json

    monkeypatch.setattr("builtins.print", fake_print)

    response = client.post("/v1/events", json=payload)
    data = response.json()

    
    # API returns structured 500
    assert response.status_code == 500
    assert data["detail"]["error"]["code"] == "INTERNAL_ERROR"

    # FANCYLOG was called
    assert "Deliberate explosion" in logged["data"]
    assert "/v1/events" in logged["data"]
    assert '"event": "explode"' in logged["data"]