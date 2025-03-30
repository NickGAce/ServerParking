from enum import Enum
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Annotated
from pydantic.functional_validators import AfterValidator


class PermissionType(str, Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"


def validate_permission_dates(v: Optional[datetime], info):
    """Валидация дат в зависимости от типа разрешения"""
    if info.data.get('permission_type') == PermissionType.PERMANENT and v is not None:
        raise ValueError("Постоянные разрешения не могут иметь дату окончания")
    if info.data.get('permission_type') == PermissionType.TEMPORARY and v is None:
        raise ValueError("Временные разрешения требуют указания даты окончания")
    return v

ValidUntilDate = Annotated[Optional[datetime], AfterValidator(validate_permission_dates)]


class AccessPermissionBase(BaseModel):
    vehicle_id: int
    parking_spot_id: Optional[int] = None
    permission_type: PermissionType
    valid_until: ValidUntilDate
    is_accepted: Optional[bool] = None  # Новое поле для статуса подтверждения
    granted_by: Optional[int] = None

    @field_validator('parking_spot_id')
    @classmethod
    def validate_parking_spot(cls, v: Optional[int], values) -> Optional[int]:
        """Проверка что постоянные разрешения не привязаны к месту"""
        if values.data.get('permission_type') == PermissionType.PERMANENT and v is not None:
            raise ValueError("Постоянные разрешения не должны быть привязаны к конкретному месту")
        return v


class AccessPermissionCreate(AccessPermissionBase):
    """Схема для создания разрешения"""
    pass


class AccessPermissionUpdate(BaseModel):
    """Схема для обновления разрешения"""
    parking_spot_id: Optional[int] = None
    permission_type: Optional[PermissionType] = None
    valid_until: ValidUntilDate = None
    is_accepted: Optional[bool] = None  # Новое поле для обновления статуса

    @field_validator('is_accepted')
    @classmethod
    def validate_acceptance(cls, v: Optional[bool], values) -> Optional[bool]:
        """Проверка что временные разрешения требуют подтверждения"""
        if (values.data.get('permission_type') == PermissionType.TEMPORARY
            and v is None):
            raise ValueError("Временные разрешения требуют явного подтверждения")
        return v


class AccessPermissionResponse(AccessPermissionBase):
    """Схема ответа с полными данными разрешения"""
    id: int
    valid_from: datetime
    vehicle: Optional[dict] = None  # Вложенные данные транспортного средства
    parking_spot: Optional[dict] = None  # Вложенные данные парковочного места
    grantor: Optional[dict] = None  # Данные выдавшего разрешение

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "vehicle_id": 5,
                "parking_spot_id": 12,
                "permission_type": "temporary",
                "valid_from": "2023-05-20T12:00:00Z",
                "valid_until": "2023-06-20T12:00:00Z",
                "is_accepted": False,
                "granted_by": 3,
                "vehicle": {"id": 5, "license_plate": "А123БВ77"},
                "parking_spot": {"id": 12, "spot_number": "A12"},
                "grantor": {"id": 3, "username": "admin"}
            }
        }
    )