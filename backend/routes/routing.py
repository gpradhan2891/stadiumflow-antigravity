"""
/routing  — zone list for heatmap/routing decisions  (Fix 3: uses crowd_engine)
/route/best-gate — best gate recommendation           (Fix 6: async httpx)
                                                      (Fix 8: batch Firestore read)
                                                      (Fix 14: Maps API TTL cache)
"""
import asyncio
import logging
import os
from threading import Lock

import httpx
from cachetools import TTLCache
from fastapi    import APIRouter, Depends

from constants           import GATES, MOCK_ZONES, CACHE_TTL_ZONES_S, CACHE_TTL_MAPS_S
from dependencies        import get_db
from models              import Zone, GateResult, BestGateResponse
from services.crowd_engine import get_routing_recommendation, get_queue_penalties

router     = APIRouter()
logger     = logging.getLogger(__name__)
MAPS_KEY   = os.environ.get("MAPS_API_KEY") or os.environ.get("GOOGLE_MAPS_API_KEY", "")

# Fix 13: routing list TTL cache (60 s)
_route_cache: TTLCache = TTLCache(maxsize=1, ttl=CACHE_TTL_ZONES_S)
_route_lock            = Lock()

# Fix 14: Maps API cache keyed by rounded (lat, lng) — 5-min TTL
_maps_cache: TTLCache  = TTLCache(maxsize=128, ttl=CACHE_TTL_MAPS_S)
_maps_lock             = Lock()


@router.get("/routing", response_model=list[Zone])
def list_routing(db=Depends(get_db)):         # Fix 12: injected db
    """
    List all zones for routing decisions.
    Fix 3: Delegates to crowd_engine — no more duplicated Firestore logic.
    Fix 13: TTL-cached for 60 seconds.
    """
    with _route_lock:
        if "data" in _route_cache:
            logger.debug("routing cache hit.")
            return _route_cache["data"]

    try:
        data = get_routing_recommendation(db)  # Fix 3: crowd_engine owns this
        with _route_lock:
            _route_cache["data"] = data
        return data
    except Exception as exc:
        logger.error("routing list failed: %s", exc)
        return MOCK_ZONES


@router.get("/route/best-gate", response_model=BestGateResponse)
async def best_gate(user_lat: float, user_lng: float, db=Depends(get_db)):
    """
    Return best gate based on walk time + live congestion penalty.

    Fix 6:  Uses httpx.AsyncClient — non-blocking Maps API call.
    Fix 8:  Batch-fetches ALL queue penalties in one Firestore read
            (was N sequential reads, one per gate).
    Fix 14: Maps API response cached by rounded coordinates (3dp ≈ 100m).
    """
    # Fix 14: round to 3 decimal places for cache key (~100 m granularity)
    cache_key = (round(user_lat, 3), round(user_lng, 3))
    with _maps_lock:
        if cache_key in _maps_cache:
            logger.debug("Maps API cache hit for key %s", cache_key)
            return _maps_cache[cache_key]

    # Fix 8: one batch read for all gates — runs in threadpool from async context
    penalties: dict[str, int] = await asyncio.to_thread(get_queue_penalties, db)

    origins      = f"{user_lat},{user_lng}"
    destinations = "|".join(f"{g['lat']},{g['lng']}" for g in GATES.values())
    url = (
        "https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origins}&destinations={destinations}"
        f"&mode=walking&key={MAPS_KEY}"
    )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:  # Fix 6: async
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        results:   list[GateResult] = []
        gate_ids = list(GATES.keys())

        for i, element in enumerate(data["rows"][0]["elements"]):
            gate_id      = gate_ids[i]
            walk_seconds = element.get("duration", {}).get("value", 9999)
            walk_minutes = round(walk_seconds / 60, 1)
            penalty      = penalties.get(gate_id, 0)   # Fix 8: from batch dict
            results.append(GateResult(
                gate_id=gate_id,
                name=GATES[gate_id]["name"],
                walk_minutes=walk_minutes,
                congestion_penalty_minutes=penalty,
                total_score=walk_minutes + penalty,
                distance_text=element.get("distance", {}).get("text", "N/A"),
            ))

        results.sort(key=lambda x: x.total_score)
        response = BestGateResponse(recommended=results[0], all_gates=results)

        # Fix 14: store in Maps cache
        with _maps_lock:
            _maps_cache[cache_key] = response
        return response

    except Exception as exc:
        logger.warning("Maps API unavailable (%s) — returning fallback gate.", exc)
        fallback = BestGateResponse(
            recommended=GateResult(
                gate_id="gate-2",
                name="Gate 2 - East",
                walk_minutes=3.5,
                congestion_penalty_minutes=0,
                total_score=3.5,
                distance_text="N/A",
            ),
            all_gates=[],
            note=f"Maps API unavailable: {exc}",
        )
        return fallback
