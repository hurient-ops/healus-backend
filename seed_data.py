import os
import sys
from datetime import datetime, timedelta, timezone
import random

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal, engine
from models import models

# Create all tables
models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 1. Ensure test user exists
    user = db.query(models.User).filter(models.User.email == "testuser@healus.com").first()
    if not user:
        user = models.User(
            email="testuser@healus.com",
            hashed_password="fake_hashed_password",
            name="김당뇨",
            device_mac="AA:BB:CC:DD:EE:FF"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    print(f"Seeding data for user: {user.name} (ID: {user.id})")
    
    # Clear existing logs for fresh start
    db.query(models.PumpLog).filter(models.PumpLog.user_id == user.id).delete()
    db.query(models.BloodGlucoseLog).filter(models.BloodGlucoseLog.user_id == user.id).delete()
    
    # 2. Seed Pump Logs (last 100 days)
    now = datetime.now(timezone.utc)
    
    error_pool = ["막힘", "배터리 부족", "센서 오류", "통신 지연", "주입 일시정지"]
    
    for i in range(100):
        dt = now - timedelta(days=99 - i)
        
        is_weekend = dt.weekday() >= 5
        
        # Base logic
        base_total = round(random.uniform(12.0, 15.0), 1)
        eat_total = round(random.uniform(15.0, 22.0), 1)
        
        # Simulate Dining Out (Bolus Spike) mostly on weekends (40% chance on weekends, 5% on weekdays)
        is_dining_out = (is_weekend and random.random() < 0.4) or (not is_weekend and random.random() < 0.05)
        if is_dining_out:
            eat_total += round(random.uniform(10.0, 18.0), 1) # Spike!
            
        # Simulate Exercise (Basal Drop) (20% chance overall)
        is_exercise = random.random() < 0.2
        if is_exercise:
            base_total -= round(random.uniform(3.0, 6.0), 1) # Drop!
            
        append_total = round(random.uniform(0.0, 3.0), 1)
        
        # Random errors (10% chance per day)
        has_error = random.random() < 0.1
        error_count = random.randint(1, 2) if has_error else 0
        error_types = ",".join(random.sample(error_pool, k=error_count)) if has_error else None

        pump_log = models.PumpLog(
            user_id=user.id,
            device_mac=user.device_mac,
            month=dt.month,
            day=dt.day,
            base_total=base_total,
            eat_total=eat_total,
            morning_total=round(eat_total * 0.3, 1),
            afternoon_total=round(eat_total * 0.4, 1),
            evening_total=round(eat_total * 0.3, 1),
            append_total=append_total,
            error_count=error_count,
            error_types=error_types,
            created_at=dt
        )
        db.add(pump_log)
    
    # 3. Seed Blood Glucose Logs (last 100 days, 4 times a day)
    tags = ["기상직후", "식전", "식후", "취침전"]
    for i in range(100):
        base_dt = now - timedelta(days=99 - i)
        for j, tag in enumerate(tags):
            log_dt = base_dt.replace(hour=8 + (j * 4), minute=random.randint(0, 59))
            
            # Normal range 80~140, occasional spike
            val = random.randint(80, 130)
            if tag == "식후":
                val = random.randint(120, 160)
                
            bg_log = models.BloodGlucoseLog(
                user_id=user.id,
                glucose_value=val,
                tag=tag,
                recorded_at=log_dt,
                created_at=log_dt
            )
            db.add(bg_log)

    db.commit()
    print("Seeding completed successfully! 100 PumpLogs and 400 BG Logs created.")
    db.close()

if __name__ == "__main__":
    seed_data()
