"""
Lazy-initialised Firestore client.

The client is created on the FIRST call to get_db(), not at import time.
This prevents silent db=None degradation on cold-start credential delays.

  get_db() -> Optional[firestore.Client]
      Returns the singleton client, or None if unavailable.
      None-safe: all callers fall back to mock data gracefully.
"""
import os
import logging
from pathlib import Path
from typing import Optional

from google.cloud import firestore

logger = logging.getLogger(__name__)

_db:          Optional[firestore.Client] = None
_initialised: bool = False

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ID  = (
    os.environ.get("FIRESTORE_PROJECT_ID")
    or os.environ.get("GCP_PROJECT_ID")
    or "stadiumflow-antigravity"
)


def _resolve_credentials() -> None:
    """Resolve and set GOOGLE_APPLICATION_CREDENTIALS if a local key file exists."""
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
    if not os.path.isabs(creds_path):
        creds_path = str(BACKEND_DIR / creds_path)
    if os.path.exists(creds_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        logger.info("Firestore credentials resolved: %s", creds_path)
    else:
        logger.warning(
            "Credentials file not found at %s — falling back to Application Default Credentials.",
            creds_path,
        )


# Fix 4: Lazy initialisation — runs only on first get_db() call.
def _initialise() -> None:
    global _db, _initialised
    _initialised = True          # mark true even on failure to avoid retry storms
    _resolve_credentials()
    try:
        _db = firestore.Client(project=PROJECT_ID, database="(default)")
        logger.info("Firestore connected to project: %s", PROJECT_ID)
    except Exception as exc:
        logger.error("Firestore init failed: %s. Routes will return mock data.", exc)
        _db = None


def get_db() -> Optional[firestore.Client]:
    """
    Return the Firestore client singleton.
    Initialises lazily on first call; safe to call from any thread.
    """
    if not _initialised:
        _initialise()
    return _db
