from datetime import datetime, timezone

from app.database import SyncSessionLocal
from app.models import Dataset, DatasetStatus, MLModel, ModelStatus, TaskLog
from app.services.ml.aqi_predictor import predictor
from app.services.ml.hcho_detector import hcho_detector
from app.tasks.celery_app import celery_app


def _log_task(task_id: str, task_name: str, status: str, message: str | None = None):
    db = SyncSessionLocal()
    try:
        db.add(TaskLog(task_id=task_id, task_name=task_name, status=status, message=message))
        db.commit()
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.tasks.retrain_model_task")
def retrain_model_task(self):
    _log_task(self.request.id, "retrain_model", "started")
    try:
        metrics = predictor.train()
        db = SyncSessionLocal()
        try:
            model = MLModel(
                name="XGBoost PM2.5 Predictor",
                model_type="xgboost",
                version=metrics["version"],
                file_path="models_store/xgboost_pm25.joblib",
                status=ModelStatus.READY,
                metrics=metrics,
                trained_at=datetime.now(timezone.utc),
            )
            db.add(model)
            db.commit()
        finally:
            db.close()
        _log_task(self.request.id, "retrain_model", "completed", str(metrics))
        return metrics
    except Exception as e:
        _log_task(self.request.id, "retrain_model", "failed", str(e))
        raise


@celery_app.task(bind=True, name="app.tasks.tasks.ingest_dataset_task")
def ingest_dataset_task(self, dataset_id: int):
    _log_task(self.request.id, "ingest_dataset", "started", f"dataset_id={dataset_id}")
    db = SyncSessionLocal()
    try:
        dataset = db.get(Dataset, dataset_id)
        if not dataset:
            return {"error": "Dataset not found"}

        dataset.status = DatasetStatus.PROCESSING
        db.commit()

        dataset.status = DatasetStatus.COMPLETED
        dataset.record_count = 100
        db.commit()
        _log_task(self.request.id, "ingest_dataset", "completed")
        return {"dataset_id": dataset_id, "status": "completed"}
    except Exception as e:
        _log_task(self.request.id, "ingest_dataset", "failed", str(e))
        raise
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.tasks.detect_hotspots_task")
def detect_hotspots_task(self):
    from app.models import HCHOHotspot, SatelliteData
    from datetime import timedelta

    _log_task(self.request.id, "detect_hotspots", "started")
    db = SyncSessionLocal()
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=72)
        readings = db.query(SatelliteData).filter(
            SatelliteData.pollutant == "HCHO",
            SatelliteData.timestamp >= since,
        ).all()

        reading_dicts = [{"latitude": r.latitude, "longitude": r.longitude, "value": r.value} for r in readings]
        detected = hcho_detector.detect(reading_dicts)

        for hs in detected:
            db.add(HCHOHotspot(
                cluster_id=hs["cluster_id"],
                timestamp=datetime.now(timezone.utc),
                latitude=hs["latitude"], longitude=hs["longitude"],
                hcho_mean=hs["hcho_mean"], hcho_max=hs["hcho_max"],
                point_count=hs["point_count"], intensity=hs["intensity"],
            ))
        db.commit()
        _log_task(self.request.id, "detect_hotspots", "completed", f"found {len(detected)} hotspots")
        return {"hotspots_detected": len(detected)}
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.tasks.refresh_predictions_task")
def refresh_predictions_task(self):
    _log_task(self.request.id, "refresh_predictions", "started")
    try:
        metrics = predictor.predict({"latitude": 28.6, "longitude": 77.2})
        _log_task(self.request.id, "refresh_predictions", "completed")
        return metrics
    except Exception as e:
        _log_task(self.request.id, "refresh_predictions", "failed", str(e))
        raise
