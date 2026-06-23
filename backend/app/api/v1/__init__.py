from fastapi import APIRouter

from app.api.v1 import admin, auth, dashboard, fire, hotspots, prediction, transport

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(prediction.router)
api_router.include_router(hotspots.router)
api_router.include_router(fire.router)
api_router.include_router(transport.router)
api_router.include_router(admin.router)
