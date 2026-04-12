import os
from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(__file__), "..", "service-account.json"
)

db = firestore.Client(
    project="stadiumflow-antigravity",
    database="(default)"
)