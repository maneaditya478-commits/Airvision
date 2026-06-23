"""Pollution transport path estimation using wind vectors."""

import math


class TransportAnalyzer:
    def generate_wind_grid(self, bounds: dict, resolution: float = 2.0) -> list[dict]:
        vectors = []
        lat = bounds["min_lat"]
        while lat <= bounds["max_lat"]:
            lon = bounds["min_lon"]
            while lon <= bounds["max_lon"]:
                speed = 3.0 + 2.0 * math.sin(math.radians(lat)) * math.cos(math.radians(lon * 0.5))
                direction = (270 + lat * 2 + lon) % 360
                rad = math.radians(direction)
                vectors.append({
                    "latitude": round(lat, 2),
                    "longitude": round(lon, 2),
                    "u_component": round(speed * math.sin(rad), 3),
                    "v_component": round(speed * math.cos(rad), 3),
                    "speed": round(speed, 2),
                    "direction": round(direction, 1),
                })
                lon += resolution
            lat += resolution
        return vectors

    def estimate_transport_path(
        self, origin_lat: float, origin_lon: float,
        u: float, v: float, hours: float = 24, step_hours: float = 1.0,
    ) -> dict:
        path = [{"lat": origin_lat, "lon": origin_lon, "hour": 0}]
        lat, lon = origin_lat, origin_lon
        km_per_deg_lat = 111.0

        for step in range(1, int(hours / step_hours) + 1):
            dlat = (v * step_hours * 3.6) / km_per_deg_lat
            dlon = (u * step_hours * 3.6) / (km_per_deg_lat * math.cos(math.radians(lat)))
            lat += dlat
            lon += dlon
            path.append({"lat": round(lat, 4), "lon": round(lon, 4), "hour": step * step_hours})

        return {
            "origin_lat": origin_lat,
            "origin_lon": origin_lon,
            "path": path,
            "estimated_hours": hours,
        }


transport_analyzer = TransportAnalyzer()
