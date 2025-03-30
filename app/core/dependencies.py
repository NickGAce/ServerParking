from fastapi import Depends, HTTPException, Security, status
from app.core.security import get_current_user
from app.db.models import User, UserRole


def admin_required(current_user: User = Security(get_current_user)):
    """Только для админов (оставляем для совместимости)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user


# def role_required(required_role: str):
#     """Новая зависимость для проверки ролей"""
#     def dependency(current_user: User = Security(get_current_user)):
#         if not current_user.is_admin and current_user.role != required_role:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Требуется роль: {required_role}"
#             )
#         return current_user
#     return dependency


def require_manager(current_user: User = Depends(get_current_user)):
    """Только менеджеры (company)"""
    print(f"DEBUG: User {current_user.username} has role {current_user.role} need {UserRole.MANAGER}")  # Отладка
    if current_user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль менеджера"
        )
    return current_user


def require_tenant(current_user: User = Depends(get_current_user)):
    """Только арендаторы"""
    if current_user.role not in [UserRole.TENANT, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль арендатора"
        )
    return current_user


def require_resident(current_user: User = Depends(get_current_user)):
    """Только резиденты"""
    if current_user.role not in [UserRole.RESIDENT, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль резидента"
        )
    return current_user


