from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.db.session import get_db
from app.db.models import ParkingSpot, SpotStatus

parking_load_router = APIRouter(
    prefix="/parking-load",
    tags=["parking-load"]
)


@parking_load_router.get("/overview")
def parking_overview(db: Session = Depends(get_db)):
    """Общая загрузка парковки."""
    total_spots = db.query(ParkingSpot).count()
    occupied = db.query(ParkingSpot).filter(ParkingSpot.status == SpotStatus.OCCUPIED).count()
    available = db.query(ParkingSpot).filter(ParkingSpot.status == SpotStatus.AVAILABLE).count()
    blocked = db.query(ParkingSpot).filter(ParkingSpot.status == SpotStatus.BLOCKED).count()
    return {
        "total_spots": total_spots,
        "occupied": occupied,
        "available": available,
        "blocked": blocked
    }


@parking_load_router.get("/available-by-type")
def available_spots_by_type(db: Session = Depends(get_db)):
    """Количество свободных мест по типу."""
    available_counts = (
        db.query(ParkingSpot.type, func.count())
        .filter(ParkingSpot.status == SpotStatus.AVAILABLE)
        .group_by(ParkingSpot.type)
        .all()
    )
    return {spot_type: count for spot_type, count in available_counts}


@parking_load_router.get("/occupancy-history")
def occupancy_history(days: int = 7, db: Session = Depends(get_db)):
    """История загрузки парковки за последние N дней."""
    today = datetime.utcnow()
    history = []
    for i in range(days):
        day = today - timedelta(days=i)
        occupied_count = (
            db.query(ParkingSpot)
            .filter(ParkingSpot.status == SpotStatus.OCCUPIED, ParkingSpot.reserved_until >= day)
            .count()
        )
        history.append({"date": day.strftime("%Y-%m-%d"), "occupied": occupied_count})
    return history


@parking_load_router.get("/detailed-status")
def detailed_parking_status(db: Session = Depends(get_db)):
    """Подробная информация о парковке (по статусу и типу)."""
    status_counts = (
        db.query(ParkingSpot.type, ParkingSpot.status, func.count())
        .group_by(ParkingSpot.type, ParkingSpot.status)
        .all()
    )
    stats = {}
    for spot_type, status, count in status_counts:
        if spot_type not in stats:
            stats[spot_type] = {}
        stats[spot_type][status] = count
    return stats
