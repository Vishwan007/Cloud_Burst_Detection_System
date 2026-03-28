from flask_cors import CORS
from flask import Flask, request, jsonify
import xgboost as xgb
import pandas as pd
import time
import os

app = Flask(__name__)

CORS(app, supports_credentials=True)

# ✅ ADD THIS HERE
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Load the AI model once at startup
print("Loading Emergency AI Brain...")
model = xgb.XGBClassifier()

# ✅ Safe path handling (VERY IMPORTANT for deployment)
model_path = os.path.join(os.path.dirname(__file__), "cloudburst_xgboost_master.json")
model.load_model(model_path)

# 🌍 Home route
@app.route('/')
def home():
    return "Cloud Burst API is running 🚀"

# 🌦️ Weather Prediction Endpoint
@app.route('/check_weather', methods=['POST', 'OPTIONS'])
def predict_burst():

    # ✅ Handle preflight request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "POST,OPTIONS"
        return response, 200

    # ✅ Handle POST request
    data = request.get_json()

    try:
        live_df = pd.DataFrame([{
            'Temp_C': float(data['temperature']),
            'Humidity_Ratio': float(data['humidity']),
            'Pressure_hPa': float(data['pressure'])
        }])

        probability_scores = model.predict_proba(live_df)[0]
        cloud_burst_risk = float(probability_scores[1])

        if cloud_burst_risk >= 0.70:
            response = jsonify({
                "alert_level": "RED",
                "status": "CRITICAL RISK",
                "message": "🚨 EXTREME CLOUD BURST RISK"
            })
        elif cloud_burst_risk >= 0.30:
            response = jsonify({
                "alert_level": "YELLOW",
                "status": "MODERATE RISK",
                "message": "⚠️ MODERATE RISK"
            })
        else:
            response = jsonify({
                "alert_level": "GREEN",
                "status": "NO RISK",
                "message": "✅ SAFE CONDITIONS"
            })

        # ✅ ADD CORS HEADERS HERE (IMPORTANT)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

# 🚨 SOS API
active_sos_alerts = []

@app.route('/api/sos', methods=['POST'])
def trigger_sos():
    data = request.get_json() or {}
    
    lat = data.get('lat', 'Unknown')
    lon = data.get('lon', 'Unknown')
    user_id = data.get('user_id', 'Anonymous')
    
    alert_record = {
        "timestamp": time.time(),
        "user_id": user_id,
        "lat": lat,
        "lon": lon,
        "status": "DISPATCHED"
    }
    
    active_sos_alerts.append(alert_record)
    
    print(f"\n🚨 SOS DETECTED | User: {user_id} | Lat:{lat}, Lon:{lon} | Active: {len(active_sos_alerts)}\n", flush=True)
    
    return jsonify({
        "success": True,
        "message": "SOS Broadcast received.",
        "active_beacons": len(active_sos_alerts)
    })
