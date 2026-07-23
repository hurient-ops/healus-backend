from pydantic import BaseModel
from typing import List, Optional

class PumpLogPayload(BaseModel):
    device_mac: str
    month: int
    day: int
    base_total: float
    eat_total: float
    morning_total: float
    afternoon_total: float
    evening_total: float
    append_total: float
    
    # New Lifelog Fields
    avg_cgm: Optional[float] = 110.0
    sleep_hours: Optional[float] = 7.5
    stress_level: Optional[int] = 3
    exercise_hours: Optional[float] = 0.5
    event_tags: Optional[str] = None
    
    error_count: Optional[int] = 0
    error_types: Optional[str] = None
    created_at: str

class BulkLogsRequest(BaseModel):
    logs: List[PumpLogPayload]

class RawPacketPayload(BaseModel):
    device_mac: str
    direction: str  # 'TX' or 'RX'
    payload_hex: str
    timestamp: str

class BulkRawPacketsRequest(BaseModel):
    packets: List[RawPacketPayload]

class BloodGlucoseLogRequest(BaseModel):
    user_email: str
    glucose_value: int
    tag: str
    recorded_at: str
