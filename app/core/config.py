import os
from pathlib import Path
from dotenv import load_dotenv

# Правильный путь к .env (в корне проекта, а не в папке app)
env_path = Path(__file__).parent.parent.parent / ".env"
print(f"Пытаемся загрузить .env из: {env_path}")

if not env_path.exists():
    raise FileNotFoundError(f"Файл .env не найден по пути: {env_path}")

load_dotenv(env_path, override=True)


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL не найден в .env файле")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()
