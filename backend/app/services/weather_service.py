import csv
import io
import json
from datetime import datetime
from typing import Any
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WeatherData
from app.repositories.weather import weather_data_repository

class WeatherService:
    async def ingest_weather_file(self, db: AsyncSession, file: UploadFile) -> dict[str, Any]:
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

            await weather_data_repository.create(
                db,
                obj_in={
                    "timestamp": ts,
                    "latitude": lat,
                    "longitude": lon,
                    "temperature": safe_float(row.get("temperature")),
                    "humidity": safe_float(row.get("humidity")),
                    "wind_speed": safe_float(row.get("wind_speed")),
                    "wind_direction": safe_float(row.get("wind_direction")),
                    "pressure": safe_float(row.get("pressure")),
                    "source": row.get("source") or "ERA5",
                }
            )
            records_added += 1

        return {"status": "success", "records_ingested": records_added}

weather_service = WeatherService()
