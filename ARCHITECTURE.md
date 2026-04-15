# Event Intake Service – Architecture Overview

## High-Level Request Flow

Client → POST /v1/events  
↓  
Middleware assigns or propagates request_id  
↓  
Pydantic validates request schema  
↓  
Business Logic:
  - Enforce metadata size constraint
  - Generate server-side event ID
  - Persist event in in-memory store
  - Invoke tracking seam
↓  
Return response:
  - 200 OK on success
  - 400 VALIDATION_ERROR on validation failure
  - 500 INTERNAL_ERROR on unexpected failure

---

## GET /v1/events

- Filters events by user_id
- Sorted by server-side `received_at` descending
- Supports optional `limit` (default 10)

---

## Design Decisions

### 1. Request Correlation

A middleware attaches a `request_id` to:
- `request.state`
- response headers (`X-Request-Id`)
- stored event record
- tracking and monitoring payloads

This enables end-to-end traceability across logs and stored data.

---

### 2. In-Memory Storage

Events are stored in a module-level list.

Advantages:
- Simplicity
- Zero setup
- Deterministic for tests

Limitations:
- No persistence across restarts
- Not safe for multi-process deployment

---

### 3. Tracking and Monitoring as Seams

Tracking (`track_event`) and monitoring (`capture_exception`) are isolated modules.

They simulate third-party integrations but:
- Do not block API responses
- Do not affect event persistence
- Are easily replaceable with real vendors

This maintains separation of concerns.

---

## Failure Modes

1. Schema validation failure → 422 (handled automatically by FastAPI/Pydantic)
2. Business validation failure (e.g. metadata too large) → 400 VALIDATION_ERROR
3. Unexpected exception → 500 INTERNAL_ERROR
   - Captured by monitoring
   - Event not persisted

Tracking failures currently log only and do not block the request.
