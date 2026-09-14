import json
import random
import string
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from app.monitoring import capture_exception
from app.store import events
from app.tracking import track_event

app = FastAPI()


# dataclass with schema for event input
# Field == empty string with limitations
class EventInput(BaseModel):
    event: str = Field(..., min_length=3, max_length=64)
    user_id: str = Field(..., min_length=1, max_length=64)
    client_ts: datetime | None = None
    metadata: dict | None = None


# random id generation (str/int combination, limited list = 8)
def generate_event_id():
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"evt_{random_part}"


# find id / otherwise generate id
# add id to request.headers (internal storage)
# run next middleware / router / endpoint
# add id to response.headers (outbound HTTP header)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id", str(uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-request-Id"] = request_id

    return response


@app.post("/v1/events")
async def create_event(event_input: EventInput, request: Request):
    request_id = request.state.request_id

    try:
        if event_input.event == "explode":
            raise Exception("Deliberate explosion")  # noqa: TRY002 - deliberate test hook
        
        metadata = event_input.metadata or {}

        if len(json.dumps(metadata)) > 2028:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Metadata too large",
                        "details": {}
                    }
                }
            )
        
        event_id = generate_event_id()

        event_record = {
            "id": event_id,
            "received_at": datetime.now(UTC),
            "client_ts": event_input.client_ts or datetime.now(UTC),
            "event": event_input.event,
            "user_id": event_input.user_id,
            "metadata": metadata,
            "request_id": request_id 
        }

        events.append(event_record)

        track_event(
            event_input.user_id,
            event_input.event,
            metadata,
            request_id
        )

        return {"id": event_id, "accepted": True}

    except HTTPException:
        raise
    
    except Exception as e:  # noqa: BLE001 - catch-all is the point: log then 500
        capture_exception(
            e,
            request_id,
            "/v1/events",
            {"event": event_input.event, "user_id": event_input.user_id}
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Something went wrong",
                    "details": {}
                }
            }
        )


@app.get("/v1/events")
async def get_events(user_id: str, limit: int = 10):
    user_events = [e for e in events if e["user_id"] == user_id]
    user_events_sorted = sorted(
        user_events,
        key=lambda x: x['received_at'],
        reverse=True
    )

    return user_events_sorted[:limit]