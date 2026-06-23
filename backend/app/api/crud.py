from typing import Any, TypeVar, Generic, Type
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.auth import get_current_admin
from app.models import (
    Base, User, AirQualityData, SatelliteData, WeatherData, FireData, HCHOHotspot, Prediction
)
from app.repositories import (
    user_repository, air_quality_data_repository, satellite_data_repository,
    weather_data_repository, fire_data_repository, hcho_hotspot_repository, prediction_repository
)
from app.schemas.crud import (
    UserCreate, UserUpdate, AirQualityDataCreate, AirQualityDataUpdate,
    SatelliteDataCreate, SatelliteDataUpdate, WeatherDataCreate, WeatherDataUpdate,
    FireDataCreate, FireDataUpdate, HCHOHotspotCreate, HCHOHotspotUpdate,
    PredictionCreate, PredictionUpdate
)
from app.repositories.base import BaseRepository

T = TypeVar("T", bound=Base)
C = TypeVar("C")
U = TypeVar("U")

class CRUDRouter(Generic[T, C, U]):
    def __init__(self, model_class: Type[T], repository: BaseRepository[T], create_schema: Type[C], update_schema: Type[U], prefix: str, tags: list[str]):
        self.model_class = model_class
        self.repository = repository
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.router = APIRouter(prefix=prefix, tags=tags)
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/", dependencies=[Depends(get_current_admin)])
        async def list_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
            return await self.repository.get_multi(db, skip=skip, limit=limit)

        @self.router.get("/{id}", dependencies=[Depends(get_current_admin)])
        async def get_item(id: int, db: AsyncSession = Depends(get_db)):
            item = await self.repository.get(db, id)
            if not item:
                raise HTTPException(status_code=404, detail=f"{self.model_class.__name__} not found")
            return item

        @self.router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_admin)])
        async def create_item(obj_in: self.create_schema, db: AsyncSession = Depends(get_db)):
            return await self.repository.create(db, obj_in=obj_in.model_dump())

        @self.router.put("/{id}", dependencies=[Depends(get_current_admin)])
        async def update_item(id: int, obj_in: self.update_schema, db: AsyncSession = Depends(get_db)):
            item = await self.repository.get(db, id)
            if not item:
                raise HTTPException(status_code=404, detail=f"{self.model_class.__name__} not found")
            return await self.repository.update(db, db_obj=item, obj_in=obj_in.model_dump(exclude_unset=True))

        @self.router.delete("/{id}", dependencies=[Depends(get_current_admin)])
        async def delete_item(id: int, db: AsyncSession = Depends(get_db)):
            item = await self.repository.get(db, id)
            if not item:
                raise HTTPException(status_code=404, detail=f"{self.model_class.__name__} not found")
            return await self.repository.remove(db, id=id)

# Main router that aggregates all CRUD routers
crud_router = APIRouter(prefix="/crud")

users_crud = CRUDRouter(User, user_repository, UserCreate, UserUpdate, "/users", ["CRUD - Users"])
aq_crud = CRUDRouter(AirQualityData, air_quality_data_repository, AirQualityDataCreate, AirQualityDataUpdate, "/air-quality", ["CRUD - Air Quality Data"])
satellite_crud = CRUDRouter(SatelliteData, satellite_data_repository, SatelliteDataCreate, SatelliteDataUpdate, "/satellite", ["CRUD - Satellite Data"])
weather_crud = CRUDRouter(WeatherData, weather_data_repository, WeatherDataCreate, WeatherDataUpdate, "/weather", ["CRUD - Weather Data"])
fire_crud = CRUDRouter(FireData, fire_data_repository, FireDataCreate, FireDataUpdate, "/fire-data", ["CRUD - Fire Data"])
hcho_crud = CRUDRouter(HCHOHotspot, hcho_hotspot_repository, HCHOHotspotCreate, HCHOHotspotUpdate, "/hcho-hotspots", ["CRUD - HCHO Hotspots"])
prediction_crud = CRUDRouter(Prediction, prediction_repository, PredictionCreate, PredictionUpdate, "/predictions", ["CRUD - Predictions"])

crud_router.include_router(users_crud.router)
crud_router.include_router(aq_crud.router)
crud_router.include_router(satellite_crud.router)
crud_router.include_router(weather_crud.router)
crud_router.include_router(fire_crud.router)
crud_router.include_router(hcho_crud.router)
crud_router.include_router(prediction_crud.router)
