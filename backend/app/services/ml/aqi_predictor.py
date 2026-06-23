"""XGBoost-based PM2.5 prediction with SHAP explainability."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from app.config import get_settings
from app.utils.aqi import calculate_aqi

settings = get_settings()

FEATURE_COLUMNS = [
    "no2", "so2", "co", "o3", "temperature", "humidity",
    "wind_speed", "latitude", "longitude", "hour", "month",
]


class AQIPredictor:
    def __init__(self):
        self.models_dir = Path(settings.models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.models_dir / "xgboost_pm25.joblib"
        self.metadata_path = self.models_dir / "model_metadata.json"
        self.model: XGBRegressor | None = None
        self.explainer: shap.TreeExplainer | None = None
        self.version = "1.0.0"
        self._load_model()

    def _load_model(self) -> None:
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            if self.metadata_path.exists():
                with open(self.metadata_path) as f:
                    meta = json.load(f)
                    self.version = meta.get("version", "1.0.0")
            self.explainer = shap.TreeExplainer(self.model)

    def _generate_synthetic_training_data(self, n_samples: int = 5000) -> pd.DataFrame:
        np.random.seed(42)
        data = {
            "no2": np.random.uniform(10, 120, n_samples),
            "so2": np.random.uniform(5, 80, n_samples),
            "co": np.random.uniform(0.2, 5, n_samples),
            "o3": np.random.uniform(20, 180, n_samples),
            "temperature": np.random.uniform(15, 45, n_samples),
            "humidity": np.random.uniform(20, 95, n_samples),
            "wind_speed": np.random.uniform(0.5, 15, n_samples),
            "latitude": np.random.uniform(8, 35, n_samples),
            "longitude": np.random.uniform(72, 92, n_samples),
            "hour": np.random.randint(0, 24, n_samples),
            "month": np.random.randint(1, 13, n_samples),
        }
        df = pd.DataFrame(data)
        df["pm25"] = (
            0.35 * df["no2"] + 0.25 * df["so2"] + 0.15 * df["co"]
            + 0.1 * df["o3"] - 0.05 * df["wind_speed"]
            + 0.02 * df["temperature"] + np.random.normal(0, 5, n_samples)
        ).clip(5, 500)
        return df

    def train(self, df: pd.DataFrame | None = None) -> dict:
        if df is None:
            df = self._generate_synthetic_training_data()

        X = df[FEATURE_COLUMNS]
        y = df["pm25"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
        )
        self.model.fit(X_train, y_train)

        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        y_pred = self.model.predict(X_test)
        rmse = float(np.sqrt(np.mean((y_test - y_pred) ** 2)))

        joblib.dump(self.model, self.model_path)
        self.version = f"1.0.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
        metadata = {"version": self.version, "train_r2": train_score, "test_r2": test_score, "rmse": rmse}
        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f)

        self.explainer = shap.TreeExplainer(self.model)
        return metadata

    def _prepare_features(self, features: dict) -> np.ndarray:
        now = datetime.now(timezone.utc)
        defaults = {
            "no2": 40.0, "so2": 20.0, "co": 1.0, "o3": 50.0,
            "temperature": 28.0, "humidity": 60.0, "wind_speed": 3.0,
            "latitude": 28.6, "longitude": 77.2,
            "hour": now.hour, "month": now.month,
        }
        merged = {**defaults, **{k: v for k, v in features.items() if v is not None}}
        return np.array([[merged[col] for col in FEATURE_COLUMNS]])

    def predict(self, features: dict) -> dict:
        if self.model is None:
            self.train()

        X = self._prepare_features(features)
        pm25 = float(self.model.predict(X)[0])
        pollutants = {"pm25": pm25, "no2": features.get("no2"), "so2": features.get("so2"),
                        "co": features.get("co"), "o3": features.get("o3")}
        aqi, category, dominant = calculate_aqi(pollutants)

        shap_values = None
        if self.explainer:
            sv = self.explainer.shap_values(X)[0]
            shap_values = {col: round(float(val), 4) for col, val in zip(FEATURE_COLUMNS, sv)}

        return {
            "predicted_pm25": round(pm25, 2),
            "predicted_aqi": aqi,
            "aqi_category": category.value,
            "dominant_pollutant": dominant,
            "model_version": self.version,
            "shap_values": shap_values,
        }

    def get_feature_importance(self) -> dict[str, float]:
        if self.model is None:
            self.train()
        importance = self.model.feature_importances_
        return {col: round(float(val), 4) for col, val in zip(FEATURE_COLUMNS, importance)}


predictor = AQIPredictor()
