import os
from google.cloud import firestore

# On Cloud Run: uses default service account automatically (no JSON needed)
# Locally: set GOOGLE_APPLICATION_CREDENTIALS in your .env file
creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if creds_path and os.path.exists(creds_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

PROJECT_ID = os.environ.get("FIRESTORE_PROJECT_ID", "stadiumflow-antigravity")

try:
    db = firestore.Client(project=PROJECT_ID, database="(default)")
except Exception as e:
    print(f"[WARNING] Firestore init failed: {e}. Using mock mode.")
    db = None
