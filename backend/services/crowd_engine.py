"""
Crowd & routing engine service layer.

Previously a dead module — never imported by any route.
Now the authoritative service called by routes/routing.py (Fix 3).

Fixed field name: "occupancy" → "occupancy_pct" to match Zone model (Fix 5).
Accepts db as a parameter instead of using a global — testable (Fix 12).
"""
import logging
from typing import Optional

from constants import MOCK_ZONES, QUEUE_LEVEL_PENALTY_MINUTES

logger = logging.getLogger(__name__)


def get_zone_data(db) -> list[dict]:
    """
    Fetch all zone documents from Firestore.
    Falls back to MOCK_ZONES when db is None or on read failure.
    """
    if db is None:
        logger.debug("db is None — returning mock zone data.")
        return MOCK_ZONES

    try:
        docs = db.collection("zones").stream()
        results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        if results:
            return results
        logger.warning("Firestore zones collection is empty — returning mock data.")
        return MOCK_ZONES
    except Exception as exc:
        logger.error("Firestore zones read failed: %s — returning mock data.", exc)
        return MOCK_ZONES


def get_routing_recommendation(db) -> list[dict]:
    """
    Derive routing status for each zone based on occupancy_pct.
    Returns list of {zone, status, occupancy_pct} dicts.
    """
    zones = get_zone_data(db)
    results = []
    for z in zones:
        # Fix 5: field is occupancy_pct (was "occupancy" in old crowd_engine)
        pct = z.get("occupancy_pct", 0.0)
        if pct < 50:
            status = "OPEN"
        elif pct < 80:
            status = "MODERATE"
        else:
            status = "CROWDED"
        results.append({
            "zone":         z.get("zone") or z.get("id", "?"),
            "status":       status,
            "occupancy_pct": round(float(pct), 1),
        })
    return results


def get_queue_penalties(db) -> dict[str, int]:
    """
    Fix 8: Batch-fetch ALL queue documents in one Firestore call.
    Returns {gate_id: penalty_minutes} dict consumed by best_gate().
    Previously issued N sequential reads (one per gate) — now one read total.
    """
    if db is None:
        return {"gate-1": 20, "gate-2": 0, "gate-3": 5}

    try:
        docs   = db.collection("queues").stream()
        result = {}
        for doc in docs:
            level   = doc.to_dict().get("queue_level", "LOW").upper()
            penalty = QUEUE_LEVEL_PENALTY_MINUTES.get(level, 0)
            result[doc.id] = penalty
        return result
    except Exception as exc:
        logger.error("Firestore queues batch-read failed: %s", exc)
        return {}
