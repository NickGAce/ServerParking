# app/db/repositories/admin.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import User, UserRole
from app.schemas.user import UserUpdateRole


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self) -> List[User]:
        """Получить список всех пользователей"""
        return self.db.query(User).order_by(User.id).all()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user_role(self, user_id: int, role_data: UserUpdateRole) -> Optional[User]:
        """Обновить роль пользователя"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Проверка допустимых ролей
        if role_data.role not in [role.value for role in UserRole]:
            return None

        user.role = role_data.role
        self.db.commit()
        self.db.refresh(user)
        return user

    def grant_admin_role(self, user_id: int) -> Optional[User]:
        """Назначить пользователя администратором"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        user.is_admin = True
        user.role = UserRole.ADMIN
        self.db.commit()
        self.db.refresh(user)
        return user

    def revoke_admin_role(self, user_id: int) -> Optional[User]:
        """Отозвать права администратора"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        user.is_admin = False
        user.role = UserRole.RESIDENT  # Или другая роль по умолчанию
        self.db.commit()
        self.db.refresh(user)
        return user

    def search_users(self, query: str) -> List[User]:
        """Поиск пользователей по email или username"""
        return self.db.query(User).filter(
            (User.email.ilike(f"%{query}%")) |
            (User.username.ilike(f"%{query}%"))
        ).all()