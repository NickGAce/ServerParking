import os
from pathlib import Path
from dotenv import load_dotenv

print("Текущая рабочая директория:", os.getcwd())
env_path = Path('.') / '.env'
print(f"Путь к .env: {env_path} (существует: {env_path.exists()})")

load_dotenv(env_path)
print("DATABASE_URL из окружения:", os.getenv("DATABASE_URL"))