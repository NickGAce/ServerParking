from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.db.models import ParkingSpot, Vehicle
from app.schemas.parking_places import ParkingPlaceResponse, SpotStatus, SpotType


class ParkingPlaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_parking_places(self) -> List[ParkingPlaceResponse]:
        """Get all parking spots with owner information"""
        spots = self.db.query(ParkingSpot) \
            .options(
            joinedload(ParkingSpot.current_vehicle).joinedload(Vehicle.user),
            joinedload(ParkingSpot.current_user)
        ) \
            .all()

        return [self._map_to_response(spot) for spot in spots]

    def get_parking_place_by_id(self, place_id: int) -> Optional[ParkingPlaceResponse]:
        """Get specific parking spot by ID"""
        spot = self.db.query(ParkingSpot) \
            .options(
            joinedload(ParkingSpot.current_vehicle).joinedload(Vehicle.user),
            joinedload(ParkingSpot.current_user)
        ) \
            .filter(ParkingSpot.id == place_id) \
            .first()

        return self._map_to_response(spot) if spot else None

    def get_available_parking_places(self) -> List[ParkingPlaceResponse]:
        """Get available parking spots"""
        spots = self.db.query(ParkingSpot) \
            .filter(ParkingSpot.status == SpotStatus.AVAILABLE) \
            .options(
            joinedload(ParkingSpot.current_vehicle).joinedload(Vehicle.user),
            joinedload(ParkingSpot.current_user)
        ) \
            .all()

        return [self._map_to_response(spot) for spot in spots]

    def _map_to_response(self, spot: ParkingSpot) -> ParkingPlaceResponse:
        # Получаем данные пользователя
        username = None
        user_id = None
        car_id = None  # Добавляем переменную для car_id

        if spot.current_user:
            username = spot.current_user.username
            user_id = spot.current_user.id
        elif spot.current_vehicle and spot.current_vehicle.user:
            username = spot.current_vehicle.user.username
            user_id = spot.current_vehicle.user.id

        # Получаем car_id если есть транспортное средство
        if spot.current_vehicle:
            car_id = spot.current_vehicle.id

        # Определяем занятость
        is_occupied = (
                spot.status == SpotStatus.OCCUPIED or
                spot.current_user_id is not None or
                spot.current_vehicle_id is not None
        )

        # Формируем fullName как строку с ID
        full_name = "Не занято"
        if is_occupied and username and user_id:
            full_name = f"{username}"

        # Определяем номер автомобиля
        car_number = "Нет авто"
        if spot.current_vehicle:
            car_number = spot.current_vehicle.license_plate
        elif is_occupied:
            car_number = "Авто не указано"

        return ParkingPlaceResponse(
            id=spot.id,
            fullName=full_name,
            user_id=user_id,
            car_id=car_id,  # Добавляем car_id в ответ
            carNumber=car_number,
            placeNumber=spot.spot_number,
            placeType=spot.type,
            placeStatus=spot.status,
            x_coordinate=spot.x_coordinate,
            y_coordinate=spot.y_coordinate
        )