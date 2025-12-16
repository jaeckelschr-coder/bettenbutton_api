from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


# =========================
# Status / Historie
# =========================

class StatusEventCreate(BaseModel):
    status: int = Field(..., ge=0, le=2)
    source: Optional[str] = "button"


class StatusEventRead(BaseModel):
    id: int
    device_id: str
    status: int = Field(..., ge=0, le=2)
    source: Optional[str] = "button"
    timestamp: datetime

    class Config:
        orm_mode = True


class PressResponse(BaseModel):
    device_id: str
    status: int = Field(..., ge=0, le=2)
    lastUpdate: datetime
    timestamp: datetime
    source: str


# =========================
# Device
# =========================

class DeviceBase(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None


class DeviceCreate(DeviceBase):
    device_key: str


class DeviceRead(DeviceBase):
    current_status: int = Field(..., ge=0, le=2)
    last_update: Optional[datetime] = None

    class Config:
        orm_mode = True


class DeviceDashboardRead(DeviceBase):
    current_status: int = Field(..., ge=0, le=2)
    last_update: Optional[datetime] = None
    status: int = Field(..., ge=0, le=2)
    lastUpdate: Optional[datetime] = None

    class Config:
        orm_mode = True
