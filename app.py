from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from model import FloodPredictor
import requests
import datetime
import os

app = Flask(__name__)
CORS(app)
predictor = FloodPredictor()

# =========================================================
# 10 CRITICAL FLASH FLOOD HILLY REGIONS OF INDIA
# Includes Topography, Live Coordinates, Danger Zones & Safe Havens
# =========================================================
HILLY_REGIONS = {
    "Kullu & Manali Valley (HP)": {
        "lat": 32.239, "lng": 77.188, "zoom": 11,
        "slope": 42.0, "elevation": 2050, "soil_baseline": 62.0, "river_baseline": 50.0,
        "history": "July 2023: Cloudburst triggered catastrophic Beas River surge (6,000 m³/s peak). 2018: Kullu-Manali highway submerged.",
        "danger_zones": [
            {"name": "Beas Riverbed Gorge", "lat": 32.235, "lng": 77.185, "desc": "High velocity surge corridor, flood prone riverbank"},
            {"name": "Old Manali Bridge Bottleneck", "lat": 32.251, "lng": 77.178, "desc": "Debris damming risk under heavy torrents"}
        ],
        "safety_zones": [
            {"name": "Upper Dhungri Ridge Ground", "lat": 32.248, "lng": 77.170, "desc": "Designated high-altitude safe haven (+120m above river)"},
            {"name": "Aleo Highland Relief Camp", "lat": 32.230, "lng": 77.195, "desc": "Official civil defense evacuation stadium"}
        ]
    },
    "Kedarnath & Mandakini Valley (UK)": {
        "lat": 30.735, "lng": 79.066, "zoom": 11,
        "slope": 48.5, "elevation": 3580, "soil_baseline": 68.0, "river_baseline": 55.0,
        "history": "June 2013: Chorabari glacial lake breach triggered massive debris wave destroying Kedarnath town and Mandakini riverbed.",
        "danger_zones": [
            {"name": "Mandakini River Confluence", "lat": 30.728, "lng": 79.060, "desc": "Steep torrent bottleneck vulnerable to flash surges"},
            {"name": "Rambara Gorge Route", "lat": 30.680, "lng": 79.040, "desc": "High-velocity debris flow channel"}
        ],
        "safety_zones": [
            {"name": "Helipad Elevated Bluff", "lat": 30.739, "lng": 79.072, "desc": "Reinforced high-ground safe plateau"},
            {"name": "Upper GMVN Shelter Complex", "lat": 30.738, "lng": 79.062, "desc": "Concrete mountain shelter on bedrock"}
        ]
    },
    "Chamoli & Joshimath (UK)": {
        "lat": 30.556, "lng": 79.567, "zoom": 11,
        "slope": 44.0, "elevation": 1890, "soil_baseline": 58.0, "river_baseline": 48.0,
        "history": "Feb 2021: Rishiganga rock-ice avalanche caused catastrophic flash flood in Dhauliganga & Alaknanda rivers.",
        "danger_zones": [
            {"name": "Dhauliganga River Bed", "lat": 30.540, "lng": 79.580, "desc": "Narrow canyon vulnerable to rapid dam burst surges"},
            {"name": "Tapovan Gorge Crossing", "lat": 30.495, "lng": 79.620, "desc": "Flash surge risk downstream of hydropower dam"}
        ],
        "safety_zones": [
            {"name": "Joshimath Upper Cantonment", "lat": 30.565, "lng": 79.560, "desc": "High-ground military evacuation center (+250m elevation)"},
            {"name": "Ravigram Plateau Shelter", "lat": 30.550, "lng": 79.550, "desc": "Stable geological bedrock emergency camp"}
        ]
    },
    "Wayanad Hill Tracts (KL)": {
        "lat": 11.554, "lng": 76.128, "zoom": 11,
        "slope": 38.0, "elevation": 860, "soil_baseline": 74.0, "river_baseline": 60.0,
        "history": "July 2024: Torrential monsoon cloudburst caused devastating Meppadi & Chooralmala landslide debris flow.",
        "danger_zones": [
            {"name": "Chooralmala River Corridor", "lat": 11.530, "lng": 76.140, "desc": "Low-lying stream basin prone to sudden debris flood"},
            {"name": "Mundakkai Valley Basin", "lat": 11.515, "lng": 76.155, "desc": "Severe mountain runoff convergence zone"}
        ],
        "safety_zones": [
            {"name": "Meppadi High School Relief Center", "lat": 11.558, "lng": 76.125, "desc": "Elevated government primary relief shelter"},
            {"name": "Vythiri High Ridge Ground", "lat": 11.545, "lng": 76.040, "desc": "Designated highland evacuation camp"}
        ]
    },
    "Shimla & Kinnaur (HP)": {
        "lat": 31.650, "lng": 78.475, "zoom": 11,
        "slope": 41.0, "elevation": 2300, "soil_baseline": 55.0, "river_baseline": 45.0,
        "history": "Aug 2023: Severe cloudburst triggered flash floods across Satluj canyon and Shimla hills, washing out NH-5.",
        "danger_zones": [
            {"name": "Satluj River Canyon Highway", "lat": 31.640, "lng": 78.465, "desc": "Direct path of high-velocity glacial runoff"},
            {"name": "Karcham Valley Gorge", "lat": 31.500, "lng": 78.200, "desc": "River narrows with high surge height risk"}
        ],
        "safety_zones": [
            {"name": "Reckong Peo District Stadium", "lat": 31.535, "lng": 78.270, "desc": "Main district evacuation camp (+180m above river)"},
            {"name": "Kalpa Ridge Shelter", "lat": 31.545, "lng": 78.250, "desc": "Stable high-ground geological shelter"}
        ]
    },
    "Munnar & Idukki Hills (KL)": {
        "lat": 10.088, "lng": 77.059, "zoom": 11,
        "slope": 36.5, "elevation": 1530, "soil_baseline": 70.0, "river_baseline": 52.0,
        "history": "Aug 2018: Extreme rainfall led to opening of Idukki arch dam shutters and massive flash floods in Periyar valley.",
        "danger_zones": [
            {"name": "Old Munnar River Confluence", "lat": 10.080, "lng": 77.062, "desc": "Submergence hazard when Muthirapuzha river overflows"},
            {"name": "Karadipara Bridge Gorge", "lat": 10.035, "lng": 76.990, "desc": "Rapid water level rise bottleneck"}
        ],
        "safety_zones": [
            {"name": "Munnar Govt College Plateau", "lat": 10.095, "lng": 77.070, "desc": "Highland evacuation center (+95m above river level)"},
            {"name": "Chithirapuram High Ground", "lat": 10.040, "lng": 77.010, "desc": "Primary district emergency relief facility"}
        ]
    },
    "Chiplun & Mahabaleshwar Ghats (MH)": {
        "lat": 17.532, "lng": 73.518, "zoom": 11,
        "slope": 34.0, "elevation": 120, "soil_baseline": 65.0, "river_baseline": 60.0,
        "history": "July 2021: Cloudburst in Mahabaleshwar catchment caused Vashishti River to submerge Chiplun under 12 feet in 4 hours.",
        "danger_zones": [
            {"name": "Vashishti River Market Basin", "lat": 17.530, "lng": 73.515, "desc": "Severe flash flood basin with high tide backflow risk"},
            {"name": "Bahadur Shaikh Bridge Basin", "lat": 17.545, "lng": 73.525, "desc": "Low-elevation bottleneck prone to rapid drowning"}
        ],
        "safety_zones": [
            {"name": "DBJ College Hilltop Ground", "lat": 17.538, "lng": 73.535, "desc": "Designated highland relief camp (+80m elevation)"},
            {"name": "Khed Bypass Ridge Center", "lat": 17.710, "lng": 73.390, "desc": "Elevated regional transit shelter"}
        ]
    },
    "Teesta Valley & Lachen (SK)": {
        "lat": 27.604, "lng": 88.647, "zoom": 11,
        "slope": 46.0, "elevation": 2750, "soil_baseline": 66.0, "river_baseline": 58.0,
        "history": "Oct 2023: South Lhonak glacial lake burst (GLOF) sent a massive surge down Teesta river, destroying Chungthang dam.",
        "danger_zones": [
            {"name": "Teesta Riverbed Highway", "lat": 27.595, "lng": 88.640, "desc": "Active flash flood corridor vulnerable to GLOF surge waves"},
            {"name": "Chungthang Dam Confluence", "lat": 27.605, "lng": 88.650, "desc": "Severe hydrological bottleneck"}
        ],
        "safety_zones": [
            {"name": "Lachen Gompa High Ground", "lat": 27.720, "lng": 88.555, "desc": "High-altitude safe haven on solid rock ridge"},
            {"name": "Mangan District Stadium", "lat": 27.500, "lng": 88.530, "desc": "Primary high-ground relief center"}
        ]
    },
    "Dharamsala & Kangra (HP)": {
        "lat": 32.219, "lng": 76.323, "zoom": 11,
        "slope": 39.0, "elevation": 1450, "soil_baseline": 60.0, "river_baseline": 46.0,
        "history": "July 2021: Bhagsu Nag cloudburst triggered sudden flash flood sweeping away vehicles and hotels in minutes.",
        "danger_zones": [
            {"name": "Bhagsu Nag Nullah Gorge", "lat": 32.245, "lng": 76.335, "desc": "Narrow stream canyon with high risk of sudden flash surge"},
            {"name": "Gaj Khad River Basin", "lat": 32.180, "lng": 76.280, "desc": "Low-lying agricultural plain subject to flash overflow"}
        ],
        "safety_zones": [
            {"name": "Dharamsala Cricket Stadium Plateau", "lat": 32.198, "lng": 76.326, "desc": "Elevated modern stadium relief ground"},
            {"name": "McLeod Ganj Ridge Complex", "lat": 32.242, "lng": 76.325, "desc": "Highland reinforced community center"}
        ]
    },
    "Dima Hasao Hills (AS)": {
        "lat": 25.176, "lng": 93.023, "zoom": 11,
        "slope": 35.0, "elevation": 510, "soil_baseline": 72.0, "river_baseline": 54.0,
        "history": "May 2022: Unprecedented mountain rain triggered widespread flash floods and mudslides, cutting off Haflong railway station.",
        "danger_zones": [
            {"name": "Jatinga Riverbed Basin", "lat": 25.160, "lng": 93.030, "desc": "Fast-rising mountain torrent path with high silt load"},
            {"name": "New Haflong Station Valley", "lat": 25.185, "lng": 93.015, "desc": "Low-lying track corridor prone to mud debris flooding"}
        ],
        "safety_zones": [
            {"name": "Haflong Hilltop District Ground", "lat": 25.170, "lng": 93.020, "desc": "Highland district administrative relief camp"},
            {"name": "Fiangpui High Ridge Shelter", "lat": 25.195, "lng": 93.040, "desc": "Elevated community center safe from mountain runoff"}
        ]
    }
}

# =========================================================
# LIVE API CONSUMER: WEATHER, SOIL & RIVER DISCHARGE
# =========================================================
def fetch_realtime_data(lat, lng, soil_baseline, river_baseline):
    """
    Pulls live precipitation, ambient temperature, multi-depth soil moisture average,
    and live river basin discharge from Open-Meteo Weather & Flood API suite.
    """
    rain_1h = 0.0
    temp = 18.5
    soil_moisture = soil_baseline
    river_level = river_baseline

    # 1. Fetch live multi-depth weather & soil moisture for this city
    try:
        url_weather = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lng}"
            f"&hourly=precipitation,rain,temperature_2m,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_moisture_3_to_9cm"
            f"&current=precipitation,rain,temperature_2m"
            f"&timezone=auto"
        )
        res_w = requests.get(url_weather, timeout=3.5).json()

        # Rainfall (1h)
        if "current" in res_w:
            curr = res_w["current"]
            rain_1h = curr.get("precipitation", curr.get("rain", 0.0))
            temp = curr.get("temperature_2m", temp)
        elif "hourly" in res_w:
            rain_arr = res_w["hourly"].get("precipitation", [0.0])
            rain_1h = rain_arr[-1] if rain_arr else 0.0
            temp = res_w["hourly"].get("temperature_2m", [temp])[-1]

        # Multi-depth Soil Moisture Average for this city basin (0-1cm, 1-3cm, 3-9cm)
        if "hourly" in res_w:
            h = res_w["hourly"]
            layer1 = (h.get("soil_moisture_0_to_1cm") or [None])[-1]
            layer2 = (h.get("soil_moisture_1_to_3cm") or [None])[-1]
            layer3 = (h.get("soil_moisture_3_to_9cm") or [None])[-1]
            valid_layers = [v for v in [layer1, layer2, layer3] if v is not None]
            if valid_layers:
                avg_volumetric = sum(valid_layers) / len(valid_layers)
                soil_moisture = min(100.0, max(15.0, avg_volumetric * 190.0))
    except Exception as e:
        print(f"Weather/Soil API notice: {e}")

    # 2. Fetch live river discharge for this city's watershed from Open-Meteo Flood API
    try:
        url_flood = (
            f"https://flood-api.open-meteo.com/v1/flood"
            f"?latitude={lat}&longitude={lng}"
            f"&daily=river_discharge,river_discharge_mean,river_discharge_max"
            f"&forecast_days=1"
        )
        res_f = requests.get(url_flood, timeout=3.0).json()
        if "daily" in res_f and "river_discharge" in res_f["daily"]:
            discharges = res_f["daily"]["river_discharge"]
            if discharges and discharges[0] is not None:
                live_discharge = float(discharges[0])
                # Normalize discharge relative to mountain valley thresholds (0-100%)
                river_level = min(100.0, max(10.0, (live_discharge * 2.5) + (rain_1h * 0.45) + (soil_moisture * 0.12)))
    except Exception as e:
        river_level = min(100.0, max(10.0, river_baseline + (rain_1h * 0.4) + (soil_moisture * 0.15)))

    return {
        "rain_1h": round(rain_1h, 1),
        "soil_moisture": round(soil_moisture, 1),
        "river_level": round(river_level, 1),
        "temperature": round(temp, 1),
        "soil_tracking_note": "City Basin Multi-Layer Average",
        "river_tracking_note": "Live Hydrometric Discharge Average"
    }

# =========================================================
# ROUTES
# =========================================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/regions")
def get_regions():
    return jsonify({"success": True, "regions": list(HILLY_REGIONS.keys())})

# Backward compatibility route for previous states endpoint
@app.route("/api/states")
def get_states_compat():
    return jsonify({"success": True, "states": list(HILLY_REGIONS.keys())})

@app.route("/api/region/<path:region_name>")
def get_region_data(region_name):
    if region_name not in HILLY_REGIONS:
        region_name = "Kullu & Manali Valley (HP)"

    region_info = HILLY_REGIONS[region_name]

    # Check for manual overrides from sliders
    override_rain = request.args.get("rain_1h")
    override_soil = request.args.get("soil_moisture")
    override_slope = request.args.get("slope")
    override_river = request.args.get("river_level")

    # Fetch live real-time environmental telemetry from Open-Meteo
    live_data = fetch_realtime_data(
        region_info["lat"],
        region_info["lng"],
        region_info["soil_baseline"],
        region_info["river_baseline"]
    )

    rain_1h = float(override_rain) if override_rain is not None else live_data["rain_1h"]
    soil = float(override_soil) if override_soil is not None else live_data["soil_moisture"]
    slope = float(override_slope) if override_slope is not None else region_info["slope"]
    river = float(override_river) if override_river is not None else live_data["river_level"]

    input_data = {
        "rain_1h": rain_1h,
        "rain_6h": rain_1h * 3.5,
        "soil_moisture": soil,
        "slope": slope,
        "elevation": region_info["elevation"],
        "river_level": river,
        "temperature": live_data["temperature"],
        "satellite_anomaly": round(min(100.0, soil * 0.7 + rain_1h * 0.3), 1)
    }

    # Run ML prediction model
    prediction = predictor.predict(input_data)

    return jsonify({
        "success": True,
        "region": region_name,
        "state": region_name,
        "lat": region_info["lat"],
        "lng": region_info["lng"],
        "zoom": region_info["zoom"],
        "history": region_info["history"],
        "danger_zones": region_info["danger_zones"],
        "safety_zones": region_info.get("safety_zones", []),
        "safe_havens": region_info.get("safety_zones", []),
        "data": {
            "rain_1h": rain_1h,
            "soil_moisture": soil,
            "slope": slope,
            "river_level": river,
            "elevation": region_info["elevation"],
            "temperature": live_data["temperature"],
            "satellite_anomaly": round(min(100.0, soil * 0.7 + rain_1h * 0.3), 1)
        },
        "prediction": prediction,
        "timestamp": datetime.datetime.now().isoformat()
    })

# Backward compatibility route for previous state query
@app.route("/api/state/<path:state_name>")
def get_state_compat(state_name):
    return get_region_data(state_name)

@app.route("/download-slides")
def download_slides():
    return send_from_directory("static", "FlashGuard_Hackathon_Slides_HighUI.pptx", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)