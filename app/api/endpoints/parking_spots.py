from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.dependencies import admin_required
from app.db.session import get_db
from app.db.repositories.parking_spots import (
    get_parking_spot,
    get_parking_spots,
    create_parking_spot,
    update_parking_spot,
    delete_parking_spot,
    get_available_spots,
    reserve_spot, partial_update_parking_spot
)
from app.schemas.parking_spots import (
    ParkingSpotCreate,
    ParkingSpotUpdate,
    ParkingSpotResponse, ParkingSpotReservationResponse
)
from app.core.security import get_current_user
from app.db.models import User, ParkingSpot, SpotStatus, Vehicle

parking_spot_router = APIRouter(
    prefix="/parking-spots",
    tags=["parking-spots"]
)


# Public endpoints
@parking_spot_router.get("/available", response_model=List[ParkingSpotResponse])
def list_available_spots(
    db: Session = Depends(get_db),
    spot_type: Optional[str] = None
):
    """Получение списка доступных парковочных мест (публичный)"""
    return get_available_spots(db, spot_type)


# Protected endpoints (require auth)
protected_router = APIRouter(dependencies=[Depends(get_current_user)])


@protected_router.post("/", response_model=ParkingSpotResponse, status_code=status.HTTP_201_CREATED)
def create_new_spot(
    spot: ParkingSpotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Создание нового парковочного места (только для админа)"""
    db_spot = get_parking_spot(db, spot_number=spot.spot_number)
    if db_spot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spot with this number already exists"
        )
    return create_parking_spot(db=db, spot=spot)


@protected_router.delete("/{spot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spot(
    spot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """Удаление парковочного места (только для админа)"""
    db_spot = get_parking_spot(db, spot_id=spot_id)
    if not db_spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )
    delete_parking_spot(db=db, spot_id=spot_id)
    return {"ok": True}


@protected_router.post("/{spot_id}/reserve", response_model=ParkingSpotReservationResponse)
def reserve_parking_spot(
    spot_id: int,
    license_plate: str = Body(...),
    until: datetime = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Бронирование парковочного места по номеру автомобиля"""
    # Находим транспортное средство
    # vehicle = db.query(Vehicle).filter(
    #     Vehicle.license_plate == license_plate,
    #     Vehicle.user_id == current_user.id
    # ).first()
    #
    # if not vehicle:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Vehicle not found or doesn't belong to you"
    #     )

    # Проверяем место
    spot = get_parking_spot(db, spot_id=spot_id)
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking spot not found"
        )

    if spot.status != SpotStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parking spot is not available"
        )

    # Бронируем место
    # spot.current_vehicle_id = vehicle.id
    spot.current_user_id = current_user.id
    spot.reserved_until = until
    spot.status = SpotStatus.OCCUPIED
    db.commit()
    db.refresh(spot)

    return {
        "spot": spot,
        "license_plate": license_plate
    }

@protected_router.patch("/{spot_id}", response_model=ParkingSpotResponse)
def partial_update_spot(
    spot_id: int,
    spot_update: ParkingSpotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Частичное обновление парковочного места (PATCH)
    - Только для администраторов
    """
    try:
        db_spot = partial_update_parking_spot(db, spot_id=spot_id, spot_update=spot_update)
        if not db_spot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parking spot not found"
            )
        return db_spot
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating parking spot: {str(e)}"
        )


@protected_router.get("/my-spots", response_model=List[ParkingSpotResponse])
def get_user_parking_spots(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Получение всех парковочных мест текущего пользователя
    (основано на его транспортных средствах)
    """
    # Получаем все транспортные средства пользователя
    user_vehicles = current_user.vehicles

    # Собираем ID всех транспортных средств пользователя
    vehicle_ids = [vehicle.id for vehicle in user_vehicles]

    # Находим все парковочные места, связанные с этими транспортными средствами
    spots = db.query(ParkingSpot).filter(
        ParkingSpot.current_vehicle_id.in_(vehicle_ids)
    ).all()

    return spots
# Подключение роутеров
parking_spot_router.include_router(protected_router)