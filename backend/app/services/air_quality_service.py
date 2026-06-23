import csv
import io
import json
from datetime import datetime
from typing import Any
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AirQualityData, AirQualityStation
from app.repositories.air_quality import air_quality_data_repository, air_quality_station_repository
from app.utils.aqi import calculate_aqi, AQICategory

class AirQualityService:
    async def get_current_aqi(self, db: AsyncSession) -> list[dict[str, Any]]:
        readings = await air_quality_data_repository.get_latest_readings_all_stations(db)
        return [
            {
                "station_id": r.station_id,
                "station_name": s.name,
                "city": s.city,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "timestamp": r.timestamp.isoformat(),
                "pm25": r.pm25,
                "pm10": r.pm10,
                "no2": r.no2,
                "so2": r.so2,
                "co": r.co,
                "o3": r.o3,
                "aqi": r.aqi,
                "aqi_category": r.aqi_category.value if r.aqi_category else None,
            }
            for r, s in readings
        ]

    async def ingest_cpcb_file(self, db: AsyncSession, file: UploadFile) -> dict[str, Any]:
        content = await file.read()
        records_added = 0
        
        # Determine format (CSV or JSON)
        filename = file.filename or ""
        if filename.endswith(".json"):
            data = json.loads(content.decode("utf-8"))
            if not isinstance(data, list):
                data = [data]
        else:
            # Assume CSV
            f = io.StringIO(content.decode("utf-8"))
            reader = csv.DictReader(f)
            data = list(reader)

        for row in data:
            station_id_str = row.get("station_id") or "CPCB_DELHI"
            # Get or create station
            station = await air_quality_station_repository.get_by_station_id(db, station_id_str)
            if not station:
                # Create a default station for this station_id
                station = await air_quality_station_repository.create(
                    db,
                    obj_in={
                        "station_id": station_id_str,
                        "name": row.get("station_name") or f"Station {station_id_str}",
                        "city": row.get("city") or "Unknown",
                        "state": row.get("state") or "Unknown",
                        "latitude": float(row.get("latitude") or 28.6139),
                        "longitude": float(row.get("longitude") or 77.2090),
                    }
                )
            
            # Parse timestamp
            ts_str = row.get("timestamp")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except ValueError:
                    ts = datetime.now()
            else:
                ts = datetime.now()

            # Parse pollutants
            def safe_float(val: Any) -> float | None:
                if val is None or str(val).strip() == "" or str(val).lower() == "nan":
                    return None
                try:
                    return float(val)
                except ValueError:
                    return None

            pm25 = safe_float(row.get("pm25"))
            pm10 = safe_float(row.get("pm10"))
            no2 = safe_float(row.get("no2"))
            so2 = safe_float(row.get("so2"))
            co = safe_float(row.get("co"))
            o3 = safe_float(row.get("o3"))
            nh3 = safe_float(row.get("nh3"))

            # Calculate AQI
            aqi, cat, _ = calculate_aqi({
                "pm25": pm25, "pm10": pm10, "no2": no2, "so2": so2, "co": co, "o3": o3, "nh3": nh3
            })

            # Create reading
            await air_quality_data_repository.create(
                db,
                obj_in={
                    "station_id": station.id,
                    "timestamp": ts,
                    "pm25": pm25,
                    "pm10": pm10,
                    "no2": no2,
                    "so2": so2,
                    "co": co,
                    "o3": o3,
                    "nh3": nh3,
                    "aqi": aqi,
                    "aqi_category": AQICategory(cat.value) if cat else None,
                }
            )
            records_added += 1

        return {"status": "success", "records_ingested": records_added}

air_quality_service = AirQualityService()
