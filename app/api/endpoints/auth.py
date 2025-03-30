from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.dependencies import admin_required, require_manager
from app.db.session import get_db
from app.db.repositories.user import get_user_by_username, check_admin_exists, create_user, authenticate_user
from app.schemas.user import UserCreate, UserResponse
from app.core.security import create_access_token, get_current_user
from app.db.models import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",  # Полный путь
    scheme_name="OAuth2PasswordBearer",
    scopes={"openid": "OpenID scope"}
)

public_router = APIRouter()
protected_router = APIRouter(dependencies=[Depends(oauth2_scheme)])


@public_router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация пользователя. Первый регистрируемый становится админом."""

    # Проверяем, есть ли уже администратор
    is_admin = not check_admin_exists(db)

    # Проверяем, существует ли пользователь
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Создаём нового пользователя
    new_user = create_user(db, user, is_admin=is_admin)
    return new_user


@public_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Авторизация пользователя с выдачей JWT-токена"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "user_role": user.role}




