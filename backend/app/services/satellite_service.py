import csv
import io
import json
from datetime import datetime
from typing import Any
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import SatelliteData
from app.repositories.satellite import satellite_data_repository

class SatelliteService:
    async def ingest_sentinel_file(self, db: AsyncSession, file: UploadFile) -> dict[str, Any]:
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
            pollutant = row.get("pollutant") or "HCHO"
            value = float(row.get("value") or 0.0)
            source = row.get("source") or "Sentinel-5P"
            
            metadata = row.get("metadata_json") or row.get("metadata")
            metadata_dict = None
            if metadata:
                if isinstance(metadata, str):
                    try:
                        metadata_dict = json.loads(metadata)
                    except ValueError:
                        metadata_dict = {"raw": metadata}
                elif isinstance(metadata, dict):
                    metadata_dict = metadata

            await satellite_data_repository.create(
                db,
                obj_in={
                    "timestamp": ts,
                    "latitude": lat,
                    "longitude": lon,
                    "pollutant": pollutant,
                    "value": value,
                    "source": source,
                    "metadata_json": metadata_dict,
                }
            )
            records_added += 1

        return {"status": "success", "records_ingested": records_added}

satellite_service = SatelliteService()
