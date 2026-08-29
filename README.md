# ⚡ FlashGuard — AI Mountain Flash Flood Early Warning System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Backend-Flask%203.1-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML%20Model-Random%20Forest-orange.svg?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Leaflet](https://img.shields.io/badge/GIS%20Mapping-Leaflet.js-green.svg?logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![Open-Meteo](https://img.shields.io/badge/Live%20Telemetry-Open--Meteo%20API-teal.svg)](https://open-meteo.com/)
[![Status](https://img.shields.io/badge/Status-Hackathon%20MVP-brightgreen.svg)]()

> **FlashGuard** is an intelligent, real-time Early Warning System (EWS) designed to predict mountain flash floods and cloudburst hazards across 10 vulnerable Himalayan and Western Ghats catchments in **under 5 milliseconds**.

---

## 🌊 The Problem
Flash floods and cloudbursts in mountainous river basins strike within **15 to 30 minutes** of intense localized rainfall. Traditional 24-hour regional weather forecasts fail to anticipate valley-specific flash surges, leaving downstream populations with near-zero lead time.

## 🛡️ The Solution
FlashGuard fuses real-time environmental telemetry (**Rainfall**, **Multi-Depth Soil Saturation**, **DEM Terrain Slope**, and **River Basin Runoff**) into a trained **Random Forest Machine Learning model** to continuously evaluate flash flood risk, display interactive GIS threat perimeters, and sound emergency evacuation sirens.

---

## 🌟 Key Features

* 🏔️ **10 Hilly Regions of India:** Real-time monitoring for Kullu & Manali, Kedarnath, Chamoli, Wayanad, Kinnaur, Munnar, Chiplun, Teesta Valley, Dharamsala, and Dima Hasao.
* 📡 **Live Environmental Telemetry:** Ingests live hourly precipitation, multi-layer volumetric soil moisture (0-1cm, 1-3cm, 3-9cm), and river discharge directly from Open-Meteo REST & Global Flood APIs.
* 🧠 **Calibrated Random Forest AI Model:** Trained on 15,000 hydro-geological records to detect non-linear compound hazards (Slope + Saturated Soil + Sudden Torrential Rain).
* 🗺️ **Geospatial Watershed GIS:** Built on Leaflet.js with OpenStreetMap to render dynamic catchment threat radiuses:
  * 🔴 **High Alert Danger Zones:** Identifies narrow river gorges, low-lying bridges, and flood-prone riverbanks.
  * 🟢 **Safety Zones:** Designated high-ground evacuation shelters, elevated stadiums, and ridge camps.
* 🔊 **Resilient Dual-Mode Emergency Siren:** High-priority auditory warning featuring local MP3 playback backed by an offline-capable Web Audio API acoustic synthesizer (320 Hz to 820 Hz sweeps).
* 🎛️ **4-Source Manual Calibration Sliders:** Interactive stress-testing simulator allowing disaster managers to test hypothetical cloudburst scenarios (0-150 mm/hr).
* 📜 **Historical Disaster Benchmarks:** Cross-references current telemetry against recorded catastrophe benchmarks (e.g. July 2023 Beas surge, 2021 Chiplun deluge, 2024 Wayanad debris flow).

---

## 🏗️ Project Architecture

`
flashGuard/
│
├── app.py                         # Flask REST API Controller & Real-Time Open-Meteo Ingestion
├── model.py                       # FloodPredictor ML Inference Wrapper
├── train_model.py                 # 15,000 Sample Hydro-Geological Training Script
├── requirements.txt               # Project Dependencies
├── README.md                      # Documentation
│
├── model/
│   └── flood_model.joblib         # Trained Random Forest Model
│
├── static/
│   ├── app.js                     # Client Engine: Leaflet Map, Web Audio Synthesizer, Live Sync
│   ├── style.css                  # UI Design System: High-Contrast Glassmorphic Presentation Theme
│   ├── siren.mp3                  # Emergency Audio Alert File
│   └── FlashGuard_Hackathon_Slides_HighUI.pptx # Presentation Slides
│
└── templates/
    └── index.html                 # Single-Page Command Dashboard
`

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
`ash
git clone https://github.com/k3kriplani-coder/flashGuard.git
cd flashGuard
`

### 2. Create and Activate Virtual Environment
`ash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
`

### 3. Install Dependencies
`ash
pip install -r requirements.txt
`

### 4. (Optional) Retrain the Machine Learning Model
`ash
python train_model.py
`

### 5. Launch FlashGuard Dashboard
`ash
python app.py
`

Open your browser and navigate to: **http://localhost:5000**

---

## 📊 Threat Classification Matrix

| Risk Level | Score Range | Color Code | Action Required |
| :--- | :---: | :---: | :--- |
| **LOW** | 0 - 29 | #52b788 | Normal absorption capacity; routine watershed monitoring. |
| **MODERATE** | 30 - 54 | #e59840 | Saturated valley soil; riverbanks on standby vigil. |
| **HIGH** | 55 - 74 | #c25e40 | Rapid mountain slope runoff; low gorges alerted. |
| **EXTREME** | 75 - 100 | #e06846 | Cloudburst surge wave imminent; automated siren & evacuation. |

---

## 👥 Authors & Acknowledgments
* Built for **Smart India Hackathon (SIH)** — Disaster Management & AI Safety Track.
* Meteorological data provided by [Open-Meteo](https://open-meteo.com/).
* Cartography & Tiles powered by [OpenStreetMap](https://www.openstreetmap.org/).
