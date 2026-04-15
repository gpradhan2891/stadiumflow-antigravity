from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


# Fix 7: Both enums now uppercase for consistency.
# Pydantic validators below normalise incoming lowercase values automatically.
class ZoneStatus(str, Enum):
    OPEN     = "OPEN"
    MODERATE = "MODERATE"
    CROWDED  = "CROWDED"


class QueueLevel(str, Enum):
    LOW    = "LOW"      # was "low" — now uppercase, matching ZoneStatus
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"


class Zone(BaseModel):
    id:           Optional[str] = None
    zone:         str
    status:       ZoneStatus
    occupancy_pct: float = Field(ge=0, le=100)
    capacity:     int   = Field(gt=0)

    # Fix 7: normalise status strings from Firestore ("crowded" → "CROWDED")
    @field_validator("status", mode="before")
    @classmethod
    def normalise_status(cls, v: str) -> str:
        return str(v).upper()


class Queue(BaseModel):
    id:                     Optional[str] = None
    zone_id:                str
    location_type:          str
    estimated_wait_minutes: int = Field(ge=0)
    queue_level:            QueueLevel

    # Fix 7: normalise queue_level strings from Firestore ("high" → "HIGH")
    @field_validator("queue_level", mode="before")
    @classmethod
    def normalise_queue_level(cls, v: str) -> str:
        return str(v).upper()


class GateResult(BaseModel):
    gate_id:                    str
    name:                       str
    walk_minutes:               float
    congestion_penalty_minutes: int
    total_score:                float
    distance_text:              str


class BestGateResponse(BaseModel):
    recommended: GateResult
    all_gates:   list[GateResult]
    note:        Optional[str] = None
