from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI
from app.api.endpoints.auth import public_router, protected_router
from app.api.endpoints.vehicles import vehicle_router
from app.api.endpoints.parking_spots import parking_spot_router
from app.api.endpoints.parking_places import router as parking_places
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.parking_load import parking_load_router


load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": "swagger-ui",
        "appName": "FastAPI Auth",
        "scopes": "openid profile",
        "useBasicAuthenticationWithAccessCodeGrant": True,
    }
)

app.include_router(
    public_router,
    prefix="/auth",
    tags=["Auth"]
)

app.include_router(
    protected_router,
    prefix="/auth",
    tags=["Auth"]
)

app.include_router(vehicle_router)

app.include_router(parking_spot_router)

app.include_router(parking_places)

app.include_router(admin_router)

app.include_router(parking_load_router)


@app.get("/")
def root():
    return {"message": "Server is running!"}