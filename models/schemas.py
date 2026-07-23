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
