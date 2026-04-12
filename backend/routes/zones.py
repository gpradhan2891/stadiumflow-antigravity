from fastapi import APIRouter
from services.firestore_client import db

router = APIRouter()

MOCK_ZONES = [
    {"id": "A1", "zone": "A1", "status": "CROWDED",  "occupancy_pct": 94, "capacity": 500},
    {"id": "A2", "zone": "A2", "status": "MODERATE", "occupancy_pct": 71, "capacity": 500},
    {"id": "B1", "zone": "B1", "status": "OPEN",     "occupancy_pct": 38, "capacity": 500},
    {"id": "B2", "zone": "B2", "status": "OPEN",     "occupancy_pct": 29, "capacity": 500},
    {"id": "C1", "zone": "C1", "status": "MODERATE", "occupancy_pct": 68, "capacity": 500},
    {"id": "C2", "zone": "C2", "status": "CROWDED",  "occupancy_pct": 89, "capacity": 500},
    {"id": "D1", "zone": "D1", "status": "OPEN",     "occupancy_pct": 44, "capacity": 500},
    {"id": "D2", "zone": "D2", "status": "OPEN",     "occupancy_pct": 52, "capacity": 500},
]

@router.get("/zones")
def list_zones():
    if db is None:
        return MOCK_ZONES
    zones = db.collection("zones").stream()
    results = [{"id": z.id, **z.to_dict()} for z in zones]
    return results if results else MOCK_ZONES

@router.post("/zones")
def create_zone(zone: dict):
    if db is None:
        return {"id": "mock", **zone}
    ref = db.collection("zones").document()
    ref.set(zone)
    return {"id": ref.id, **zone}
