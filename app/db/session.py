from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Подключаемся к PostgreSQL
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Создаёт и закрывает сессию базы данных."""
    db = SessionLocal()
    try:
        yield db  # Передаём сессию
    finally:
        db.close()  # Закрываем после использования
