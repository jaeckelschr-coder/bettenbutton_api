from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import os

# ============================================================
# FastAPI-App Grundkonfiguration
# ============================================================

app = FastAPI(title="Betten-Button API", version="0.1.0")

# CORS – für den Anfang offen, später auf konkrete Domains einschränken
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # z.B. ["https://bettenbutton.schiltach.de"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basis- und Static-Pfade
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Static-Files mounten (falls du später CSS/JS/Image-Dateien trennst)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ============================================================
# In-Memory Datenmodell für Geräte
# ============================================================

DEVICES = [
    {
        "id": "BB-001",
        "name": "FeWo Flößerblick",
        "phone": "+49 7836 123456",
        "email": "info@floesserblick.de",
        "status": 2,
        "lastUpdate": "2025-12-08T10:20:00Z",
        "source": "button"
    },
    {
        "id": "BB-002",
        "name": "Hotel zum Bären",
        "phone": "+49 7836 987654",
        "email": "info@hotel-baeren.de",
        "status": 0,
        "lastUpdate": "2025-12-08T09:50:00Z",
        "source": "daily_reset"
    },
    {
        "id": "BB-003",
        "name": "Berghütte Tannenblick",
        "phone": "+49 7422 555222",
        "email": "info@tannenblick.de",
        "status": 1,
        "lastUpdate": "2025-12-08T08:30:00Z",
        "source": "button"
    },
    {
        "id": "BB-004",
        "name": "Pension Waldecke",
        "phone": "+49 7836 223344",
        "email": "kontakt@waldecke.de",
        "status": 0,
        "lastUpdate": "2025-12-07T17:10:00Z",
        "source": "daily_reset"
    },
    {
        "id": "BB-005",
        "name": "Gästehaus am Markt",
        "phone": "+49 7836 445566",
        "email": "anfrage@gaestehaus-am-markt.de",
        "status": 2,
        "lastUpdate": "2025-12-08T11:05:00Z",
        "source": "button"
    }
]


class StatusUpdate(BaseModel):
    status: int                 # 0 = rot, 1 = heute, 2 = mehrere Tage
    source: Optional[str] = "button"


def get_device(device_id: str) -> Optional[dict]:
    for dev in DEVICES:
        if dev["id"] == device_id:
            return dev
    return None

# ============================================================
# Frontend-Routen: Dashboard & Simulator
# ============================================================

@app.get("/", include_in_schema=False)
def serve_dashboard():
    """
    Liefert das Dashboard (Root-URL).
    Erwartet: static/dashboard.html
    """
    dashboard_path = os.path.join(STATIC_DIR, "dashboard.html")
    if not os.path.exists(dashboard_path):
        # Fallback, falls Datei fehlt
        raise HTTPException(status_code=404, detail="dashboard.html nicht gefunden")
    return FileResponse(dashboard_path)


@app.get("/simulator", include_in_schema=False)
def serve_simulator():
    """
    Liefert den Button-Simulator.
    Erwartet: static/simulator.html
    """
    sim_path = os.path.join(STATIC_DIR, "simulator.html")
    if not os.path.exists(sim_path):
        raise HTTPException(status_code=404, detail="simulator.html nicht gefunden")
    return FileResponse(sim_path)

# ============================================================
# API-Routen für Geräte & Status
# ============================================================

@app.get("/devices")
def list_devices():
    """
    Liefert die komplette Liste der Geräte (für das Dashboard).
    """
    return DEVICES


@app.post("/devices/{device_id}/status")
def update_status(device_id: str, payload: StatusUpdate):
    """
    Aktualisiert den Status eines Gerätes (z. B. durch Button oder Simulator).
    """
    dev = get_device(device_id)
    if dev is None:
        raise HTTPException(status_code=404, detail="Device not found")

    if payload.status not in (0, 1, 2):
        raise HTTPException(status_code=400, detail="Invalid status (must be 0, 1 or 2)")

    dev["status"] = payload.status
    dev["source"] = payload.source or "button"
    dev["lastUpdate"] = datetime.now(timezone.utc).isoformat()

    return dev
