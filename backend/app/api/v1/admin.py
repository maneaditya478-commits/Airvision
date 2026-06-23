from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_admin, get_current_analyst
from app.database import get_db
from app.models import Dataset, DatasetStatus, MLModel, ModelStatus, TaskLog, User
from app.schemas import DatasetCreate, DatasetResponse, ModelResponse, TaskStatusResponse
from app.tasks.tasks import retrain_model_task, ingest_dataset_task

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/datasets", response_model=list[DatasetResponse])
async def list_datasets(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_analyst),
):
    result = await db.execute(select(Dataset).order_by(Dataset.created_at.desc()))
    return result.scalars().all()


@router.post("/datasets", response_model=DatasetResponse, status_code=201)
async def create_dataset(
    dataset: DatasetCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_analyst),
):
    record = Dataset(
        name=dataset.name, source=dataset.source,
        metadata_json=dataset.metadata_json,
        uploaded_by=user.id, status=DatasetStatus.PENDING,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.post("/datasets/{dataset_id}/ingest")
async def ingest_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    dataset = await db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    task = ingest_dataset_task.delay(dataset_id)
    return {"task_id": task.id, "status": "queued"}


@router.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_analyst),
):
    dataset = Dataset(
        name=file.filename or "uploaded_dataset",
        source="upload",
        file_path=f"data/{file.filename}",
        uploaded_by=user.id,
        status=DatasetStatus.PENDING,
    )
    db.add(dataset)
    await db.flush()
    return {"dataset_id": dataset.id, "filename": file.filename, "status": "pending"}


@router.get("/models", response_model=list[ModelResponse])
async def list_models(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_analyst),
):
    result = await db.execute(select(MLModel).order_by(MLModel.created_at.desc()))
    return result.scalars().all()


@router.post("/models/retrain")
async def retrain_model(_: User = Depends(get_current_admin)):
    task = retrain_model_task.delay()
    return {"task_id": task.id, "status": "training_started"}


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    from app.tasks.celery_app import celery_app
    result = celery_app.AsyncResult(task_id)
    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,
        result=result.result if result.ready() else None,
    )


@router.get("/monitoring/logs")
async def get_task_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(
        select(TaskLog).order_by(TaskLog.created_at.desc()).limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": log.id, "task_id": log.task_id, "task_name": log.task_name,
            "status": log.status, "message": log.message,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    from app.models import AirQualityStation, AirQualityData, FireData, SatelliteData
    from sqlalchemy import func

    return {
        "stations": await db.scalar(select(func.count(AirQualityStation.id))),
        "readings": await db.scalar(select(func.count(AirQualityData.id))),
        "satellite_records": await db.scalar(select(func.count(SatelliteData.id))),
        "fire_points": await db.scalar(select(func.count(FireData.id))),
        "datasets": await db.scalar(select(func.count(Dataset.id))),
        "models": await db.scalar(select(func.count(MLModel.id))),
    }
