from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True)  # z.B. "BB-001"
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    location = Column(String, nullable=True)

    current_status = Column(Integer, default=0)  # 0,1,2
    last_update = Column(DateTime, nullable=True)

    device_key = Column(String, nullable=False, unique=True)  # API-Key fürs Gerät

    # Historie
    status_events = relationship("StatusEvent", back_populates="device")


class StatusEvent(Base):
    __tablename__ = "status_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    status = Column(Integer, nullable=False)  # 0,1,2
    source = Column(String, nullable=True)   # "button", "daily_reset", "boot", "wake", "admin"
    timestamp = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="status_events")
