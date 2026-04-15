import logging
from threading import Lock

from cachetools    import TTLCache
from fastapi       import APIRouter, Depends

from constants     import MOCK_ZONES, CACHE_TTL_ZONES_S
from dependencies  import get_db, verify_api_key
from models        import Zone

router = APIRouter()
logger = logging.getLogger(__name__)

# Fix 13: 60-second TTL cache — one Firestore stream per minute max
_cache: TTLCache = TTLCache(maxsize=1, ttl=CACHE_TTL_ZONES_S)
_lock            = Lock()


def _fetch_from_firestore(db) -> list[dict]:
    """Single Firestore read; result stored in TTL cache by caller."""
    docs    = db.collection("zones").stream()
    results = [{"id": z.id, **z.to_dict()} for z in docs]
    return results if results else MOCK_ZONES


@router.get("/zones", response_model=list[Zone])
def list_zones(db=Depends(get_db)):           # Fix 12: db injected, not global
    """List all stadium zones with current occupancy and status."""
    if db is None:
        logger.debug("db unavailable — returning mock zones.")
        return MOCK_ZONES

    with _lock:
        if "data" in _cache:
            logger.debug("zones cache hit.")
            return _cache["data"]                # Fix 13: serve from cache

    try:
        data = _fetch_from_firestore(db)
        with _lock:
            _cache["data"] = data
        return data
    except Exception as exc:
        logger.error("zones Firestore read failed: %s", exc)
        return MOCK_ZONES


@router.post("/zones", response_model=Zone, status_code=201)
def create_zone(
    zone: Zone,
    db  = Depends(get_db),
    _   = Depends(verify_api_key),             # Fix 2: auth guard on write
):
    """Create or update a zone record in Firestore."""
    if db is None:
        logger.warning("db unavailable — returning mock zone (no write).")
        return {"id": "mock", **zone.model_dump()}

    try:
        ref = db.collection("zones").document()
        ref.set(zone.model_dump(exclude={"id"}))
        with _lock:
            _cache.clear()                       # Fix 13: invalidate on write
        logger.info("Zone created: %s", ref.id)
        return {"id": ref.id, **zone.model_dump(exclude={"id"})}
    except Exception as exc:
        logger.error("Zone create failed: %s", exc)
        raise
