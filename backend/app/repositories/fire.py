from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import FireData
from app.repositories.base import BaseRepository

class FireDataRepository(BaseRepository[FireData]):
    async def get_by_time_range(
        self, db: AsyncSession, *, since: datetime
    ) -> list[FireData]:
        result = await db.execute(
            select(self.model)
            .where(self.model.timestamp >= since)
            .order_by(self.model.timestamp.desc())
        )
        return list(result.scalars().all())

fire_data_repository = FireDataRepository(FireData)
