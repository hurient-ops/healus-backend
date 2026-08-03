from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.schemas import BulkLogsRequest, BulkRawPacketsRequest
from models.models import PumpLog, RawPacketLog, User
from core.database import get_db
import uuid

router = APIRouter()

@router.post("/logs")
def receive_logs(payload: BulkLogsRequest, db: Session = Depends(get_db)):
    if not payload.logs:
        return {"status": "success", "message": "No logs to insert"}
    
    # Find user_id by pump_id
    pump_id = payload.logs[0].pump_id
    user = db.query(User).filter(User.pump_id == pump_id).first()
    user_id = user.id if user else None
    
    db_logs = [
        PumpLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            pump_id=log.pump_id,
            month=log.month,
            day=log.day,
            base_total=log.base_total,
            eat_total=log.eat_total,
            morning_total=log.morning_total,
            afternoon_total=log.afternoon_total,
            evening_total=log.evening_total,
            append_total=log.append_total
        )
        for log in payload.logs
    ]
    db.add_all(db_logs)
    db.commit()

    print(f"Inserted {len(payload.logs)} logs from device {payload.logs[0].pump_id}")
    return {"status": "success", "message": f"Successfully inserted {len(payload.logs)} logs"}

@router.post("/raw_logs")
def receive_raw_logs(payload: BulkRawPacketsRequest, db: Session = Depends(get_db)):
    if not payload.packets:
        return {"status": "success", "message": "No packets to insert"}

    # Find user_id by pump_id
    pump_id = payload.packets[0].pump_id
    user = db.query(User).filter(User.pump_id == pump_id).first()
    user_id = user.id if user else None

    db_packets = [
        RawPacketLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            pump_id=packet.pump_id,
            direction=packet.direction,
            payload_hex=packet.payload_hex,
            timestamp=packet.timestamp
        )
        for packet in payload.packets
    ]
    db.add_all(db_packets)
    db.commit()

    print(f"Inserted {len(payload.packets)} raw packets from device {payload.packets[0].pump_id}")
    return {"status": "success", "message": f"Successfully inserted {len(payload.packets)} raw packets"}
