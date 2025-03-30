from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from app.db.models import ParkingSpot, SpotStatus, Vehicle
from app.schemas.parking_spots import ParkingSpotCreate, ParkingSpotUpdate


def get_parking_spot(db: Session, spot_id: int = None, spot_number: str = None):
    query = db.query(ParkingSpot)
    if spot_id:
        return query.filter(ParkingSpot.id == spot_id).first()
    if spot_number:
        return query.filter(ParkingSpot.spot_number == spot_number).first()
    return None


def get_parking_spots(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ParkingSpot).offset(skip).limit(limit).all()


def get_available_spots(db: Session, spot_type: str = None):
    query = db.query(ParkingSpot).filter(ParkingSpot.status == SpotStatus.AVAILABLE)
    if spot_type:
        query = query.filter(ParkingSpot.type == spot_type)
    return query.all()


def create_parking_spot(db: Session, spot: ParkingSpotCreate):
    db_spot = ParkingSpot(**spot.dict())
    db.add(db_spot)
    db.commit()
    db.refresh(db_spot)
    return db_spot


def update_parking_spot(db: Session, spot_id: int, spot: ParkingSpotUpdate):
    db_spot = get_parking_spot(db, spot_id=spot_id)
    if not db_spot:
        return None
    update_data = spot.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_spot, field, update_data[field])
    db.commit()
    db.refresh(db_spot)
    return db_spot


def delete_parking_spot(db: Session, spot_id: int):
    db_spot = get_parking_spot(db, spot_id=spot_id)
    if not db_spot:
        return False
    db.delete(db_spot)
    db.commit()
    return True


def reserve_spot(db: Session, spot_id: int, license_plate: str, until: datetime, user_id: int):
    """Бронирование парковочного места по номеру автомобиля"""
    # vehicle = db.query(Vehicle).filter(
    #     Vehicle.license_plate == license_plate,
    #     Vehicle.user_id == user_id
    # ).first()
    #
    # if not vehicle:
    #     return None

    spot = get_parking_spot(db, spot_id=spot_id)
    if not spot:
        return None

    if spot.status != SpotStatus.AVAILABLE:
        return None

    # spot.current_vehicle_id = vehicle.id
    spot.current_user_id = user_id
    spot.reserved_until = until
    spot.status = SpotStatus.OCCUPIED
    db.commit()
    db.refresh(spot)

    return spot, license_plate


def partial_update_parking_spot(
        db: Session,
        spot_id: int,
        spot_update: ParkingSpotUpdate
) -> Optional[ParkingSpot]:
    db_spot = get_parking_spot(db, spot_id=spot_id)
    if not db_spot:
        return None

    update_data = spot_update.model_dump(exclude_unset=True)

    # Проверка уникальности spot_number
    if 'spot_number' in update_data:
        existing_spot = db.query(ParkingSpot) \
            .filter(ParkingSpot.spot_number == update_data['spot_number']) \
            .filter(ParkingSpot.id != spot_id) \
            .first()
        if existing_spot:
            raise ValueError("Spot number already exists")

    # Обновляем только переданные поля
    for field, value in update_data.items():
        setattr(db_spot, field, value)

    db.commit()
    db.refresh(db_spot)
    return db_spot