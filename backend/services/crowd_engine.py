import os
from .firestore_client import db

def get_zone_data():
    if db is None:
        return [{"zone": "A", "occupancy": 45, "capacity": 100},
                {"zone": "B", "occupancy": 78, "capacity": 100},
                {"zone": "C", "occupancy": 30, "capacity": 100}]
    try:
        zones_ref = db.collection("zones")
        docs = zones_ref.stream()
        return [{"zone": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        print(f"[WARNING] Firestore read failed: {e}")
        return [{"zone": "A", "occupancy": 45, "capacity": 100},
                {"zone": "B", "occupancy": 78, "capacity": 100},
                {"zone": "C", "occupancy": 30, "capacity": 100}]

def get_routing_recommendation():
    zones = get_zone_data()
    recommendations = []
    for z in zones:
        pct = z.get("occupancy", 0) / z.get("capacity", 100) * 100
        if pct < 50:
            status = "OPEN"
        elif pct < 80:
            status = "MODERATE"
        else:
            status = "CROWDED"
        recommendations.append({"zone": z["zone"], "status": status, "occupancy_pct": round(pct, 1)})
    return recommendations
