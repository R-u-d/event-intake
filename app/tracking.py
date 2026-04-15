import json
from datetime import datetime, UTC

# event-tracker
def track_event(user_id, event_name, properties, request_id):
    payload = {
        "type": "track",
        "userId": user_id,
        "event": event_name,
        "properties": properties,
        "context": {
            "requestId": request_id,
            "source": "event-intake-service"
        },
        "timestamp": datetime.now(UTC).isoformat()
    }

    print("TRACK:", json.dumps(payload))
