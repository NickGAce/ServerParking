from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.user import UserResponse, UserUpdateRole  # Исправил импорт схем
from app.core.dependencies import admin_required
from app.db.repositories.admin import AdminRepository

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(admin_required)
):
    """Получить список всех пользователей"""
    repo = AdminRepository(db)
    return repo.get_all_users()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_details(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(admin_required)
):
    """Получить информацию о пользователе"""
    repo = AdminRepository(db)
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
        user_id: int,
        role_data: UserUpdateRole,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(admin_required)
):
    """Изменить роль пользователя"""
    repo = AdminRepository(db)

    # Дополнительные проверки
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя изменить свою роль"
        )

    user = repo.update_user_role(user_id, role_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден или недопустимая роль"
        )
    return user


@router.get("/users/search/{query}", response_model=List[UserResponse])
async def search_users(
        query: str,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(admin_required)
):
    """Поиск пользователей
    Поиск пользователей по email или username"""

    repo = AdminRepository(db)
    return repo.search_users(query)
