from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


# ----------- Status/Historie -----------

class StatusEventBase(BaseModel):
    status: int = Field(..., ge=0, le=2)
    source: Optional[str] = "button"


class StatusEventCreate(StatusEventBase):
    pass


class StatusEventRead(StatusEventBase):
    timestamp: datetime

    class Config:
        orm_mode = True


# ----------- Device -----------

class DeviceBase(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceRead(DeviceBase):
    current_status: int
    last_update: Optional[datetime] = None

    class Config:
        orm_mode = True


class DeviceDetail(DeviceRead):
    # mit letztem Event (optional)
    last_event: Optional[StatusEventRead] = None


class DeviceListResponse(BaseModel):
    devices: List[DeviceRead]
