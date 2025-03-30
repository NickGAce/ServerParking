from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAlchemyEnum, ForeignKey, func, Float
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime


class UserRole(str, Enum):
    RESIDENT = "resident"
    ADMIN = "admin"
    MANAGER = "company"
    TENANT = "tenant"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    role = Column(SQLAlchemyEnum(UserRole, name="user_role_enum"), default=UserRole.RESIDENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicles = relationship("Vehicle", back_populates="user", cascade="all, delete")
    granted_permissions = relationship("AccessPermission", back_populates="grantor")
    parking_spots = relationship("ParkingSpot", back_populates="current_user")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False)
    is_special = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="vehicles")
    parking_spot = relationship("ParkingSpot", back_populates="current_vehicle")
    access_permissions = relationship("AccessPermission", back_populates="vehicle", cascade="all, delete-orphan")


class SpotType(str, Enum):
    OWNED = "owned"
    RENT = "rent"
    GUEST = "guest"
    SPECIAL = "special"


class SpotStatus(str, Enum):
    OCCUPIED = "occupied"
    AVAILABLE = "available"
    BLOCKED = "blocked"

#нету
class ParkingConfig(Base):
    __tablename__ = "parking_config"

    id = Column(Integer, primary_key=True)
    total_max_spots = Column(Integer, nullable=False)
    owned = Column(Integer, nullable=False)
    guest = Column(Integer, nullable=False)
    special = Column(Integer, nullable=False)
    rent = Column(Integer, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    spot_number = Column(String(10), unique=True, nullable=False)
    type = Column(SQLAlchemyEnum(SpotType), nullable=False)
    status = Column(SQLAlchemyEnum(SpotStatus), nullable=False)
    parking_id = Column(Integer, ForeignKey("parking_config.id"))
    current_vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="SET NULL"))
    current_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    reserved_until = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    x_coordinate = Column(Float, nullable=False)  # Новая колонка
    y_coordinate = Column(Float, nullable=False)  # Новая колонка

    current_vehicle = relationship("Vehicle", back_populates="parking_spot")
    parking_config = relationship("ParkingConfig")
    current_user = relationship("User", back_populates="parking_spots")

class PermissionType(str, Enum):
    PERMANENT = "permanent"#зачем?
    TEMPORARY = "temporary"

#нету
class AccessPermission(Base):
    __tablename__ = "access_permissions"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    parking_spot_id = Column(Integer, ForeignKey("parking_spots.id", ondelete="SET NULL"))
    permission_type = Column(SQLAlchemyEnum(PermissionType), nullable=False)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True))
    is_accepted = Column(Boolean)
    granted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    vehicle = relationship("Vehicle", back_populates="access_permissions")
    parking_spot = relationship("ParkingSpot")
    grantor = relationship("User", back_populates="granted_permissions")