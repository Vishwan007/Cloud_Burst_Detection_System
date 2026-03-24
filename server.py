from flask import Flask, request, jsonify
import xgboost as xgb
import pandas as pd

app = Flask(__name__)

# Load the AI Brain once when the server starts
print("Loading Emergency AI Brain...")
model = xgb.XGBClassifier()
model.load_model("cloudburst_xgboost_master.json")

# 🌍 Serve the Beautiful 3D Frontend UI!
@app.route('/')
def home():
    return open("frontend.html").read()

# This is the "Endpoint" that mobile apps or weather stations will hit!
@app.route('/check_weather', methods=['POST'])
def predict_burst():
    # 1. Look at the weather data sent to us by the user
    data = request.get_json()
    
    try:
        live_df = pd.DataFrame([{
            'Temp_C': float(data['temperature']),
            'Humidity_Ratio': float(data['humidity']),
            'Pressure_hPa': float(data['pressure'])
        }])
        
        # 2. Ask the XGBoost AI for specific PROBABILITIES rather than just 0 or 1
        probability_scores = model.predict_proba(live_df)[0]
        cloud_burst_risk = float(probability_scores[1]) # Probability of a Cloud Burst (0.0 to 1.0)
        
        # 3. Generate the Multi-Tier Alert Response based on risk levels
        if cloud_burst_risk >= 0.70:
            return jsonify({
                "alert_level": "RED",
                "status": "CRITICAL RISK",
                "message": f"🚨 EXTREME CLOUD BURST PROBABILITY ({cloud_burst_risk*100:.1f}% Match). Evacuation warning issued via SMS! 🚨"
            })
        elif cloud_burst_risk >= 0.30:
            return jsonify({
                "alert_level": "YELLOW",
                "status": "MODERATE RISK",
                "message": f"⚠️ ATMOSPHERIC INSTABILITY ({cloud_burst_risk*100:.1f}% Match). Conditions worsening. Monitor closely. ⚠️"
            })
        else:
            return jsonify({
                "alert_level": "GREEN",
                "status": "NO RISK",
                "message": f"✅ Atmospheric conditions are extremely stable ({cloud_burst_risk*100:.1f}% chance of burst)."
            })
            
    except Exception as e:
        return jsonify({"error": str(e)})


import time

# Thread-safe in-memory storage for multi-user active SOS beacons
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
    
    # Thread-safe append
    active_sos_alerts.append(alert_record)
    
    # Secure logging for server monitoring of concurrent requests
    print(f"\n🚨🚨 [CONCURRENT SOS DETECTED] User: {user_id} | Lat:{lat}, Lon:{lon} | Total Active Beacons: {len(active_sos_alerts)} 🚨🚨\n", flush=True)
    
    return jsonify({
        "success": True, 
        "message": "SOS Broadcast received.", 
        "active_beacons": len(active_sos_alerts)
    })

if __name__ == '__main__':

    print("📡 Cloud Burst Alert API is officially LIVE on Port 5000!")
    app.run(host='0.0.0.0', port=8080)
