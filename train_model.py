import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "flood_model.joblib")
os.makedirs(MODEL_DIR, exist_ok=True)

np.random.seed(42)
N = 15000

# ---------------------------------------------------------
# Realistic Multisource Environmental Distribution
# ---------------------------------------------------------
rain_1h = np.random.exponential(scale=25, size=N)        # Most rain is 0-40mm, rare cloudbursts up to 150mm
rain_1h = np.clip(rain_1h, 0, 160)

rain_6h = rain_1h * np.random.uniform(1.8, 3.5, N) + np.random.uniform(0, 30, N)
rain_6h = np.clip(rain_6h, 0, 350)

soil_moisture = np.random.uniform(15, 98, N)
slope = np.random.uniform(2, 55, N)
elevation = np.random.uniform(50, 3500, N)
river_level = np.random.uniform(10, 98, N)
temperature = np.random.uniform(5, 38, N)
satellite_anomaly = np.random.uniform(5, 98, N)

# ---------------------------------------------------------
# Calibrated Hydrological Risk Formulation
# ---------------------------------------------------------
# Non-linear surge occurs when rain is high AND soil is saturated
effective_runoff = (rain_1h / 70.0) * (soil_moisture / 80.0) ** 1.5
slope_factor = (slope / 40.0) ** 1.2
river_factor = (river_level / 80.0) ** 1.4

hydrological_index = (
    0.42 * np.clip(effective_runoff, 0, 1.5)
    + 0.22 * np.clip(river_factor, 0, 1.2)
    + 0.18 * np.clip(slope_factor, 0, 1.2)
    + 0.10 * (satellite_anomaly / 100.0)
    + 0.08 * (rain_6h / 250.0)
)

# Realistic class assignment
labels = []
for idx in range(N):
    r1 = rain_1h[idx]
    soil = soil_moisture[idx]
    riv = river_level[idx]
    h_idx = hydrological_index[idx]

    # Extreme: Requires intense rain (>70mm) OR massive river surge + saturated soil
    if (r1 > 80 and soil > 75) or (riv > 88 and r1 > 50) or h_idx > 0.85:
        labels.append(3)  # EXTREME
    # High: Elevated storm on steep or saturated catchment
    elif (r1 > 50 and soil > 60) or (riv > 72 and r1 > 35) or h_idx > 0.58:
        labels.append(2)  # HIGH
    # Moderate: Steady rain with moderate soil moisture
    elif r1 > 25 or riv > 55 or soil > 75 or h_idx > 0.32:
        labels.append(1)  # MODERATE
    # Low: Normal, dry, or light rain
    else:
        labels.append(0)  # LOW

y = np.array(labels)

X = pd.DataFrame({
    "rain_1h": rain_1h,
    "rain_6h": rain_6h,
    "soil_moisture": soil_moisture,
    "slope": slope,
    "elevation": elevation,
    "river_level": river_level,
    "temperature": temperature,
    "satellite_anomaly": satellite_anomaly
})

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    min_samples_split=4,
    random_state=42
)
model.fit(X_train, y_train)

preds = model.predict(X_test)
print(f"✅ Calibrated Model Accuracy: {accuracy_score(y_test, preds) * 100:.2f}%")
print(classification_report(y_test, preds, target_names=["LOW", "MODERATE", "HIGH", "EXTREME"]))

joblib.dump(model, MODEL_PATH)
print(f"✅ Saved calibrated model to {MODEL_PATH}")