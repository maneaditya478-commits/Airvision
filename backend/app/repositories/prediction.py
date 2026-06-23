from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Prediction
from app.repositories.base import BaseRepository

class PredictionRepository(BaseRepository[Prediction]):
    async def get_recent_predictions(
        self, db: AsyncSession, *, limit: int = 50
    ) -> list[Prediction]:
        result = await db.execute(
            select(self.model)
            .order_by(self.model.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

prediction_repository = PredictionRepository(Prediction)
