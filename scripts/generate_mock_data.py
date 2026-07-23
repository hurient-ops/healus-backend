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

        # 2. Generate 100 days of mock PumpLog data
        print("[WAIT] Generating 100 days of mock PumpLog data...")
        
        # Clear existing logs for this device to prevent duplicates
        db.query(models.PumpLog).filter(models.PumpLog.device_mac == user.device_mac).delete()
        
        today = datetime.now()
        mock_logs = []
        
        for i in range(100, 0, -1):
            log_date = today - timedelta(days=i)
            
            # Base values
            base_val = round(random.uniform(15.0, 18.0), 1)
            morning_val = round(random.uniform(4.0, 6.0), 1)
            afternoon_val = round(random.uniform(6.0, 9.0), 1)
            evening_val = round(random.uniform(5.0, 8.0), 1)
            append_val = round(random.uniform(0.0, 2.0), 1)
            
            avg_cgm = round(random.uniform(90.0, 120.0), 1)
            sleep_hours = round(random.uniform(6.5, 8.5), 1)
            stress_level = random.randint(1, 4)
            exercise_hours = round(random.uniform(0.0, 0.5), 1)
            event_tags = []
            
            # Random Events (Regardless of weekday/weekend)
            # 1. Dining Out (회식/과식) - 20% chance
            if random.random() < 0.2:
                evening_val += round(random.uniform(5.0, 10.0), 1)
                append_val += round(random.uniform(2.0, 5.0), 1)
                avg_cgm += round(random.uniform(30.0, 60.0), 1)
                event_tags.append("회식")
                
            # 2. Overtime/Stress (야근/스트레스) - 15% chance
            if random.random() < 0.15:
                sleep_hours -= round(random.uniform(2.0, 4.0), 1)
                stress_level += random.randint(3, 6)
                avg_cgm += round(random.uniform(10.0, 25.0), 1) # Stress increases bg
                event_tags.append("야근")
                
            # 3. Exercise (운동) - 30% chance
            if random.random() < 0.3:
                exercise_hours += round(random.uniform(0.5, 2.0), 1)
                avg_cgm -= round(random.uniform(10.0, 20.0), 1)
                event_tags.append("운동")
                
            eat_val = round(morning_val + afternoon_val + evening_val + append_val, 1)
            
            # Ensure CGM doesn't drop below 70 or exceed 300
            avg_cgm = max(70.0, min(300.0, avg_cgm))
            stress_level = max(1, min(10, stress_level))
            
            # Random Pump Errors (10% chance)
            error_count = 0
            error_types = []
            if random.random() < 0.1:
                error_count = random.randint(1, 3)
                possible_errors = ["막힘", "배터리부족", "통신오류", "누수"]
                error_types = random.sample(possible_errors, k=min(error_count, len(possible_errors)))
            
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
                avg_cgm=avg_cgm,
                sleep_hours=sleep_hours,
                stress_level=stress_level,
                exercise_hours=exercise_hours,
                event_tags=",".join(event_tags) if event_tags else None,
                error_count=error_count,
                error_types=",".join(error_types) if error_types else None,
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
