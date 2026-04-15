"""
StadiumFlow API — entrypoint.

Fix 1:  CORS origins driven by ALLOWED_ORIGINS env var.
        Falls back to ["*"] only when APP_ENV=development (never silently in prod).
Fix 9:  sys.path hack removed. Set PYTHONPATH=. in your Dockerfile / Procfile.
Fix 10: Structured JSON-ready logging configured at startup.
"""
import logging
import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import zones, queues, routing

# Fix 10: configure logging before anything else
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title       = "StadiumFlow API",
    description = "Real-time stadium crowd management API",
    version     = "2.0.0",
)

# Fix 1: CORS — env-var driven, not hardcoded wildcard in production
_env            = os.environ.get("APP_ENV", "production").lower()
_raw_origins    = os.environ.get("ALLOWED_ORIGINS", "")
_allowed_origins: list[str]

if _raw_origins:
    _allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
    logger.info("CORS origins: %s", _allowed_origins)
elif _env == "development":
    _allowed_origins = ["*"]
    logger.warning("CORS is open (*) — APP_ENV=development. Do NOT use in production.")
else:
    # Prod with no ALLOWED_ORIGINS set: lock down entirely rather than silently open
    _allowed_origins = []
    logger.error(
        "ALLOWED_ORIGINS env var is not set and APP_ENV=%s. "
        "All cross-origin requests will be blocked. "
        "Set ALLOWED_ORIGINS=https://your-domain.com to fix this.",
        _env,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins     = _allowed_origins,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(zones.router)
app.include_router(queues.router)
app.include_router(routing.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "env": _env}
