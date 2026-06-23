"""DBSCAN-based HCHO hotspot detection."""

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


class HCHODetector:
    EPS = 0.5
    MIN_SAMPLES = 5
    INTENSITY_THRESHOLDS = {"low": 1.5, "medium": 2.5, "high": 4.0}

    def detect(self, readings: list[dict]) -> list[dict]:
        if len(readings) < self.MIN_SAMPLES:
            return []

        df = pd.DataFrame(readings)
        coords = df[["latitude", "longitude"]].values
        values = df["value"].values.reshape(-1, 1)

        scaler = StandardScaler()
        scaled_coords = scaler.fit_transform(coords)
        scaled_values = StandardScaler().fit_transform(values)
        features = np.hstack([scaled_coords, scaled_values * 0.5])

        clustering = DBSCAN(eps=self.EPS, min_samples=self.MIN_SAMPLES).fit(features)
        df["cluster"] = clustering.labels_

        hotspots = []
        for cluster_id in set(clustering.labels_):
            if cluster_id == -1:
                continue
            cluster_data = df[df["cluster"] == cluster_id]
            hcho_mean = float(cluster_data["value"].mean())
            hcho_max = float(cluster_data["value"].max())

            hotspots.append({
                "cluster_id": int(cluster_id),
                "latitude": float(cluster_data["latitude"].mean()),
                "longitude": float(cluster_data["longitude"].mean()),
                "hcho_mean": round(hcho_mean, 4),
                "hcho_max": round(hcho_max, 4),
                "point_count": len(cluster_data),
                "intensity": self._classify_intensity(hcho_mean),
            })

        return sorted(hotspots, key=lambda x: x["hcho_mean"], reverse=True)

    def _classify_intensity(self, hcho_mean: float) -> str:
        if hcho_mean >= self.INTENSITY_THRESHOLDS["high"]:
            return "high"
        if hcho_mean >= self.INTENSITY_THRESHOLDS["medium"]:
            return "medium"
        return "low"

    def temporal_analysis(self, hotspots_by_date: dict[str, list[dict]]) -> dict:
        timeline = []
        for date, hotspots in sorted(hotspots_by_date.items()):
            timeline.append({
                "date": date,
                "hotspot_count": len(hotspots),
                "avg_intensity": round(np.mean([h["hcho_mean"] for h in hotspots]), 4) if hotspots else 0,
                "max_intensity": round(max((h["hcho_mean"] for h in hotspots), default=0), 4),
            })
        return {"timeline": timeline, "total_days": len(timeline)}


hcho_detector = HCHODetector()
