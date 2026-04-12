import os
from pathlib import Path
from google.cloud import firestore

# Resolve service-account.json relative to THIS file's directory (backend/services/)
# so it works regardless of where uvicorn is launched from
BACKEND_DIR = Path(__file__).resolve().parent.parent

creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
# If it's a relative path, resolve it against the backend directory
if not os.path.isabs(creds_path):
    creds_path = str(BACKEND_DIR / creds_path)

if os.path.exists(creds_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    print(f"[Firestore] Using credentials: {creds_path}")
else:
    print(f"[Firestore] WARNING: credentials file not found at {creds_path} — will try Application Default Credentials")

PROJECT_ID = (
    os.environ.get("FIRESTORE_PROJECT_ID")
    or os.environ.get("GCP_PROJECT_ID")
    or "stadiumflow-antigravity"
)

try:
    db = firestore.Client(project=PROJECT_ID, database="(default)")
    print(f"[Firestore] Connected to project: {PROJECT_ID}")
except Exception as e:
    print(f"[Firestore] Init failed: {e}. Routes will return mock data.")
    db = None
