import os
import json
from google.cloud import pubsub_v1
from services.firestore_client import db

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "stadiumflow-antigravity")

def process_staff_update(message):
    """Handle staff queue updates: {zone_id, queue_level, location_type}"""
    try:
        data = json.loads(message.data.decode("utf-8"))
        zone_id = data.get("zone_id")
        queue_level = data.get("queue_level", "low")  # low/medium/high
        location_type = data.get("location_type", "general")

        wait_map = {"low": 5, "medium": 15, "high": 25}
        wait_minutes = wait_map.get(queue_level, 5)

        db.collection("queues").document(zone_id).set({
            "zone_id": zone_id,
            "queue_level": queue_level,
            "estimated_wait_minutes": wait_minutes,
            "location_type": location_type,
            "last_updated": "staff"
        }, merge=True)

        print(f"[staff-update] Zone {zone_id}: {queue_level} ({wait_minutes} min)")
        message.ack()
    except Exception as e:
        print(f"Error processing staff update: {e}")
        message.nack()


def process_sensor_event(message):
    """Handle sensor events: {zone_id, event_type: entry|exit}"""
    try:
        data = json.loads(message.data.decode("utf-8"))
        zone_id = data.get("zone_id")
        event_type = data.get("event_type")  # entry or exit

        zone_ref = db.collection("zones").document(zone_id)
        zone = zone_ref.get()
        current = zone.to_dict() if zone.exists else {"occupancy": 0, "capacity": 100}

        occupancy = current.get("occupancy", 0)
        capacity = current.get("capacity", 100)

        if event_type == "entry":
            occupancy = min(occupancy + 1, capacity)
        elif event_type == "exit":
            occupancy = max(occupancy - 1, 0)

        ratio = occupancy / capacity
        congestion = "low" if ratio < 0.5 else "medium" if ratio < 0.8 else "high"

        zone_ref.set({
            "zone_id": zone_id,
            "occupancy": occupancy,
            "capacity": capacity,
            "congestion_level": congestion
        }, merge=True)

        print(f"[sensor] Zone {zone_id}: {occupancy}/{capacity} ({congestion})")
        message.ack()
    except Exception as e:
        print(f"Error processing sensor event: {e}")
        message.nack()


def start_subscribers():
    subscriber = pubsub_v1.SubscriberClient()

    staff_sub = subscriber.subscription_path(PROJECT_ID, "staff-updates-sub")
    sensor_sub = subscriber.subscription_path(PROJECT_ID, "sensor-events-sub")

    subscriber.subscribe(staff_sub, callback=process_staff_update)
    subscriber.subscribe(sensor_sub, callback=process_sensor_event)

    print("Crowd engine listening for updates...")
    import time
    while True:
        time.sleep(60)


if __name__ == "__main__":
    start_subscribers()