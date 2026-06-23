from datetime import datetime
from pydantic import BaseModel, Field
from app.core.security import Token, UserCreate, UserResponse


class StationResponse(BaseModel):
    id: int
    station_id: str
    name: str
    city: str
    state: str
    latitude: float
    longitude: float

    model_config = {"from_attributes": True}


class AirQualityDataResponse(BaseModel):
    id: int
    station_id: int
    timestamp: datetime
    pm25: float | None
    pm10: float | None
    no2: float | None
    so2: float | None
    co: float | None
    o3: float | None
    aqi: float | None
    aqi_category: str | None

    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    total_stations: int
    avg_aqi: float
    category_distribution: dict[str, int]
    worst_city: str | None
    best_city: str | None
    last_updated: datetime | None


class AQITrendPoint(BaseModel):
    date: str
    avg_aqi: float
    avg_pm25: float
    station_count: int


class MapPoint(BaseModel):
    latitude: float
    longitude: float
    value: float
    category: str | None = None
    label: str | None = None


class PredictionRequest(BaseModel):
    latitude: float = Field(..., ge=6.0, le=37.0)
    longitude: float = Field(..., ge=68.0, le=98.0)
    no2: float | None = None
    so2: float | None = None
    co: float | None = None
    o3: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None


class PredictionResponse(BaseModel):
    latitude: float
    longitude: float
    predicted_pm25: float
    predicted_aqi: float
    aqi_category: str
    dominant_pollutant: str
    model_version: str
    shap_values: dict[str, float] | None = None


class HotspotResponse(BaseModel):
    id: int
    cluster_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    hcho_mean: float
    hcho_max: float
    point_count: int
    intensity: str

    model_config = {"from_attributes": True}


class FireDataResponse(BaseModel):
    id: int
    timestamp: datetime
    latitude: float
    longitude: float
    brightness: float | None
    confidence: float | None
    frp: float | None

    model_config = {"from_attributes": True}


class FireCorrelationResponse(BaseModel):
    fire_count: int
    avg_hcho_near_fires: float
    avg_hcho_away_from_fires: float
    correlation_coefficient: float
    hotspots_near_fires: int


class WindVector(BaseModel):
    latitude: float
    longitude: float
    u_component: float
    v_component: float
    speed: float
    direction: float


class TransportPath(BaseModel):
    origin_lat: float
    origin_lon: float
    path: list[dict[str, float]]
    estimated_hours: float


class SHAPExplanation(BaseModel):
    feature_importance: dict[str, float]
    pollutant_contributions: dict[str, float]
    base_value: float
    prediction: float


class DatasetCreate(BaseModel):
    name: str
    source: str
    metadata_json: dict | None = None


class DatasetResponse(BaseModel):
    id: int
    name: str
    source: str
    status: str
    record_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ModelResponse(BaseModel):
    id: int
    name: str
    model_type: str
    version: str
    status: str
    metrics: dict | None
    trained_at: datetime | None

    model_config = {"from_attributes": True}


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
