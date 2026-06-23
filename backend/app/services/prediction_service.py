from datetime import datetime, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Prediction, AQICategory
from app.repositories.prediction import prediction_repository
from app.services.ml.aqi_predictor import predictor

class PredictionService:
    async def predict_aqi(self, db: AsyncSession, features: dict[str, Any]) -> dict[str, Any]:
        result = predictor.predict(features)
        
        # Save to database
        pred_obj = await prediction_repository.create(
            db,
            obj_in={
                "timestamp": datetime.now(timezone.utc),
                "latitude": features.get("latitude", 28.6),
                "longitude": features.get("longitude", 77.2),
                "predicted_pm25": result["predicted_pm25"],
                "predicted_aqi": result["predicted_aqi"],
                "aqi_category": AQICategory(result["aqi_category"]),
                "model_version": result["model_version"],
                "features": {k: v for k, v in features.items() if k not in ["latitude", "longitude"]},
                "shap_values": result.get("shap_values"),
            }
        )
        return result

    async def get_history(self, db: AsyncSession, limit: int = 50) -> list[Prediction]:
        return await prediction_repository.get_recent_predictions(db, limit=limit)

    async def get_shap_explanation(self, lat: float, lon: float) -> dict[str, Any]:
        result = predictor.predict({"latitude": lat, "longitude": lon})
        shap_vals = result.get("shap_values") or {}
        importance = predictor.get_feature_importance()

        pollutant_keys = ["no2", "so2", "co", "o3"]
        contributions = {k: abs(shap_vals.get(k, 0)) for k in pollutant_keys}
        total = sum(contributions.values()) or 1.0
        contributions = {k: round(v / total * 100, 2) for k, v in contributions.items()}

        return {
            "feature_importance": importance,
            "pollutant_contributions": contributions,
            "base_value": round(result["predicted_pm25"] - sum(shap_vals.values()), 2),
            "prediction": result["predicted_pm25"],
        }

prediction_service = PredictionService()
