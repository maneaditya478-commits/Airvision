from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import SatelliteData
from app.repositories.base import BaseRepository

class SatelliteDataRepository(BaseRepository[SatelliteData]):
    async def get_by_pollutant_and_time(
        self, db: AsyncSession, pollutant: str, *, since: datetime
    ) -> list[SatelliteData]:
        result = await db.execute(
            select(self.model)
            .where(self.model.pollutant == pollutant, self.model.timestamp >= since)
        )
        return list(result.scalars().all())

satellite_data_repository = SatelliteDataRepository(SatelliteData)
