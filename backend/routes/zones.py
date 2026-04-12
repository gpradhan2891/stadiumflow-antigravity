from fastapi import APIRouter
from services.firestore_client import db

router = APIRouter()

@router.get("/zones")
def list_zones():
    zones = db.collection("zones").stream()
    return [{"id": z.id, **z.to_dict()} for z in zones]

@router.post("/zones")
def create_zone(zone: dict):
    ref = db.collection("zones").document()
    ref.set(zone)
    return {"id": ref.id, **zone}