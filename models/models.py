from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    device_mac = Column(String, unique=True, index=True, nullable=True)  # Mapped to a single pump for now
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pump_logs = relationship("PumpLog", back_populates="owner")
    raw_packets = relationship("RawPacketLog", back_populates="owner")
    bg_logs = relationship("BloodGlucoseLog", back_populates="owner")

class PumpLog(Base):
    __tablename__ = "pump_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Linked to User
    device_mac = Column(String, index=True, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    base_total = Column(Float, nullable=False)
    eat_total = Column(Float, nullable=False)
    morning_total = Column(Float, nullable=False)
    afternoon_total = Column(Float, nullable=False)
    evening_total = Column(Float, nullable=False)
    append_total = Column(Float, nullable=False)
    
    # New Lifelog Fields
    avg_cgm = Column(Float, nullable=True, default=110.0)
    sleep_hours = Column(Float, nullable=True, default=7.5)
    stress_level = Column(Integer, nullable=True, default=3)
    exercise_hours = Column(Float, nullable=True, default=0.5)
    event_tags = Column(String, nullable=True) # "회식", "운동", "야근" 등
    
    error_count = Column(Integer, nullable=False, default=0)
    error_types = Column(String, nullable=True) # Comma-separated string like "막힘,배터리부족"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="pump_logs")

class RawPacketLog(Base):
    __tablename__ = "raw_packet_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Linked to User
    device_mac = Column(String, index=True, nullable=False)
    direction = Column(String, nullable=False)  # 'TX' or 'RX'
    payload_hex = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="raw_packets")

class BloodGlucoseLog(Base):
    __tablename__ = "blood_glucose_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    glucose_value = Column(Integer, nullable=False)
    tag = Column(String, nullable=False) # e.g., '식전', '식후', '공복', '취침전'
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="bg_logs")
