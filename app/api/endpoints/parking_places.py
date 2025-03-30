from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.repositories.parking_places import ParkingPlaceRepository
from app.db.session import get_db
from app.schemas.parking_places import ParkingPlaceResponse
from app.core.security import get_current_user
from app.db.models import User

router = APIRouter(
    prefix="/api/parking_places",
    tags=["parking_places"]
)


@router.get("/", response_model=List[ParkingPlaceResponse])
async def get_all_parking_places(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка всех парковочных мест"""
    repo = ParkingPlaceRepository(db)
    try:
        return repo.get_all_parking_places()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении данных: {str(e)}"
        )

@router.get("/available", response_model=List[ParkingPlaceResponse])
async def get_available_parking_places(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение доступных мест"""
    repo = ParkingPlaceRepository(db)
    try:
        return repo.get_available_parking_places()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении данных: {str(e)}"
        )

@router.get("/{place_id}", response_model=ParkingPlaceResponse)
async def get_parking_place_details(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение информации о конкретном месте"""
    repo = ParkingPlaceRepository(db)
    spot = repo.get_parking_place_by_id(place_id)
    if not spot:
        raise HTTPException(
            status_code=404,
            detail="Парковочное место не найдено"
        )
    return spot


