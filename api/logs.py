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
    
    db_logs_added = 0
    db_logs_updated = 0
    for log in payload.logs:
        existing_log = db.query(PumpLog).filter(
            PumpLog.pump_id == log.pump_id,
            PumpLog.month == log.month,
            PumpLog.day == log.day
        ).first()
        
        if existing_log:
            existing_log.base_total = log.base_total
            existing_log.eat_total = log.eat_total
            existing_log.morning_total = log.morning_total
            existing_log.afternoon_total = log.afternoon_total
            existing_log.evening_total = log.evening_total
            existing_log.append_total = log.append_total
            db_logs_updated += 1
        else:
            new_log = PumpLog(
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
            db.add(new_log)
            db_logs_added += 1
            
    db.commit()

    print(f"Processed {len(payload.logs)} logs (Inserted: {db_logs_added}, Updated: {db_logs_updated}) from device {payload.logs[0].pump_id}")
    return {"status": "success", "message": f"Successfully processed {len(payload.logs)} logs"}

@router.post("/raw_logs")
def receive_raw_logs(payload: BulkRawPacketsRequest, db: Session = Depends(get_db)):
    if not payload.packets:
        return {"status": "success", "message": "No packets to insert"}

    # Find user_id by pump_id
    pump_id = payload.packets[0].pump_id
    user = db.query(User).filter(User.pump_id == pump_id).first()
    user_id = user.id if user else None

    db_packets_added = 0
    for packet in payload.packets:
        existing_packet = db.query(RawPacketLog).filter(
            RawPacketLog.pump_id == packet.pump_id,
            RawPacketLog.timestamp == packet.timestamp,
            RawPacketLog.payload_hex == packet.payload_hex
        ).first()
        
        if not existing_packet:
            new_packet = RawPacketLog(
                id=str(uuid.uuid4()),
                user_id=user_id,
                pump_id=packet.pump_id,
                direction=packet.direction,
                payload_hex=packet.payload_hex,
                timestamp=packet.timestamp
            )
            db.add(new_packet)
            db_packets_added += 1
            
    db.commit()

    print(f"Inserted {db_packets_added} (out of {len(payload.packets)}) raw packets from device {payload.packets[0].pump_id}")
    return {"status": "success", "message": f"Successfully inserted {db_packets_added} raw packets"}
