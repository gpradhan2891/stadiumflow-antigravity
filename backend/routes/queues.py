import logging
from threading import Lock

from cachetools    import TTLCache
from fastapi       import APIRouter, Depends

from constants     import MOCK_QUEUES, CACHE_TTL_QUEUES_S
from dependencies  import get_db, verify_api_key
from models        import Queue

router = APIRouter()
logger = logging.getLogger(__name__)

# Fix 13: 60-second TTL cache on queue reads
_cache: TTLCache = TTLCache(maxsize=1, ttl=CACHE_TTL_QUEUES_S)
_lock            = Lock()


def _fetch_from_firestore(db) -> list[dict]:
    docs    = db.collection("queues").stream()
    results = [{"id": q.id, **q.to_dict()} for q in docs]
    return results if results else MOCK_QUEUES


@router.get("/queues", response_model=list[Queue])
def list_queues(db=Depends(get_db)):          # Fix 12: injected db
    """List all queue locations with current wait times."""
    if db is None:
        logger.debug("db unavailable — returning mock queues.")
        return MOCK_QUEUES

    with _lock:
        if "data" in _cache:
            logger.debug("queues cache hit.")
            return _cache["data"]               # Fix 13: cache hit

    try:
        data = _fetch_from_firestore(db)
        with _lock:
            _cache["data"] = data
        return data
    except Exception as exc:
        logger.error("queues Firestore read failed: %s", exc)
        return MOCK_QUEUES


@router.post("/queues", response_model=Queue, status_code=201)
def update_queue(
    queue: Queue,
    db   = Depends(get_db),
    _    = Depends(verify_api_key),            # Fix 2: auth guard on write
):
    """Create or update a queue record in Firestore."""
    if db is None:
        logger.warning("db unavailable — mock queue returned (no write).")
        return {"id": "mock", **queue.model_dump()}

    try:
        ref = db.collection("queues").document()
        ref.set(queue.model_dump(exclude={"id"}))
        with _lock:
            _cache.clear()                      # Fix 13: invalidate on write
        logger.info("Queue updated: %s", ref.id)
        return {"id": ref.id, **queue.model_dump(exclude={"id"})}
    except Exception as exc:
        logger.error("Queue update failed: %s", exc)
        raise
