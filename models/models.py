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
