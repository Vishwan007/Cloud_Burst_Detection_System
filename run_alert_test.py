import xgboost as xgb
import pandas as pd

# 1. Load your newly downloaded AI Brain
print("Loading AI Brain...")
model = xgb.XGBClassifier()
model.load_model("cloudburst_xgboost_master.json")

# 2. Simulate pushing "Live Weather" into the system
# Let's pretend a weather station just sent us these terrifying numbers:
# Extremely high pressure shift, 100% suffocating humidity, and 30C heat
live_weather_data = pd.DataFrame({
    'Temp_C': [30.5],
    'Humidity_Ratio': [0.025], # Very high humidity
    'Pressure_hPa': [998.0]   # Dropping pressure
})

print("\nScanning current weather conditions for anomalies...")

# 3. Ask the AI what it thinks is going to happen
prediction = model.predict(live_weather_data)

# 4. Trigger the Alert!
if prediction[0] == 1:
    print("\n🚨 CRITICAL ALERT: CLOUD BURST DETECTED! 🚨")
    print("Initiating emergency SMS broadcast protocol...")
else:
    print("\n✅ Skies are clear. All normal.")
