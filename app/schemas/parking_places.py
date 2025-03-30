from enum import Enum
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Tuple, Union


class SpotType(str, Enum):
    OWNED = "owned"
    RENT = "rent"
    GUEST = "guest"
    SPECIAL = "special"


class SpotStatus(str, Enum):
    OCCUPIED = "occupied"
    AVAILABLE = "available"
    BLOCKED = "blocked"


class ParkingPlaceBase(BaseModel):
    placeNumber: str
    placeType: SpotType
    placeStatus: SpotStatus

    @field_validator('placeNumber')
    @classmethod
    def validate_spot_number(cls, v: str) -> str:
        if len(v) > 10:
            raise ValueError("Номер места не может быть длиннее 10 символов")
        return v


class ParkingPlaceCreate(ParkingPlaceBase):
    placeStatus: SpotStatus = SpotStatus.AVAILABLE


class ParkingPlaceUpdate(BaseModel):
    placeNumber: Optional[str] = None
    placeType: Optional[SpotType] = None
    placeStatus: Optional[SpotStatus] = None

    @field_validator('placeNumber')
    @classmethod
    def validate_update_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 10:
            raise ValueError("Номер места не может быть длиннее 10 символов")
        return v


class ParkingPlaceResponse(BaseModel):
    id: int
    fullName: str
    user_id: Optional[int] = None
    car_id: Optional[int] = None  # Добавляем новое поле
    carNumber: str
    placeNumber: str
    placeType: SpotType
    placeStatus: SpotStatus
    x_coordinate: Optional[float] = None  # Добавлено для полноты, так как используется в ответе
    y_coordinate: Optional[float] = None  # Добавлено для полноты, так как используется в ответе

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "fullName": "Иванов Иван",
                "user_id": 123,
                "car_id": 456,  # Добавляем пример car_id
                "carNumber": "А123БВ77",
                "placeNumber": "A12",
                "placeType": "owned",
                "placeStatus": "occupied",
                "x_coordinate": 12.345,
                "y_coordinate": 67.890
            }
        }
    )