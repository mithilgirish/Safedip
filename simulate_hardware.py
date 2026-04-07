import time
import requests
import random

API_URL = "http://localhost:8000/api/v1/ingest"

# Starting base parameters
ph = 7.3
tds = 400.0
turbidity = 15.0
temp = 28.5
orp = 700.0

print("Starting ESP32 Hardware Simulator...")
print(f"Target API: {API_URL}")

while True:
    # Add random drift to simulate realistic sensor variations
    ph += random.uniform(-0.02, 0.03)  
    tds += random.uniform(5, 15)        # Quickly accumulating TDS to trigger ML
    turbidity += random.uniform(-0.5, 1.0)
    temp += random.uniform(-0.2, 0.2)
    orp += random.uniform(-5, 0)        # Diminishing ORP

    # Ensure bounds so it doesn't go completely crazy right away
    ph = max(6.0, min(9.0, ph))
    tds = max(0, min(3000, tds))
    turbidity = max(0, min(100, turbidity))
    temp = max(15, min(40, temp))
    orp = max(300, min(900, orp))

    payload = {
        "device_id": "ESP32_01",
        "pool_id": "pool_vit_01",
        "temperature": round(temp, 2),
        "tds": round(tds, 1),
        "turbidity": round(turbidity, 1),
        "ph": round(ph, 2),
        "orp": round(orp, 1)
    }
    
    try:
        res = requests.post(API_URL, json=payload)
        print(f"[SUCCESS] Ingested -> pH: {payload['ph']}, TDS: {payload['tds']}")
    except Exception as e:
        print(f"[RETRYING] Backend offline or warming up...")
        
    time.sleep(3)
