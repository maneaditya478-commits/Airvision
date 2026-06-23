"""National Air Quality Index calculation per CPCB standards."""

from enum import Enum


class AQICategory(str, Enum):
    GOOD = "Good"
    SATISFACTORY = "Satisfactory"
    MODERATE = "Moderate"
    POOR = "Poor"
    VERY_POOR = "Very Poor"
    SEVERE = "Severe"


# CPCB sub-index breakpoints: (concentration_low, concentration_high, aqi_low, aqi_high)
BREAKPOINTS = {
    "pm25": [(0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200), (91, 120, 201, 300), (121, 250, 301, 400), (251, 500, 401, 500)],
    "pm10": [(0, 50, 0, 50), (51, 100, 51, 100), (101, 250, 101, 200), (251, 350, 201, 300), (351, 430, 301, 400), (431, 600, 401, 500)],
    "no2": [(0, 40, 0, 50), (41, 80, 51, 100), (81, 180, 101, 200), (181, 280, 201, 300), (281, 400, 301, 400), (401, 600, 401, 500)],
    "so2": [(0, 40, 0, 50), (41, 80, 51, 100), (81, 380, 101, 200), (381, 800, 201, 300), (801, 1600, 301, 400), (1601, 2100, 401, 500)],
    "co": [(0, 1.0, 0, 50), (1.1, 2.0, 51, 100), (2.1, 10, 101, 200), (10.1, 17, 201, 300), (17.1, 34, 301, 400), (34.1, 60, 401, 500)],
    "o3": [(0, 50, 0, 50), (51, 100, 51, 100), (101, 168, 101, 200), (169, 208, 201, 300), (209, 748, 301, 400), (749, 940, 401, 500)],
    "nh3": [(0, 200, 0, 50), (201, 400, 51, 100), (401, 800, 101, 200), (801, 1200, 201, 300), (1201, 1800, 301, 400), (1801, 2400, 401, 500)],
}


def calculate_sub_index(pollutant: str, concentration: float) -> float:
    pollutant = pollutant.lower()
    if pollutant not in BREAKPOINTS:
        return 0.0
    for c_low, c_high, aqi_low, aqi_high in BREAKPOINTS[pollutant]:
        if c_low <= concentration <= c_high:
            return ((aqi_high - aqi_low) / (c_high - c_low)) * (concentration - c_low) + aqi_low
    return 500.0


def get_aqi_category(aqi: float) -> AQICategory:
    if aqi <= 50:
        return AQICategory.GOOD
    if aqi <= 100:
        return AQICategory.SATISFACTORY
    if aqi <= 200:
        return AQICategory.MODERATE
    if aqi <= 300:
        return AQICategory.POOR
    if aqi <= 400:
        return AQICategory.VERY_POOR
    return AQICategory.SEVERE


def calculate_aqi(pollutants: dict[str, float | None]) -> tuple[float, AQICategory, str]:
    sub_indices: dict[str, float] = {}
    for pollutant, value in pollutants.items():
        if value is not None and pollutant.lower() in BREAKPOINTS:
            sub_indices[pollutant.lower()] = calculate_sub_index(pollutant.lower(), value)

    if not sub_indices:
        return 0.0, AQICategory.GOOD, "pm25"

    dominant = max(sub_indices, key=sub_indices.get)
    aqi = sub_indices[dominant]
    return round(aqi, 1), get_aqi_category(aqi), dominant


def get_category_color(category: str) -> str:
    colors = {
        "Good": "#00E400",
        "Satisfactory": "#92D050",
        "Moderate": "#FFFF00",
        "Poor": "#FF7E00",
        "Very Poor": "#FF0000",
        "Severe": "#7E0023",
    }
    return colors.get(category, "#808080")
