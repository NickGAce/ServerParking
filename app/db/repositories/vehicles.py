from sqlalchemy.orm import Session, joinedload, contains_eager
from app.db.models import Vehicle, ParkingSpot
from app.schemas.vehicles import VehicleCreate, VehicleUpdate


def get_vehicle(db: Session, vehicle_id: int = None, license_plate: str = None):
    query = db.query(Vehicle)
    if vehicle_id:
        return query.filter(Vehicle.id == vehicle_id).first()
    if license_plate:
        return query.filter(Vehicle.license_plate == license_plate).first()
    return None


def get_vehicles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Vehicle).offset(skip).limit(limit).all()


def get_user_vehicles(db: Session, user_id: int):
    return db.query(Vehicle).filter(Vehicle.user_id == user_id).all()


def create_vehicle(db: Session, vehicle: VehicleCreate, user_id: int):
    db_vehicle = Vehicle(**vehicle.dict(exclude={"user_id"}), user_id=user_id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def update_vehicle(db: Session, vehicle_id: int, vehicle: VehicleUpdate):
    db_vehicle = get_vehicle(db, vehicle_id=vehicle_id)
    if not db_vehicle:
        return None
    update_data = vehicle.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_vehicle, field, update_data[field])
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: int):
    db_vehicle = get_vehicle(db, vehicle_id=vehicle_id)
    if not db_vehicle:
        return False
    db.delete(db_vehicle)
    db.commit()
    return True


