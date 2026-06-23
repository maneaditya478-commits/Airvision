from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WeatherData
from app.repositories.base import BaseRepository

class WeatherDataRepository(BaseRepository[WeatherData]):
    async def get_by_time_range(
        self, db: AsyncSession, *, since: datetime
    ) -> list[WeatherData]:
        result = await db.execute(
            select(self.model)
            .where(self.model.timestamp >= since)
        )
        return list(result.scalars().all())

weather_data_repository = WeatherDataRepository(WeatherData)
