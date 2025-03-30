from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password


def get_user_by_username(db: Session, username: str):
    """Получение пользователя по username"""
    return db.query(User).filter(User.username == username).first()


def check_admin_exists(db: Session) -> bool:
    """Проверяем, есть ли в системе хотя бы один администратор"""
    return db.query(User).filter(User.is_admin == True).first() is not None


def create_user(db: Session, user: UserCreate, is_admin: bool = False):
    """Создание нового пользователя"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    """Проверять пароль при входе"""
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user