APP_NAME = "Betten-Button API"
APP_VERSION = "0.9.0-2025-12-17"

# ================================================================
# Bettenbutton – main.py (Swagger/Schemas wieder sauber)
# + Dashboard Route /dashboard
# ================================================================

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import Optional, List
from datetime import datetime
import os

from database import Base, engine, SessionLocal
import models
import schemas

print(f"### {APP_NAME} LOADED – VERSION {APP_VERSION} ###")

# ================================================================
# INITIAL SETUP
# ================================================================

Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Static Files (Dashboard etc.)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ================================================================
# FRONTEND ROOT + DASHBOARD
# ================================================================

@app.get("/", include_in_schema=False, response_class=HTMLResponse)
def root():
    return HTMLResponse("<h1>Bettenbutton Backend läuft</h1>")

@app.get("/dashboard", include_in_schema=False)
def dashboard():
    # statisches Dashboard (Polling via GET /devices)
    return FileResponse(os.path.join(STATIC_DIR, "dashboard.html"))


# ================================================================
# DB SESSION
# ================================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================================================================
# SECURITY (PROTOTYP)
# ================================================================

ADMIN_KEY = "supersecret_admin_key_123"

def require_admin_key(x_admin_key: Optional[str]):
    if not x_admin_key or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")

def require_device_key(db, device_id: str, x_device_key: Optional[str]):
    if not x_device_key:
        raise HTTPException(status_code=401, detail="Missing X-Device-Key")
    dev = db.query(models.Device).get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    if dev.device_key != x_device_key:
        raise HTTPException(status_code=403, detail="Invalid device key")
    return dev


# ================================================================
# HELPER
# ================================================================

def next_status(current: int) -> int:
    # verbindliche Betten-Button-Logik:
    # 0 (rot) -> 1 (heute) -> 2 (mehrere Tage) -> 0
    return (int(current) + 1) % 3

def to_dashboard_device(d: models.Device) -> schemas.DeviceDashboardRead:
    # Dashboard-kompatibles Objekt inkl. Dopplung der Felder
    return schemas.DeviceDashboardRead(
        id=d.id,
        name=d.name,
        phone=d.phone,
        email=d.email,
        location=d.location,
        current_status=d.current_status,
        last_update=d.last_update,
        status=d.current_status,
        lastUpdate=d.last_update
    )


# ================================================================
# DEVICES
# ================================================================

@app.post("/devices", response_model=schemas.DeviceRead)
def create_device(payload: schemas.DeviceCreate, db=Depends(get_db)):
    # id ist String (z.B. "BB-001") – bleibt so wie im Modell
    existing = db.query(models.Device).get(payload.id)
    if existing:
        raise HTTPException(status_code=409, detail="Device ID already exists")

    dev = models.Device(
        id=payload.id,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        location=payload.location,
        device_key=payload.device_key,
        current_status=0,
        last_update=None,
    )
    db.add(dev)
    db.commit()
    db.refresh(dev)
    return dev

@app.get("/devices", response_model=List[schemas.DeviceDashboardRead])
def list_devices(db=Depends(get_db)):
    devices = db.query(models.Device).all()
    return [to_dashboard_device(d) for d in devices]

@app.get("/api/version")
def get_version():
    return {"name": APP_NAME, "version": APP_VERSION, "status": "ok"}


# ================================================================
# BUTTON PRESS (SYSTEMKERN)
# ================================================================

@app.post("/devices/{device_id}/press", response_model=schemas.PressResponse)
def press_device(
    device_id: str,
    x_device_key: Optional[str] = Header(default=None),
    db=Depends(get_db),
):
    dev = require_device_key(db, device_id, x_device_key)

    new_status = next_status(dev.current_status)
    now = datetime.utcnow()

    event = models.StatusEvent(
        device_id=device_id,
        status=new_status,
        source="button",
        timestamp=now,
    )
    db.add(event)

    dev.current_status = new_status
    dev.last_update = now

    db.commit()
    db.refresh(event)

    return schemas.PressResponse(
        device_id=device_id,
        status=new_status,
        lastUpdate=now,
        timestamp=event.timestamp,
        source=event.source or "button",
    )


# ================================================================
# STATUS OVERRIDE (ADMIN / SIMULATOR)
# ================================================================

@app.post("/devices/{device_id}/status", response_model=schemas.StatusEventRead)
def set_device_status(
    device_id: str,
    payload: schemas.StatusEventCreate,
    x_admin_key: Optional[str] = Header(default=None),
    db=Depends(get_db),
):
    require_admin_key(x_admin_key)

    dev = db.query(models.Device).get(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")

    now = datetime.utcnow()

    event = models.StatusEvent(
        device_id=device_id,
        status=payload.status,
        source=payload.source or "admin",
        timestamp=now,
    )
    db.add(event)

    dev.current_status = payload.status
    dev.last_update = now

    db.commit()
    db.refresh(event)

    return event
