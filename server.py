from flask_cors import CORS
from flask import Flask, request, jsonify
import xgboost as xgb
import pandas as pd
import time
import os

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://cloud-burst-detection-system-frontend-8lux5vuy.vercel.app"
        ]
    }
})

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
@app.route('/check_weather', methods=['POST'])
def predict_burst():
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
            return jsonify({
                "alert_level": "RED",
                "status": "CRITICAL RISK",
                "message": f"🚨 EXTREME CLOUD BURST PROBABILITY ({cloud_burst_risk*100:.1f}% Match). Evacuation warning issued! 🚨"
            })
        elif cloud_burst_risk >= 0.30:
            return jsonify({
                "alert_level": "YELLOW",
                "status": "MODERATE RISK",
                "message": f"⚠️ ATMOSPHERIC INSTABILITY ({cloud_burst_risk*100:.1f}% Match). Monitor closely."
            })
        else:
            return jsonify({
                "alert_level": "GREEN",
                "status": "NO RISK",
                "message": f"✅ Stable conditions ({cloud_burst_risk*100:.1f}% chance of burst)."
            })
            
    except Exception as e:
        return jsonify({"error": str(e)})

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
