from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from app.db.models import SpotType, SpotStatus


class ParkingSpotBase(BaseModel):
    """Базовая схема парковочного места"""
    spot_number: str
    type: SpotType
    status: SpotStatus = SpotStatus.AVAILABLE  # Значение по умолчанию
    x_coordinate: float
    y_coordinate: float

    @field_validator('spot_number')
    @classmethod
    def validate_spot_number(cls, v: str) -> str:
        """Валидация номера места"""
        v = v.strip()
        if not v:
            raise ValueError("Номер места не может быть пустым")
        if len(v) > 10:
            raise ValueError("Номер места должен содержать не более 10 символов")
        return v

    @field_validator('x_coordinate', 'y_coordinate')
    @classmethod
    def validate_coordinates(cls, v: float) -> float:
        """Валидация географических координат"""
        if not (-180 <= v <= 180):
            raise ValueError("Координаты должны быть в диапазоне от -180 до 180")
        return round(v, 6)  # Округление до 6 знаков


class ParkingSpotCreate(ParkingSpotBase):
    """Схема для создания парковочного места"""
    current_vehicle_id: Optional[int] = None
    reserved_until: Optional[datetime] = None

    parking_id: Optional[int] = None
    current_user_id: Optional[int] = None

    @field_validator('reserved_until')
    @classmethod
    def validate_reservation_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Проверка даты бронирования"""
        if v and v < datetime.now():
            raise ValueError("Дата бронирования не может быть в прошлом")
        return v


class ParkingSpotUpdate(BaseModel):
    """Схема для обновления парковочного места"""
    spot_number: Optional[str] = None
    type: Optional[SpotType] = None
    status: Optional[SpotStatus] = None
    current_vehicle_id: Optional[int] = None
    current_user_id: Optional[int] = None
    reserved_until: Optional[datetime] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None

    @field_validator('*')
    @classmethod
    def validate_update_fields(cls, v, info):
        """Комплексная валидация при обновлении"""
        if v is None:
            return v

        field_name = info.field_name
        if field_name == 'spot_number':
            v = v.strip()
            if not v:
                raise ValueError("Номер места не может быть пустым")
            if len(v) > 10:
                raise ValueError("Номер места должен содержать не более 10 символов")
            return v

        if field_name in ('x_coordinate', 'y_coordinate'):
            if not (-180 <= v <= 180):
                raise ValueError("Координаты должны быть в диапазоне от -180 до 180")
            return round(v, 6)

        if field_name == 'reserved_until' and v < datetime.now():
            raise ValueError("Дата бронирования не может быть в прошлом")

        return v


class ParkingSpotResponse(ParkingSpotBase):
    """Схема ответа с данными парковочного места"""
    id: int
    current_vehicle_id: Optional[int] = None
    reserved_until: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None  # Добавлено поле времени обновления
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    current_user_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "spot_number": "A12",
                "type": "owned",
                "status": "occupied",
                "x_coordinate": 37.617634,
                "y_coordinate": 55.755864,
                "current_vehicle_id": 5,
                "reserved_until": "2023-12-31T23:59:59",
                "created_at": "2023-01-15T10:00:00",
                "updated_at": "2023-01-20T15:30:00"
            }
        }
    )

class ParkingSpotReservationResponse(BaseModel):
    spot: ParkingSpotResponse
    license_plate: str