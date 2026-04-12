import os
import requests
from fastapi import APIRouter
from services.firestore_client import db

router = APIRouter()
MAPS_API_KEY = os.environ.get("MAPS_API_KEY") or os.environ.get("GOOGLE_MAPS_API_KEY", "")

GATES = {
    "gate-1": {"lat": 12.9716, "lng": 77.5946, "name": "Gate 1 - North"},
    "gate-2": {"lat": 12.9720, "lng": 77.5960, "name": "Gate 2 - East"},
    "gate-3": {"lat": 12.9710, "lng": 77.5935, "name": "Gate 3 - West"},
}

MOCK_ROUTING = [
    {"zone": "A1", "status": "CROWDED",  "occupancy_pct": 94},
    {"zone": "A2", "status": "MODERATE", "occupancy_pct": 71},
    {"zone": "B1", "status": "OPEN",     "occupancy_pct": 38},
    {"zone": "B2", "status": "OPEN",     "occupancy_pct": 29},
    {"zone": "C1", "status": "MODERATE", "occupancy_pct": 68},
    {"zone": "C2", "status": "CROWDED",  "occupancy_pct": 89},
    {"zone": "D1", "status": "OPEN",     "occupancy_pct": 44},
    {"zone": "D2", "status": "OPEN",     "occupancy_pct": 52},
]

def get_congestion_penalty(gate_id: str) -> int:
    if db is None:
        return {"gate-1": 20, "gate-2": 0, "gate-3": 5}.get(gate_id, 0)
    doc = db.collection("queues").document(gate_id).get()
    if doc.exists:
        level = doc.to_dict().get("queue_level", "low")
        return {"low": 0, "medium": 10, "high": 20}.get(level, 0)
    return 0

@router.get("/routing")
def list_routing():
    if db is None:
        return MOCK_ROUTING
    zones = db.collection("zones").stream()
    results = [{"zone": z.id, **z.to_dict()} for z in zones]
    return results if results else MOCK_ROUTING

@router.get("/route/best-gate")
def best_gate(user_lat: float, user_lng: float):
    origins = f"{user_lat},{user_lng}"
    destinations = "|".join(
        [f"{g['lat']},{g['lng']}" for g in GATES.values()]
    )
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origins}&destinations={destinations}"
        f"&mode=walking&key={MAPS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        results = []
        gate_ids = list(GATES.keys())
        for i, element in enumerate(data["rows"][0]["elements"]):
            gate_id = gate_ids[i]
            walk_seconds = element.get("duration", {}).get("value", 9999)
            walk_minutes = round(walk_seconds / 60, 1)
            penalty = get_congestion_penalty(gate_id)
            results.append({
                "gate_id": gate_id,
                "name": GATES[gate_id]["name"],
                "walk_minutes": walk_minutes,
                "congestion_penalty_minutes": penalty,
                "total_score": walk_minutes + penalty,
                "distance_text": element.get("distance", {}).get("text", "N/A"),
            })
        results.sort(key=lambda x: x["total_score"])
        return {"recommended": results[0], "all_gates": results}
    except Exception as e:
        return {
            "recommended": {"gate_id": "gate-2", "name": "Gate 2 - East", "walk_minutes": 3.5, "total_score": 3.5},
            "all_gates": [],
            "note": f"Maps API unavailable: {str(e)}"
        }
