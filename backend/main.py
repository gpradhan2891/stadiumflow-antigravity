import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routes import zones, queues, routing
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="StadiumFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow all origins (file://, localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zones.router)
app.include_router(queues.router)
app.include_router(routing.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}