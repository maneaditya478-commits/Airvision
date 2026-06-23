from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.auth import get_current_analyst, get_current_user
from app.models import User
from app.services.air_quality_service import air_quality_service
from app.services.satellite_service import satellite_service
from app.services.weather_service import weather_service
from app.services.fire_service import fire_service
from app.services.hcho_service import hcho_service
from app.services.prediction_service import prediction_service

router = APIRouter(tags=["AirVision India API"])

# Upload Ingestions
@router.post("/upload/cpcb")
async def upload_cpcb(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_analyst)
):
    return await air_quality_service.ingest_cpcb_file(db, file)

@router.post("/upload/sentinel")
async def upload_sentinel(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_analyst)
):
    return await satellite_service.ingest_sentinel_file(db, file)

@router.post("/upload/weather")
async def upload_weather(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_analyst)
):
    return await weather_service.ingest_weather_file(db, file)

@router.post("/upload/fire")
async def upload_fire(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_analyst)
):
    return await fire_service.ingest_fire_file(db, file)


# AQI Queries
@router.get("/aqi/current")
async def get_current_aqi(db: AsyncSession = Depends(get_db)):
    return await air_quality_service.get_current_aqi(db)

@router.get("/aqi/predict")
async def predict_aqi(
    latitude: float = Query(..., ge=6.0, le=37.0),
    longitude: float = Query(..., ge=68.0, le=98.0),
    no2: float | None = Query(None),
    so2: float | None = Query(None),
    co: float | None = Query(None),
    o3: float | None = Query(None),
    temperature: float | None = Query(None),
    humidity: float | None = Query(None),
    wind_speed: float | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    features = {
        "latitude": latitude,
        "longitude": longitude,
        "no2": no2,
        "so2": so2,
        "co": co,
        "o3": o3,
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
    }
    return await prediction_service.predict_aqi(db, features)


# HCHO Queries
@router.get("/hcho/hotspots")
async def get_hcho_hotspots(
    hours: int = Query(72, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    return await hcho_service.get_hotspots(db, hours)

@router.get("/hcho/timeseries")
async def get_hcho_timeseries(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    return await hcho_service.get_timeseries(db, days)


# Fire Queries
@router.get("/fire/correlation")
async def get_fire_correlation(
    hours: int = Query(72, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    return await fire_service.get_correlation(db, hours)


# Explainability Queries
@router.get("/explainability/shap")
async def get_shap_explainability(
    latitude: float = Query(..., ge=6.0, le=37.0),
    longitude: float = Query(..., ge=68.0, le=98.0),
):
    return await prediction_service.get_shap_explanation(latitude, longitude)
