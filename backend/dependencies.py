"""
Shared FastAPI dependencies.
  - get_db()        : injects the Firestore client (or None) into any route
  - verify_api_key(): guards write endpoints with X-API-Key header
"""
import os
import logging
from typing import Optional

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from services.firestore_client import get_db as _get_db_singleton

logger = logging.getLogger(__name__)

# ── Fix 12: Firestore dependency ──────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that returns the Firestore client.
    Returns None when the client is unavailable; routes fall back to mock data.
    Usage:  db = Depends(get_db)
    Tests:  app.dependency_overrides[get_db] = lambda: None
    """
    return _get_db_singleton()


# ── Fix 2: API-key guard for write endpoints ──────────────────────────────────
_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: Optional[str] = Security(_API_KEY_HEADER)) -> str:
    """
    Validates the X-API-Key header against the STADIUMFLOW_API_KEY env var.
    Raises 403 on missing or wrong key.
    Usage:  _: str = Depends(verify_api_key)
    """
    expected = os.environ.get("STADIUMFLOW_API_KEY", "")
    if not expected:
        logger.warning("STADIUMFLOW_API_KEY env var is not set — write endpoints are unprotected!")
    if not api_key or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key.",
        )
    return api_key
