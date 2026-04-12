from fastapi import APIRouter
from services.firestore_client import db

router = APIRouter()

MOCK_QUEUES = [
    {"id": "gate-1", "zone_id": "Gate 1", "location_type": "Entry Gate",  "estimated_wait_minutes": 22, "queue_level": "high"},
    {"id": "gate-2", "zone_id": "Gate 2", "location_type": "Entry Gate",  "estimated_wait_minutes": 8,  "queue_level": "low"},
    {"id": "gate-3", "zone_id": "Gate 3", "location_type": "Entry Gate",  "estimated_wait_minutes": 5,  "queue_level": "low"},
    {"id": "gate-4", "zone_id": "Gate 4", "location_type": "Entry Gate",  "estimated_wait_minutes": 17, "queue_level": "medium"},
    {"id": "stand-a","zone_id": "Stand A","location_type": "Concession",  "estimated_wait_minutes": 12, "queue_level": "medium"},
    {"id": "stand-b","zone_id": "Stand B","location_type": "Concession",  "estimated_wait_minutes": 4,  "queue_level": "low"},
    {"id": "stand-c","zone_id": "Stand C","location_type": "Concession",  "estimated_wait_minutes": 19, "queue_level": "high"},
    {"id": "rest-n", "zone_id": "Restroom N","location_type": "Facility", "estimated_wait_minutes": 3,  "queue_level": "low"},
]

@router.get("/queues")
def list_queues():
    if db is None:
        return MOCK_QUEUES
    queues = db.collection("queues").stream()
    results = [{"id": q.id, **q.to_dict()} for q in queues]
    return results if results else MOCK_QUEUES

@router.post("/queues")
def update_queue(queue: dict):
    if db is None:
        return {"id": "mock", **queue}
    ref = db.collection("queues").document()
    ref.set(queue)
    return {"id": ref.id, **queue}
