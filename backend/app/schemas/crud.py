from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Any

# Users
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "viewer"

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None

# Air Quality Data
class AirQualityDataCreate(BaseModel):
    station_id: int
    timestamp: datetime
    pm25: float | None = None
    pm10: float | None = None
    no2: float | None = None
    so2: float | None = None
    co: float | None = None
    o3: float | None = None
    nh3: float | None = None

class AirQualityDataUpdate(BaseModel):
    pm25: float | None = None
    pm10: float | None = None
    no2: float | None = None
    so2: float | None = None
    co: float | None = None
    o3: float | None = None
    nh3: float | None = None

# Satellite Data
class SatelliteDataCreate(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    pollutant: str
    value: float
    source: str = "Sentinel-5P"
    metadata_json: dict[str, Any] | None = None

class SatelliteDataUpdate(BaseModel):
    value: float | None = None
    metadata_json: dict[str, Any] | None = None

# Weather Data
class WeatherDataCreate(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    pressure: float | None = None
    source: str = "ERA5"

class WeatherDataUpdate(BaseModel):
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    pressure: float | None = None

# Fire Data
class FireDataCreate(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    brightness: float | None = None
    confidence: float | None = None
    frp: float | None = None
    source: str = "NASA FIRMS"

class FireDataUpdate(BaseModel):
    brightness: float | None = None
    confidence: float | None = None
    frp: float | None = None

# HCHO Hotspots
class HCHOHotspotCreate(BaseModel):
    cluster_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    hcho_mean: float
    hcho_max: float
    point_count: int
    intensity: str
    metadata_json: dict[str, Any] | None = None

class HCHOHotspotUpdate(BaseModel):
    hcho_mean: float | None = None
    hcho_max: float | None = None
    point_count: int | None = None
    intensity: str | None = None

# Predictions
class PredictionCreate(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    predicted_pm25: float
    predicted_aqi: float
    aqi_category: str
    model_version: str
    features: dict[str, Any] | None = None
    shap_values: dict[str, Any] | None = None

class PredictionUpdate(BaseModel):
    predicted_pm25: float | None = None
    predicted_aqi: float | None = None
    aqi_category: str | None = None
