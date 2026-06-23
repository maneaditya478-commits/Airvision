from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import HCHOHotspot, SatelliteData
from app.schemas import HotspotResponse, MapPoint
from app.services.ml.hcho_detector import hcho_detector

router = APIRouter(prefix="/hotspots", tags=["HCHO Hotspots"])


@router.get("/", response_model=list[HotspotResponse])
async def list_hotspots(
    hours: int = Query(72, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = await db.execute(
        select(HCHOHotspot).where(HCHOHotspot.timestamp >= since).order_by(HCHOHotspot.hcho_mean.desc())
    )
    hotspots = result.scalars().all()
    if not hotspots:
        return await _detect_and_store(db)
    return hotspots


@router.post("/detect", response_model=list[HotspotResponse])
async def detect_hotspots(db: AsyncSession = Depends(get_db)):
    return await _detect_and_store(db)


async def _detect_and_store(db: AsyncSession) -> list[HotspotResponse]:
    since = datetime.now(timezone.utc) - timedelta(hours=72)
    result = await db.execute(
        select(SatelliteData)
        .where(SatelliteData.pollutant == "HCHO", SatelliteData.timestamp >= since)
    )
    readings = result.scalars().all()
    if not readings:
        return []

    reading_dicts = [
        {"latitude": r.latitude, "longitude": r.longitude, "value": r.value}
        for r in readings
    ]
    detected = hcho_detector.detect(reading_dicts)

    for hs in detected:
        db.add(HCHOHotspot(
            cluster_id=hs["cluster_id"],
            timestamp=datetime.now(timezone.utc),
            latitude=hs["latitude"], longitude=hs["longitude"],
            hcho_mean=hs["hcho_mean"], hcho_max=hs["hcho_max"],
            point_count=hs["point_count"], intensity=hs["intensity"],
        ))
    await db.flush()

    result = await db.execute(
        select(HCHOHotspot).order_by(HCHOHotspot.hcho_mean.desc()).limit(20)
    )
    return result.scalars().all()


@router.get("/map", response_model=list[MapPoint])
async def hotspot_map(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HCHOHotspot).order_by(HCHOHotspot.timestamp.desc()).limit(50)
    )
    return [
        MapPoint(
            latitude=h.latitude, longitude=h.longitude,
            value=h.hcho_mean, category=h.intensity,
            label=f"Cluster {h.cluster_id}: {h.hcho_mean}",
        )
        for h in result.scalars().all()
    ]


@router.get("/temporal")
async def temporal_analysis(days: int = Query(7, ge=1, le=30), db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(HCHOHotspot).where(HCHOHotspot.timestamp >= since).order_by(HCHOHotspot.timestamp)
    )
    hotspots = result.scalars().all()

    by_date: dict[str, list] = {}
    for h in hotspots:
        date_key = h.timestamp.strftime("%Y-%m-%d")
        by_date.setdefault(date_key, []).append({
            "hcho_mean": h.hcho_mean, "intensity": h.intensity,
        })

    return hcho_detector.temporal_analysis(by_date)
