from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import HCHOHotspot
from app.repositories.base import BaseRepository

class HCHOHotspotRepository(BaseRepository[HCHOHotspot]):
    async def get_by_time_range(
        self, db: AsyncSession, *, since: datetime
    ) -> list[HCHOHotspot]:
        result = await db.execute(
            select(self.model)
            .where(self.model.timestamp >= since)
            .order_by(self.model.hcho_mean.desc())
        )
        return list(result.scalars().all())

    async def get_latest_hotspots(
        self, db: AsyncSession, *, limit: int = 50
    ) -> list[HCHOHotspot]:
        result = await db.execute(
            select(self.model)
            .order_by(self.model.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

hcho_hotspot_repository = HCHOHotspotRepository(HCHOHotspot)
