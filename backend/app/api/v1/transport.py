from fastapi import APIRouter, Query

from app.schemas import TransportPath, WindVector
from app.services.ml.transport_analyzer import transport_analyzer

router = APIRouter(prefix="/transport", tags=["Transport Analysis"])

INDIA_BOUNDS = {"min_lat": 6.0, "max_lat": 37.0, "min_lon": 68.0, "max_lon": 98.0}


@router.get("/wind", response_model=list[WindVector])
async def get_wind_vectors(resolution: float = Query(3.0, ge=1.0, le=5.0)):
    vectors = transport_analyzer.generate_wind_grid(INDIA_BOUNDS, resolution)
    return [WindVector(**v) for v in vectors]


@router.get("/path", response_model=TransportPath)
async def estimate_transport_path(
    lat: float = Query(28.6, ge=6, le=37),
    lon: float = Query(77.2, ge=68, le=98),
    hours: float = Query(24, ge=1, le=72),
):
    vectors = transport_analyzer.generate_wind_grid(
        {"min_lat": lat - 0.5, "max_lat": lat + 0.5, "min_lon": lon - 0.5, "max_lon": lon + 0.5},
        resolution=1.0,
    )
    if vectors:
        u, v = vectors[0]["u_component"], vectors[0]["v_component"]
    else:
        u, v = 2.0, 1.0

    result = transport_analyzer.estimate_transport_path(lat, lon, u, v, hours)
    return TransportPath(**result)
