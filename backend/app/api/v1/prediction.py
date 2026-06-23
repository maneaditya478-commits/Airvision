from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Prediction
from app.schemas import MapPoint, PredictionRequest, PredictionResponse, SHAPExplanation
from app.services.ml.aqi_predictor import predictor

router = APIRouter(prefix="/prediction", tags=["AQI Prediction"])


@router.post("/predict", response_model=PredictionResponse)
async def predict_aqi(request: PredictionRequest):
    result = predictor.predict(request.model_dump())
    return PredictionResponse(
        latitude=request.latitude,
        longitude=request.longitude,
        predicted_pm25=result["predicted_pm25"],
        predicted_aqi=result["predicted_aqi"],
        aqi_category=result["aqi_category"],
        dominant_pollutant=result["dominant_pollutant"],
        model_version=result["model_version"],
        shap_values=result.get("shap_values"),
    )


@router.get("/heatmap", response_model=list[MapPoint])
async def get_prediction_heatmap(
    grid_size: float = Query(1.0, ge=0.5, le=5.0),
    db: AsyncSession = Depends(get_db),
):
    points = []
    lat = 8.0
    while lat <= 35.0:
        lon = 68.0
        while lon <= 92.0:
            result = predictor.predict({"latitude": lat, "longitude": lon})
            points.append(MapPoint(
                latitude=lat, longitude=lon,
                value=result["predicted_aqi"],
                category=result["aqi_category"],
            ))
            lon += grid_size
        lat += grid_size
    return points


@router.get("/history", response_model=list[PredictionResponse])
async def get_prediction_history(limit: int = Query(50, le=200), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Prediction).order_by(Prediction.timestamp.desc()).limit(limit)
    )
    preds = result.scalars().all()
    return [
        PredictionResponse(
            latitude=p.latitude, longitude=p.longitude,
            predicted_pm25=p.predicted_pm25, predicted_aqi=p.predicted_aqi,
            aqi_category=p.aqi_category.value, dominant_pollutant="pm25",
            model_version=p.model_version, shap_values=p.shap_values,
        )
        for p in preds
    ]


@router.get("/explain", response_model=SHAPExplanation)
async def explain_prediction(
    latitude: float = Query(28.6), longitude: float = Query(77.2),
):
    result = predictor.predict({"latitude": latitude, "longitude": longitude})
    shap_vals = result.get("shap_values") or {}
    importance = predictor.get_feature_importance()

    pollutant_keys = ["no2", "so2", "co", "o3"]
    contributions = {k: abs(shap_vals.get(k, 0)) for k in pollutant_keys}
    total = sum(contributions.values()) or 1
    contributions = {k: round(v / total * 100, 2) for k, v in contributions.items()}

    return SHAPExplanation(
        feature_importance=importance,
        pollutant_contributions=contributions,
        base_value=round(result["predicted_pm25"] - sum(shap_vals.values()), 2),
        prediction=result["predicted_pm25"],
    )
