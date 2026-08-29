import os
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = os.path.join("model", "flood_model.joblib")

class FloodPredictor:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("ML model not found. Run train_model.py first.")

        self.model = joblib.load(MODEL_PATH)
        self.features = [
            "rain_1h", "rain_6h", "soil_moisture", "slope",
            "elevation", "river_level", "temperature", "satellite_anomaly"
        ]
        self.classes = ["LOW", "MODERATE", "HIGH", "EXTREME"]
        self.colors = ["#22c55e", "#facc15", "#fb923c", "#ef4444"]

    def predict(self, data):
        values = {feat: float(data.get(feat, 0.0)) for feat in self.features}
        df = pd.DataFrame([values])

        probabilities = self.model.predict_proba(df)[0]
        pred_class = int(self.model.predict(df)[0])

        # Smooth continuous risk score (0-100)
        continuous_score = (
            probabilities[0] * 12.0
            + probabilities[1] * 40.0
            + probabilities[2] * 68.0
            + probabilities[3] * 96.0
        )
        risk_score = int(np.clip(round(continuous_score), 0, 100))

        # Determine risk label & color based on score thresholds
        if risk_score < 30:
            risk = "LOW"
            color = "#22c55e"
        elif risk_score < 55:
            risk = "MODERATE"
            color = "#facc15"
        elif risk_score < 75:
            risk = "HIGH"
            color = "#fb923c"
        else:
            risk = "EXTREME"
            color = "#ef4444"

        return {
            "risk_score": risk_score,
            "risk": risk,
            "color": color,
            "class": pred_class,
            "class_probabilities": {
                "LOW": round(probabilities[0] * 100, 1),
                "MODERATE": round(probabilities[1] * 100, 1),
                "HIGH": round(probabilities[2] * 100, 1),
                "EXTREME": round(probabilities[3] * 100, 1)
            }
        }