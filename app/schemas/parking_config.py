from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional


class ParkingConfigBase(BaseModel):
    total_max_spots: int
    owned: int
    guest: int
    special: int
    rent: int

    @field_validator('*')
    @classmethod
    def validate_positive_numbers(cls, v: int) -> int:
        """Проверка, что все значения положительные"""
        if v < 0:
            raise ValueError("All values must be positive numbers")
        return v

    @field_validator('total_max_spots')
    @classmethod
    def validate_total(cls, v: int, values) -> int:
        """Проверка, что общее количество не меньше суммы по типам"""
        if all(field in values.data for field in ['owned', 'guest', 'special', 'rent']):
            sum_spots = values.data['owned'] + values.data['guest'] + values.data['special'] + values.data['rent']
            if v < sum_spots:
                raise ValueError("Total max spots cannot be less than sum of all spot types")
        return v


class ParkingConfigCreate(ParkingConfigBase):
    pass


class ParkingConfigUpdate(BaseModel):
    total_max_spots: Optional[int] = None
    owned: Optional[int] = None
    guest: Optional[int] = None
    special: Optional[int] = None
    rent: Optional[int] = None

    @field_validator('*')
    @classmethod
    def validate_positive_if_present(cls, v: Optional[int]) -> Optional[int]:
        """Проверка для частичного обновления"""
        if v is not None and v < 0:
            raise ValueError("All values must be positive numbers")
        return v


class ParkingConfigResponse(ParkingConfigBase):
    id: int
    updated_at: datetime
    current_usage: Optional[int] = None  # Добавляем вычисляемое поле для текущей загрузки

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "total_max_spots": 100,
                "owned": 40,
                "guest": 30,
                "special": 10,
                "rent": 20,
                "updated_at": "2023-05-20T12:00:00Z",
                "current_usage": 85
            }
        }
    )