import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from routes import zones, queues

app = FastAPI()

app.include_router(zones.router)
app.include_router(queues.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}