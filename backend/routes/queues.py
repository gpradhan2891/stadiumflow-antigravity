from fastapi import APIRouter
from services.firestore_client import db

router = APIRouter()

@router.get("/queues")
def list_queues():
    queues = db.collection("queues").stream()
    return [{"id": q.id, **q.to_dict()} for q in queues]

@router.post("/queues")
def update_queue(queue: dict):
    ref = db.collection("queues").document()
    ref.set(queue)
    return {"id": ref.id, **queue}