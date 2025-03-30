#!/bin/bash

# Останавливаем сервер, если он уже запущен (необязательно, но полезно)
pkill -f "uvicorn app.main:app"

# Запускаем сервер FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


Response body

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0MzE4OTgzMH0.tYIwv_NcdtI0v_hJz8G2AY25ZGqDzyYPZFr1pDLXqnE",
  "token_type": "bearer"
}