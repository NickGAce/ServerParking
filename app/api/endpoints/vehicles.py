from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.core.dependencies import require_resident
from app.db.session import get_db
from app.db.repositories.vehicles import (
    get_vehicle,
    get_vehicles,
    create_vehicle,
    update_vehicle,
    delete_vehicle,
    get_user_vehicles
)
from app.schemas.parking_spots import ParkingSpotResponse
from app.schemas.vehicles import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleParkingResponse
from app.core.security import get_current_user
from app.db.models import User, Vehicle, UserRole, ParkingSpot

vehicle_router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
    dependencies=[Depends(get_current_user)]
)


@vehicle_router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_new_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_resident)
):
    """Создание нового транспортного средства для resident"""
    db_vehicle = get_vehicle(db, license_plate=vehicle.license_plate)
    if db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle with this license plate already registered"
        )
    return create_vehicle(db=db, vehicle=vehicle, user_id=current_user.id)


@vehicle_router.get("/my", response_model=List[VehicleResponse])
def read_user_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение транспортных средств текущего пользователя"""
    return get_user_vehicles(db, user_id=current_user.id)


@vehicle_router.get("/{identifier}", response_model=VehicleResponse)
def read_vehicle(
        identifier: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Получение информации о транспортном средстве по ID или номеру"""
    # Пытаемся понять, это ID или номер
    if identifier.isdigit():
        db_vehicle = get_vehicle(db, vehicle_id=int(identifier))
    else:
        db_vehicle = get_vehicle(db, license_plate=identifier)

    if db_vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    if db_vehicle.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return db_vehicle


@vehicle_router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_existing_vehicle(
    vehicle_id: int,
    vehicle: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление информации о транспортном средстве"""
    db_vehicle = get_vehicle(db, vehicle_id=vehicle_id)
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    if db_vehicle.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return update_vehicle(db=db, vehicle_id=vehicle_id, vehicle=vehicle)


@vehicle_router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление транспортного средства"""
    db_vehicle = get_vehicle(db, vehicle_id=vehicle_id)
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    if db_vehicle.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    delete_vehicle(db=db, vehicle_id=vehicle_id)
    return {"ok": True}




