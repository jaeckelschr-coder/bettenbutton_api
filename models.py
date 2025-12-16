from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
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

    # -----------------------------
# B2B / B2C-Modelle Bettenbutton
# -----------------------------

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(50), nullable=False)          # z.B. 'touristinfo', 'destination'
    default_scope = Column(String(50), nullable=False) # z.B. 'schiltach_only', 'nachbarorte', 'whole_kinzigtal'
    is_active = Column(Boolean, default=True)

    # Beziehungen
    region_scopes = relationship("ClientRegionScope", back_populates="client", cascade="all, delete-orphan")
    property_permissions = relationship("ClientPropertyPermission", back_populates="client", cascade="all, delete-orphan")


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)  # 'schiltach', 'kinzigtal'
    type = Column(String(50), nullable=False)                # 'gemeinde', 'region', ...

    parent_region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)

    parent = relationship("Region", remote_side=[id], backref="children")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=True, unique=True)   # interne Kennung, optional

    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)

    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    postal_code = Column(String(20), nullable=False)
    city = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)

    region = relationship("Region")
    permissions = relationship("ClientPropertyPermission", back_populates="property", cascade="all, delete-orphan")

    device_id = Column(String, ForeignKey("devices.id"), nullable=True)
    device = relationship("Device", backref="properties")



class ClientRegionScope(Base):
    __tablename__ = "client_region_scopes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    scope_type = Column(String(20), nullable=False)  # 'include' oder 'exclude'

    client = relationship("Client", back_populates="region_scopes")
    region = relationship("Region")


class ClientPropertyPermission(Base):
    __tablename__ = "client_property_permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    permission_type = Column(String(20), nullable=False)  # 'allow' / 'deny'
    is_exclusive = Column(Boolean, default=False)

    client = relationship("Client", back_populates="property_permissions")
    property = relationship("Property", back_populates="permissions")

