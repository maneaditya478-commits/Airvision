from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import HCHOHotspot
from app.repositories.hcho import hcho_hotspot_repository
from app.repositories.satellite import satellite_data_repository
from app.services.ml.hcho_detector import hcho_detector

class HCHOHotspotService:
    async def get_hotspots(self, db: AsyncSession, hours: int = 72) -> list[HCHOHotspot]:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        hotspots = await hcho_hotspot_repository.get_by_time_range(db, since=since)
        if not hotspots:
            # Trigger detection
            return await self.detect_and_store(db, hours)
        return hotspots

    async def detect_and_store(self, db: AsyncSession, hours: int = 72) -> list[HCHOHotspot]:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        readings = await satellite_data_repository.get_by_pollutant_and_time(db, pollutant="HCHO", since=since)
        if not readings:
            return []

        reading_dicts = [
            {"latitude": r.latitude, "longitude": r.longitude, "value": r.value}
            for r in readings
        ]
        detected = hcho_detector.detect(reading_dicts)

        results = []
        for hs in detected:
            hotspot = await hcho_hotspot_repository.create(
                db,
                obj_in={
                    "cluster_id": hs["cluster_id"],
                    "timestamp": datetime.now(timezone.utc),
                    "latitude": hs["latitude"],
                    "longitude": hs["longitude"],
                    "hcho_mean": hs["hcho_mean"],
                    "hcho_max": hs["hcho_max"],
                    "point_count": hs["point_count"],
                    "intensity": hs["intensity"],
                }
            )
            results.append(hotspot)
        return results

    async def get_timeseries(self, db: AsyncSession, days: int = 7) -> dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        hotspots = await hcho_hotspot_repository.get_by_time_range(db, since=since)

        by_date: dict[str, list[dict[str, Any]]] = {}
        for h in hotspots:
            date_key = h.timestamp.strftime("%Y-%m-%d")
            by_date.setdefault(date_key, []).append({
                "hcho_mean": h.hcho_mean,
                "intensity": h.intensity,
            })

        return hcho_detector.temporal_analysis(by_date)

hcho_service = HCHOHotspotService()
