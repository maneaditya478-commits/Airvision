from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import FireData, SatelliteData
from app.schemas import FireCorrelationResponse, FireDataResponse, MapPoint
from app.services.ml.fire_correlation import fire_correlation_service

router = APIRouter(prefix="/fire", tags=["Fire Correlation"])


@router.get("/points", response_model=list[FireDataResponse])
async def get_fire_points(
    hours: int = Query(48, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = await db.execute(
        select(FireData).where(FireData.timestamp >= since).order_by(FireData.timestamp.desc())
    )
    return result.scalars().all()


@router.get("/map", response_model=list[MapPoint])
async def fire_map(hours: int = Query(48), db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = await db.execute(select(FireData).where(FireData.timestamp >= since))
    return [
        MapPoint(
            latitude=f.latitude, longitude=f.longitude,
            value=f.frp or 0, label=f"FRP: {f.frp}",
        )
        for f in result.scalars().all()
    ]


@router.get("/correlation", response_model=FireCorrelationResponse)
async def fire_hcho_correlation(hours: int = Query(72), db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    fires = await db.execute(select(FireData).where(FireData.timestamp >= since))
    fire_list = [
        {"latitude": f.latitude, "longitude": f.longitude, "frp": f.frp}
        for f in fires.scalars().all()
    ]

    hcho = await db.execute(
        select(SatelliteData)
        .where(SatelliteData.pollutant == "HCHO", SatelliteData.timestamp >= since)
    )
    hcho_list = [
        {"latitude": r.latitude, "longitude": r.longitude, "value": r.value}
        for r in hcho.scalars().all()
    ]

    result = fire_correlation_service.correlate(fire_list, hcho_list)
    return FireCorrelationResponse(**result)
