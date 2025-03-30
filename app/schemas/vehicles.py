from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional

from app.schemas.parking_spots import ParkingSpotResponse


class VehicleBase(BaseModel):
    license_plate: str
    is_special: bool = False


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = None
    is_special: Optional[bool] = None

    @field_validator('license_plate')
    @classmethod
    def validate_license_plate(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 20:
            raise ValueError("License plate must be 20 characters or less")
        return v


class VehicleResponse(VehicleBase):
    id: int
    created_at: datetime
    user: Optional['UserResponse'] = None  # Для связанных данных пользователя

    model_config = ConfigDict(from_attributes=True)  # Replaces orm_mode=True


class VehicleResponse(BaseModel):
    id: int
    license_plate: str
    is_special: bool
    created_at: datetime

class VehicleParkingResponse(VehicleResponse):
    parking_spot: Optional[ParkingSpotResponse] = None  # Связанное парковочное место


# Для избежания circular imports
from app.schemas.user import UserResponse
VehicleResponse.model_rebuild()