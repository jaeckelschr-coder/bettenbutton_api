import secrets
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Device

# Einfacher Admin-Key für Prototyp
ADMIN_KEY = "supersecret_admin_key_123"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True


def get_device_by_key(
    db: Session = Depends(get_db),
    x_device_key: str = Header(...)
):
    device = db.query(Device).filter(Device.device_key == x_device_key).first()
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device key")
    return device


def generate_device_key() -> str:
    # Sicherer zufälliger Schlüssel
    return secrets.token_urlsafe(32)
