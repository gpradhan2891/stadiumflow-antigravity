"""
Single source of truth for mock data and shared configuration.
All routes import from here — no more duplicated/diverged mock datasets.
"""

# Fix 5: MOCK_ZONES — was duplicated verbatim in zones.py and routing.py
MOCK_ZONES: list[dict] = [
    {"id": "A1", "zone": "A1", "status": "CROWDED",  "occupancy_pct": 94.0, "capacity": 500},
    {"id": "A2", "zone": "A2", "status": "MODERATE", "occupancy_pct": 71.0, "capacity": 500},
    {"id": "B1", "zone": "B1", "status": "OPEN",     "occupancy_pct": 38.0, "capacity": 500},
    {"id": "B2", "zone": "B2", "status": "OPEN",     "occupancy_pct": 29.0, "capacity": 500},
    {"id": "C1", "zone": "C1", "status": "MODERATE", "occupancy_pct": 68.0, "capacity": 500},
    {"id": "C2", "zone": "C2", "status": "CROWDED",  "occupancy_pct": 89.0, "capacity": 500},
    {"id": "D1", "zone": "D1", "status": "OPEN",     "occupancy_pct": 44.0, "capacity": 500},
    {"id": "D2", "zone": "D2", "status": "OPEN",     "occupancy_pct": 52.0, "capacity": 500},
]

# Fix 5: MOCK_QUEUES — was duplicated in queues.py and crowd_engine.py
MOCK_QUEUES: list[dict] = [
    {"id": "gate-1",  "zone_id": "Gate 1",     "location_type": "Entry Gate", "estimated_wait_minutes": 22, "queue_level": "HIGH"},
    {"id": "gate-2",  "zone_id": "Gate 2",     "location_type": "Entry Gate", "estimated_wait_minutes": 8,  "queue_level": "LOW"},
    {"id": "gate-3",  "zone_id": "Gate 3",     "location_type": "Entry Gate", "estimated_wait_minutes": 5,  "queue_level": "LOW"},
    {"id": "gate-4",  "zone_id": "Gate 4",     "location_type": "Entry Gate", "estimated_wait_minutes": 17, "queue_level": "MEDIUM"},
    {"id": "stand-a", "zone_id": "Stand A",    "location_type": "Concession", "estimated_wait_minutes": 12, "queue_level": "MEDIUM"},
    {"id": "stand-b", "zone_id": "Stand B",    "location_type": "Concession", "estimated_wait_minutes": 4,  "queue_level": "LOW"},
    {"id": "stand-c", "zone_id": "Stand C",    "location_type": "Concession", "estimated_wait_minutes": 19, "queue_level": "HIGH"},
    {"id": "rest-n",  "zone_id": "Restroom N", "location_type": "Facility",   "estimated_wait_minutes": 3,  "queue_level": "LOW"},
]

# Fix 5: GATES — was hardcoded only in routing.py, now shared
GATES: dict[str, dict] = {
    "gate-1": {"lat": 12.9716, "lng": 77.5946, "name": "Gate 1 - North"},
    "gate-2": {"lat": 12.9720, "lng": 77.5960, "name": "Gate 2 - East"},
    "gate-3": {"lat": 12.9710, "lng": 77.5935, "name": "Gate 3 - West"},
}

# Fix 8: Congestion penalty map — single definition
QUEUE_LEVEL_PENALTY_MINUTES: dict[str, int] = {
    "LOW":    0,
    "MEDIUM": 10,
    "HIGH":   20,
}

# Cache TTL in seconds
CACHE_TTL_ZONES_S:  int = 60
CACHE_TTL_QUEUES_S: int = 60
CACHE_TTL_MAPS_S:   int = 300   # Maps API rounded-coord cache: 5 min
