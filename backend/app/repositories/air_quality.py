from datetime import datetime
from typing import Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AirQualityData, AirQualityStation
from app.repositories.base import BaseRepository

class AirQualityDataRepository(BaseRepository[AirQualityData]):
    async def get_recent_readings(
        self, db: AsyncSession, *, station_id: int | None = None, limit: int = 100
    ) -> list[AirQualityData]:
        query = select(self.model).order_by(self.model.timestamp.desc()).limit(limit)
        if station_id is not None:
            query = query.where(self.model.station_id == station_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_latest_readings_all_stations(self, db: AsyncSession) -> list[tuple[AirQualityData, AirQualityStation]]:
        latest_subq = (
            select(
                self.model.station_id,
                func.max(self.model.timestamp).label("max_ts"),
            )
            .group_by(self.model.station_id)
            .subquery()
        )
        query = (
            select(self.model, AirQualityStation)
            .join(AirQualityStation, self.model.station_id == AirQualityStation.id)
            .join(
                latest_subq,
                (self.model.station_id == latest_subq.c.station_id)
                & (self.model.timestamp == latest_subq.c.max_ts),
            )
        )
        result = await db.execute(query)
        return list(result.all())

    async def get_trends(self, db: AsyncSession, *, since: datetime) -> list[tuple[Any, Any, Any, Any]]:
        query = (
            select(
                func.date(self.model.timestamp).label("date"),
                func.avg(self.model.aqi).label("avg_aqi"),
                func.avg(self.model.pm25).label("avg_pm25"),
                func.count(self.model.id).label("count"),
            )
            .where(self.model.timestamp >= since)
            .group_by(func.date(self.model.timestamp))
            .order_by(func.date(self.model.timestamp))
        )
        result = await db.execute(query)
        return list(result.all())

class AirQualityStationRepository(BaseRepository[AirQualityStation]):
    async def get_by_station_id(self, db: AsyncSession, station_id: str) -> AirQualityStation | None:
        result = await db.execute(select(self.model).where(self.model.station_id == station_id))
        return result.scalar_one_or_none()

    async def get_active_stations(self, db: AsyncSession) -> list[AirQualityStation]:
        result = await db.execute(select(self.model).where(self.model.is_active == True))
        return list(result.scalars().all())

air_quality_data_repository = AirQualityDataRepository(AirQualityData)
air_quality_station_repository = AirQualityStationRepository(AirQualityStation)
