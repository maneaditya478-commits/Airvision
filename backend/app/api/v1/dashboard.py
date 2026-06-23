from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AirQualityData, AirQualityStation, AQICategory
from app.schemas import (
    AirQualityDataResponse,
    AQITrendPoint,
    DashboardSummary,
    MapPoint,
    StationResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    station_count = await db.scalar(select(func.count(AirQualityStation.id)))

    latest_subq = (
        select(
            AirQualityData.station_id,
            func.max(AirQualityData.timestamp).label("max_ts"),
        )
        .group_by(AirQualityData.station_id)
        .subquery()
    )

    latest_readings = await db.execute(
        select(AirQualityData)
        .join(
            latest_subq,
            (AirQualityData.station_id == latest_subq.c.station_id)
            & (AirQualityData.timestamp == latest_subq.c.max_ts),
        )
    )
    readings = latest_readings.scalars().all()

    avg_aqi = sum(r.aqi or 0 for r in readings) / len(readings) if readings else 0
    category_dist = {cat.value: 0 for cat in AQICategory}
    for r in readings:
        if r.aqi_category:
            category_dist[r.aqi_category.value] += 1

    city_aqi: dict[str, list[float]] = {}
    for r in readings:
        station = await db.get(AirQualityStation, r.station_id)
        if station and r.aqi:
            city_aqi.setdefault(station.city, []).append(r.aqi)

    worst = max(city_aqi, key=lambda c: sum(city_aqi[c]) / len(city_aqi[c])) if city_aqi else None
    best = min(city_aqi, key=lambda c: sum(city_aqi[c]) / len(city_aqi[c])) if city_aqi else None

    return DashboardSummary(
        total_stations=station_count or 0,
        avg_aqi=round(avg_aqi, 1),
        category_distribution=category_dist,
        worst_city=worst,
        best_city=best,
        last_updated=max((r.timestamp for r in readings), default=None),
    )


@router.get("/trends", response_model=list[AQITrendPoint])
async def get_aqi_trends(days: int = Query(30, ge=1, le=90), db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(AirQualityData.timestamp).label("date"),
            func.avg(AirQualityData.aqi).label("avg_aqi"),
            func.avg(AirQualityData.pm25).label("avg_pm25"),
            func.count(AirQualityData.id).label("count"),
        )
        .where(AirQualityData.timestamp >= since)
        .group_by(func.date(AirQualityData.timestamp))
        .order_by(func.date(AirQualityData.timestamp))
    )
    return [
        AQITrendPoint(date=str(row.date), avg_aqi=round(row.avg_aqi or 0, 1),
                      avg_pm25=round(row.avg_pm25 or 0, 1), station_count=row.count)
        for row in result.all()
    ]


@router.get("/map", response_model=list[MapPoint])
async def get_aqi_map(db: AsyncSession = Depends(get_db)):
    latest_subq = (
        select(AirQualityData.station_id, func.max(AirQualityData.timestamp).label("max_ts"))
        .group_by(AirQualityData.station_id).subquery()
    )
    result = await db.execute(
        select(AirQualityData, AirQualityStation)
        .join(AirQualityStation, AirQualityData.station_id == AirQualityStation.id)
        .join(latest_subq, (AirQualityData.station_id == latest_subq.c.station_id)
              & (AirQualityData.timestamp == latest_subq.c.max_ts))
    )
    return [
        MapPoint(
            latitude=s.latitude, longitude=s.longitude,
            value=r.aqi or 0, category=r.aqi_category.value if r.aqi_category else None,
            label=f"{s.city}: AQI {r.aqi}",
        )
        for r, s in result.all()
    ]


@router.get("/stations", response_model=list[StationResponse])
async def list_stations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AirQualityStation).where(AirQualityStation.is_active == True))
    return result.scalars().all()


@router.get("/readings", response_model=list[AirQualityDataResponse])
async def get_recent_readings(
    station_id: int | None = None, limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(AirQualityData).order_by(AirQualityData.timestamp.desc()).limit(limit)
    if station_id:
        query = query.where(AirQualityData.station_id == station_id)
    result = await db.execute(query)
    return result.scalars().all()
