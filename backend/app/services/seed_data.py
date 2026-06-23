"""Seed sample data for development and demo."""

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import (
    AirQualityData,
    AirQualityStation,
    AQICategory,
    FireData,
    SatelliteData,
    User,
    UserRole,
    WeatherData,
)
from app.core.security import get_password_hash
from app.utils.aqi import calculate_aqi

INDIAN_CITIES = [
    ("Delhi", "Delhi", 28.6139, 77.2090),
    ("Mumbai", "Maharashtra", 19.0760, 72.8777),
    ("Kolkata", "West Bengal", 22.5726, 88.3639),
    ("Chennai", "Tamil Nadu", 13.0827, 80.2707),
    ("Bangalore", "Karnataka", 12.9716, 77.5946),
    ("Hyderabad", "Telangana", 17.3850, 78.4867),
    ("Ahmedabad", "Gujarat", 23.0225, 72.5714),
    ("Pune", "Maharashtra", 18.5204, 73.8567),
    ("Jaipur", "Rajasthan", 26.9124, 75.7873),
    ("Lucknow", "Uttar Pradesh", 26.8467, 80.9462),
    ("Patna", "Bihar", 25.5941, 85.1376),
    ("Chandigarh", "Chandigarh", 30.7333, 76.7794),
]


def seed_database(db: Session) -> dict:
    counts = {"users": 0, "stations": 0, "readings": 0, "satellite": 0, "weather": 0, "fires": 0}

    if not db.query(User).filter(User.email == "admin@airvision.in").first():
        db.add(User(
            email="admin@airvision.in",
            hashed_password=get_password_hash("admin123"),
            full_name="System Admin",
            role=UserRole.ADMIN,
        ))
        db.add(User(
            email="analyst@airvision.in",
            hashed_password=get_password_hash("analyst123"),
            full_name="Data Analyst",
            role=UserRole.ANALYST,
        ))
        counts["users"] = 2

    if db.query(AirQualityStation).count() == 0:
        for i, (city, state, lat, lon) in enumerate(INDIAN_CITIES):
            db.add(AirQualityStation(
                station_id=f"CPCB_{city.upper().replace(' ', '_')}",
                name=f"CPCB Station {city}",
                city=city, state=state, latitude=lat, longitude=lon,
            ))
        db.flush()
        counts["stations"] = len(INDIAN_CITIES)

        now = datetime.now(timezone.utc)
        for station in db.query(AirQualityStation).all():
            for day in range(30):
                for hour in [6, 12, 18]:
                    ts = now - timedelta(days=day, hours=hour)
                    pm25 = random.uniform(20, 250)
                    pm10 = pm25 * random.uniform(1.2, 2.0)
                    no2 = random.uniform(10, 100)
                    so2 = random.uniform(5, 60)
                    co = random.uniform(0.3, 4.0)
                    o3 = random.uniform(20, 150)
                    aqi, cat, _ = calculate_aqi({"pm25": pm25, "pm10": pm10, "no2": no2, "so2": so2, "co": co, "o3": o3})
                    db.add(AirQualityData(
                        station_id=station.id, timestamp=ts,
                        pm25=round(pm25, 2), pm10=round(pm10, 2),
                        no2=round(no2, 2), so2=round(so2, 2),
                        co=round(co, 2), o3=round(o3, 2),
                        aqi=aqi, aqi_category=AQICategory(cat.value),
                    ))
                    counts["readings"] += 1

    if db.query(SatelliteData).count() == 0:
        for _ in range(500):
            lat = random.uniform(8, 35)
            lon = random.uniform(68, 92)
            pollutant = random.choice(["NO2", "SO2", "CO", "O3", "HCHO"])
            base = {"NO2": 50, "SO2": 20, "CO": 1.5, "O3": 60, "HCHO": 2.0}[pollutant]
            db.add(SatelliteData(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 72)),
                latitude=lat, longitude=lon,
                pollutant=pollutant,
                value=round(random.uniform(base * 0.5, base * 3), 4),
            ))
            counts["satellite"] += 1

    if db.query(WeatherData).count() == 0:
        for city, _, lat, lon in INDIAN_CITIES:
            db.add(WeatherData(
                timestamp=datetime.now(timezone.utc),
                latitude=lat, longitude=lon,
                temperature=round(random.uniform(20, 42), 1),
                humidity=round(random.uniform(30, 90), 1),
                wind_speed=round(random.uniform(1, 12), 1),
                wind_direction=round(random.uniform(0, 360), 1),
                pressure=round(random.uniform(990, 1020), 1),
            ))
            counts["weather"] += 1

    if db.query(FireData).count() == 0:
        fire_regions = [(28.6, 77.2), (22.5, 88.3), (13.0, 80.2), (26.9, 75.8), (23.0, 72.5)]
        for _ in range(80):
            region = random.choice(fire_regions)
            db.add(FireData(
                timestamp=datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 48)),
                latitude=region[0] + random.uniform(-1, 1),
                longitude=region[1] + random.uniform(-1, 1),
                brightness=round(random.uniform(300, 400), 1),
                confidence=round(random.uniform(60, 100), 1),
                frp=round(random.uniform(5, 100), 2),
            ))
            counts["fires"] += 1

    db.commit()
    return counts
