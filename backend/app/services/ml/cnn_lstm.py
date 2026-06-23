"""CNN-LSTM architecture placeholder for future spatiotemporal AQI prediction.

This module defines the planned deep learning pipeline for processing
Sentinel-5P satellite image sequences combined with ERA5 weather data.

Upgrade path:
1. Collect time-series satellite tiles (NO2, SO2, HCHO) over India
2. Build 3D tensor input: (timesteps, lat, lon, channels)
3. CNN layers extract spatial features from each timestep
4. LSTM layers capture temporal pollution dynamics
5. Dense head outputs PM2.5 / AQI predictions

Usage (future):
    from app.services.ml.cnn_lstm import CNNLSTMPredictor
    model = CNNLSTMPredictor()
    model.train(satellite_sequences, ground_truth_pm25)
"""

ARCHITECTURE = {
    "input_shape": (24, 64, 64, 5),
    "channels": ["NO2", "SO2", "CO", "O3", "HCHO"],
    "cnn_filters": [32, 64, 128],
    "lstm_units": [128, 64],
    "output": "pm25_regression",
}


class CNNLSTMPredictor:
    """Placeholder for CNN-LSTM model — integrate TensorFlow/PyTorch when satellite tile pipeline is ready."""

    def __init__(self):
        self.architecture = ARCHITECTURE
        self.model = None

    def build_model(self):
        raise NotImplementedError(
            "CNN-LSTM training requires satellite tile sequences. "
            "Use XGBoost predictor for current production predictions."
        )

    def train(self, *args, **kwargs):
        raise NotImplementedError("CNN-LSTM training not yet implemented")

    def predict(self, *args, **kwargs):
        raise NotImplementedError("CNN-LSTM inference not yet implemented")
