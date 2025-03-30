from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import Optional
from datetime import datetime
from app.db.models import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="ivanov")
    email: EmailStr = Field(..., example="user@example.com")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="strongpassword123")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, example="new_username")
    email: Optional[EmailStr] = Field(None, example="new_email@example.com")


class UserUpdateRole(BaseModel):
    role: UserRole = Field(..., example="resident")


class UserResponse(UserBase):
    id: int = Field(..., example=1)
    is_admin: bool = Field(False, example=False)
    role: UserRole = Field(..., example="resident")
    created_at: datetime = Field(..., example="2023-01-01T00:00:00")

    class Config:
        from_attributes = True  # Вместо orm_mode
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserAdminResponse(UserResponse):
    last_login: Optional[datetime] = Field(None, example="2023-01-01T00:00:00")

    class Config:
        json_schema_extra = {  # Вместо schema_extra
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "is_admin": True,
                "role": "admin",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "last_login": "2023-01-02T12:00:00"
            }
        }


class UserListResponse(BaseModel):
    users: list[UserResponse]
    count: int = Field(..., example=10)
