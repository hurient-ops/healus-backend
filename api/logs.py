from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.schemas import BulkLogsRequest, BulkRawPacketsRequest, PumpStatusRequest
from models.models import PumpLog, RawPacketLog, User
from core.database import get_db
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/logs")
def receive_logs(payload: BulkLogsRequest, db: Session = Depends(get_db)):
    if not payload.logs:
        return {"status": "success", "message": "No logs to insert"}
    
    pump_id = payload.logs[0].pump_id
    if not pump_id or pump_id in ["EMPTY", "UNKNOWN_PID"]:
        # HTTP 400 에러를 반환하여 유입 차단
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid pump_id. Real PID is required.")

    # Find user_id by pump_id
    user = db.query(User).filter(User.pump_id == pump_id).first()
    user_id = user.id if user else None
    
    db_logs_added = 0
    db_logs_updated = 0
    for log in payload.logs:
        if user_id:
            existing_log = db.query(PumpLog).filter(
                PumpLog.user_id == user_id,
                PumpLog.month == log.month,
                PumpLog.day == log.day
            ).first()
        else:
            existing_log = db.query(PumpLog).filter(
                PumpLog.pump_id == log.pump_id,
                PumpLog.month == log.month,
                PumpLog.day == log.day
            ).first()
        
        if existing_log:
            existing_log.pump_id = log.pump_id
            existing_log.base_total = log.base_total
            existing_log.eat_total = log.eat_total
            existing_log.morning_total = log.morning_total
            existing_log.afternoon_total = log.afternoon_total
            existing_log.evening_total = log.evening_total
            existing_log.append_total = log.append_total
            db_logs_updated += 1
        else:
            current_year = datetime.now().year
            date_str = f"{current_year}-{log.month:02d}-{log.day:02d}"
            
            new_log = PumpLog(
                id=uuid.uuid4(),
                user_id=user_id,
                pump_id=log.pump_id,
                date=date_str,
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

    pump_id = payload.packets[0].pump_id
    if not pump_id or pump_id in ["EMPTY", "UNKNOWN_PID"]:
        # HTTP 400 에러를 반환하여 유입 차단
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid pump_id. Real PID is required.")

    # Find user_id by pump_id
    user = db.query(User).filter(User.pump_id == pump_id).first()
    user_id = user.id if user else None

    db_packets_added = 0
    for packet in payload.packets:
        existing_packet = db.query(RawPacketLog).filter(
            RawPacketLog.pump_id == packet.pump_id,
            RawPacketLog.payload_hex == packet.payload_hex
        ).first()
        
        if not existing_packet:
            new_packet = RawPacketLog(
                id=uuid.uuid4(),
                user_id=user_id,
                pump_id=packet.pump_id,
                direction=packet.direction,
                payload_hex=packet.payload_hex
            )
            db.add(new_packet)
            db_packets_added += 1
            
    db.commit()

    print(f"Inserted {db_packets_added} (out of {len(payload.packets)}) raw packets from device {payload.packets[0].pump_id}")
    return {"status": "success", "message": f"Successfully inserted {db_packets_added} raw packets"}

@router.post("/pump-status/{pump_id}")
def update_pump_status(pump_id: str, payload: PumpStatusRequest, db: Session = Depends(get_db)):
    if not pump_id or pump_id in ["EMPTY", "UNKNOWN_PID"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid pump_id. Real PID is required.")
    
    user = db.query(User).filter(User.pump_id == pump_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User with this pump_id not found")
        
    if payload.battery_level is not None:
        user.pump_battery_level = payload.battery_level
    if payload.insulin_remaining is not None:
        user.pump_insulin_remaining = payload.insulin_remaining
        
    db.commit()
    return {"status": "success", "message": "Pump status updated successfully"}
