import csv
import io
import json
from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import FireData, SatelliteData
from app.repositories.fire import fire_data_repository
from app.repositories.satellite import satellite_data_repository
from app.services.ml.fire_correlation import fire_correlation_service

class FireService:
    async def ingest_fire_file(self, db: AsyncSession, file: UploadFile) -> dict[str, Any]:
        content = await file.read()
        records_added = 0
        
        filename = file.filename or ""
        if filename.endswith(".json"):
            data = json.loads(content.decode("utf-8"))
            if not isinstance(data, list):
                data = [data]
        else:
            f = io.StringIO(content.decode("utf-8"))
            reader = csv.DictReader(f)
            data = list(reader)

        for row in data:
            ts_str = row.get("timestamp")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except ValueError:
                    ts = datetime.now()
            else:
                ts = datetime.now()

            lat = float(row.get("latitude") or 0)
            lon = float(row.get("longitude") or 0)

            def safe_float(val: Any) -> float | None:
                if val is None or str(val).strip() == "" or str(val).lower() == "nan":
                    return None
                try:
                    return float(val)
                except ValueError:
                    return None

            await fire_data_repository.create(
                db,
                obj_in={
                    "timestamp": ts,
                    "latitude": lat,
                    "longitude": lon,
                    "brightness": safe_float(row.get("brightness")),
                    "confidence": safe_float(row.get("confidence")),
                    "frp": safe_float(row.get("frp")),
                    "source": row.get("source") or "NASA FIRMS",
                }
            )
            records_added += 1

        return {"status": "success", "records_ingested": records_added}

    async def get_correlation(self, db: AsyncSession, hours: int = 72) -> dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Get fire points
        fires = await fire_data_repository.get_by_time_range(db, since=since)
        fire_list = [
            {"latitude": f.latitude, "longitude": f.longitude, "frp": f.frp}
            for f in fires
        ]

        # Get HCHO satellite data
        hcho = await satellite_data_repository.get_by_pollutant_and_time(db, pollutant="HCHO", since=since)
        hcho_list = [
            {"latitude": r.latitude, "longitude": r.longitude, "value": r.value}
            for r in hcho
        ]

        # Correlate
        return fire_correlation_service.correlate(fire_list, hcho_list)

fire_service = FireService()
