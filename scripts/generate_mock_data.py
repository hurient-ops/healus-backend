import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path to import models and core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, engine
from models import models

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

def create_mock_data():
    db = SessionLocal()
    try:
        # 1. Create a dummy user
        test_email = "testuser@healus.com"
        user = db.query(models.User).filter(models.User.email == test_email).first()
        if not user:
            user = models.User(
                email=test_email,
                hashed_password="hashed_dummy_password",
                name="김철수",
                device_mac="MAC_1234"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"[OK] Created mock user: {user.name} ({user.email})")
        else:
            print(f"[INFO] User {user.name} already exists.")

        # 2. Generate 30 days of mock PumpLog data
        print("[WAIT] Generating 30 days of mock PumpLog data...")
        
        # Clear existing logs for this device to prevent duplicates
        db.query(models.PumpLog).filter(models.PumpLog.device_mac == user.device_mac).delete()
        
        today = datetime.now()
        mock_logs = []
        
        for i in range(30, 0, -1):
            log_date = today - timedelta(days=i)
            
            # Base logic: Weekends have higher eat_total (eating out/irregular)
            is_weekend = log_date.weekday() >= 5
            
            # Random variations
            base_val = round(random.uniform(15.0, 18.0), 1)
            
            if is_weekend:
                morning_val = round(random.uniform(5.0, 8.0), 1)
                afternoon_val = round(random.uniform(8.0, 12.0), 1)
                evening_val = round(random.uniform(10.0, 15.0), 1)
                append_val = round(random.uniform(2.0, 5.0), 1)
            else:
                morning_val = round(random.uniform(4.0, 6.0), 1)
                afternoon_val = round(random.uniform(6.0, 9.0), 1)
                evening_val = round(random.uniform(5.0, 8.0), 1)
                append_val = round(random.uniform(0.0, 2.0), 1)
                
            eat_val = round(morning_val + afternoon_val + evening_val + append_val, 1)
            
            log = models.PumpLog(
                user_id=user.id,
                device_mac=user.device_mac,
                month=log_date.month,
                day=log_date.day,
                base_total=base_val,
                eat_total=eat_val,
                morning_total=morning_val,
                afternoon_total=afternoon_val,
                evening_total=evening_val,
                append_total=append_val,
                created_at=log_date
            )
            mock_logs.append(log)
            
        db.add_all(mock_logs)
        db.commit()
        print(f"[OK] Successfully inserted {len(mock_logs)} daily logs for {user.device_mac}.")
        
    except Exception as e:
        print(f"[ERROR] Error generating mock data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_mock_data()
