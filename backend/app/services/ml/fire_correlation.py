"""Fire-HCHO correlation analysis."""

import math

import numpy as np


class FireCorrelationService:
    FIRE_RADIUS_KM = 50.0

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def correlate(self, fire_points: list[dict], hcho_readings: list[dict]) -> dict:
        if not fire_points or not hcho_readings:
            return {
                "fire_count": len(fire_points),
                "avg_hcho_near_fires": 0.0,
                "avg_hcho_away_from_fires": 0.0,
                "correlation_coefficient": 0.0,
                "hotspots_near_fires": 0,
            }

        near_hcho = []
        away_hcho = []

        for reading in hcho_readings:
            min_dist = min(
                self.haversine(reading["latitude"], reading["longitude"], f["latitude"], f["longitude"])
                for f in fire_points
            )
            if min_dist <= self.FIRE_RADIUS_KM:
                near_hcho.append(reading["value"])
            else:
                away_hcho.append(reading["value"])

        fire_frp = [f.get("frp", 1.0) or 1.0 for f in fire_points]
        hcho_near_fire = []
        for fire in fire_points:
            nearby = [
                r["value"] for r in hcho_readings
                if self.haversine(fire["latitude"], fire["longitude"], r["latitude"], r["longitude"]) <= self.FIRE_RADIUS_KM
            ]
            hcho_near_fire.append(np.mean(nearby) if nearby else 0)

        corr = 0.0
        if len(fire_frp) > 1 and len(hcho_near_fire) > 1:
            corr = float(np.corrcoef(fire_frp, hcho_near_fire)[0, 1])
            if np.isnan(corr):
                corr = 0.0

        return {
            "fire_count": len(fire_points),
            "avg_hcho_near_fires": round(float(np.mean(near_hcho)), 4) if near_hcho else 0.0,
            "avg_hcho_away_from_fires": round(float(np.mean(away_hcho)), 4) if away_hcho else 0.0,
            "correlation_coefficient": round(corr, 4),
            "hotspots_near_fires": sum(1 for v in hcho_near_fire if v > 2.0),
        }


fire_correlation_service = FireCorrelationService()
