from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1 import api_router
from app.api.endpoints import router as new_api_endpoints_router
from app.api.crud import crud_router
from app.config import get_settings
from app.database import Base, SyncSessionLocal, engine
from app.schemas import HealthResponse
from app.services.seed_data import seed_database

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SyncSessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    from app.services.ml.aqi_predictor import predictor
    if predictor.model is None:
        predictor.train()

    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AirVision India - ISRO PS-3: Surface AQI & HCHO Hotspot Detection",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://airvision-nine.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(new_api_endpoints_router, prefix="/api")
app.include_router(crud_router, prefix="/api")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
@app.get("/healthz", response_model=HealthResponse, tags=["Health"])
async def health_check():
    db_status = "connected"
    redis_status = "connected"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    try:
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
    except Exception:
        redis_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.app_version,
        database=db_status,
        redis=redis_status,
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
