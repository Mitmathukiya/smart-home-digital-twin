from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import datetime
import joblib
import pandas as pd
import requests
import google.generativeai as genai
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

# Initialize the ML Backend App
app = FastAPI(
    title="Microgrid ML Hub",
    description="AI/ML Backend for Smart Home Digital Twin",
    version="1.0.0"    
)

# Insert your real API key here!
genai.configure(api_key="AIzaSyDcpawp9VgqWr6k4hSt1oNQDrLJwTxzT3Q")
llm_model = genai.GenerativeModel('gemini-1.5-flash') # Fast, perfect for real-time voice

# We define the shape of the data the frontend will send us
class ChatRequest(BaseModel):
    transcript: str
    house_state: dict

# --- ROUTE 4: CONVERSATIONAL AI (LLM) ---
@app.post("/chat")
async def chat_with_house(request: ChatRequest):
    """Feeds the live house state to an LLM to answer user questions."""
    try:
        # We inject the LIVE JSON data of your house into the AI's system prompt
        prompt = f"""
        You are the AI brain of a highly advanced smart home. You are helpful, concise, and slightly witty.
        Your primary job is to answer the user's questions based on the CURRENT telemetry of the house.
        
        DO NOT use formatting like markdown, asterisks, or bold text, because your response will be read aloud by a Text-to-Speech engine. Keep answers under 3 sentences.
        
        LIVE HOUSE STATE:
        {request.house_state}
        
        USER QUESTION: "{request.transcript}"
        """
        
        # Ask Gemini!
        response = llm_model.generate_content(prompt)
        
        # Clean up any accidental asterisks the LLM might generate
        clean_text = response.text.replace('*', '')
        
        return {"status": "success", "reply": clean_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IN-MEMORY MODEL STORE ---
models = {
    "prophet_energy": None,
    "xgboost_occupancy": None,
    "isolation_forest": None
}

@app.on_event("startup")
async def load_models():
    """Loads serialized .pkl models into memory on server start."""
    print("Loading ML models into memory...")
    
    # Load Prophet (Energy)
    try:
        models["prophet_energy"] = joblib.load("model_store/prophet_energy_v1.pkl")
        print("✅ Prophet Energy Model loaded successfully!")
    except Exception as e:
        print(f"⚠️ Could not load Prophet model: {e}")
        
    # Load XGBoost (Occupancy)
    try:
        models["xgboost_occupancy"] = joblib.load("model_store/xgboost_occupancy_v1.pkl")
        print("✅ XGBoost Occupancy Models loaded successfully!")
    except Exception as e:
        print(f"⚠️ Could not load XGBoost models: {e}")

        # Load Isolation Forest (Anomaly Detection)
    try:
        models["isolation_forest"] = joblib.load("model_store/isolation_forest_v1.pkl")
        print("✅ Isolation Forest Model loaded successfully!")
    except Exception as e:
        print(f"⚠️ Could not load Isolation Forest: {e}")

# ... (Keep your Prophet route exactly as it is) ...

# --- ROUTE 2: OCCUPANCY PREDICTION (XGBoost) ---
@app.get("/predict/occupancy")
async def predict_occupancy():
    """Returns real ML occupancy probabilities based on current time & weather."""
    
    if models["xgboost_occupancy"] is None:
        raise HTTPException(status_code=503, detail="XGBoost models not loaded.")

    try:
        # 1. Get the current time features
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # 2. Get current live weather from Open-Meteo
        url = "https://api.open-meteo.com/v1/forecast?latitude=52.12&longitude=11.62&current=temperature_2m,cloud_cover&timezone=Europe%2FBerlin"
        weather_res = requests.get(url).json()
        temp = weather_res['current']['temperature_2m']
        cloud = weather_res['current']['cloud_cover']
        
        # 3. Format the exact features XGBoost was trained on
        # Order matters! ['hour', 'day_of_week', 'is_weekend', 'temperature_2m', 'cloud_cover']
        features = pd.DataFrame([[hour, day_of_week, is_weekend, temp, cloud]], 
                                columns=['hour', 'day_of_week', 'is_weekend', 'temperature_2m', 'cloud_cover'])
        
        probabilities = {}
        
        # 4. Ask all 3 room brains for their prediction
        for room, model in models["xgboost_occupancy"].items():
            # predict_proba returns an array like [[prob_empty, prob_occupied]]
            # We want the second number (index 1), which is the probability someone is inside
            prob_occupied = model.predict_proba(features)[0][1] 
            
            # Clean up the name for the frontend (e.g., 'occ_living_room' -> 'living_room')
            clean_name = room.replace('occ_', '')
            probabilities[clean_name] = round(float(prob_occupied), 2)

        return {
            "status": "success",
            "model": "XGBoost_v1",
            "current_context": {"hour": hour, "temp": temp},
            "probabilities": probabilities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ROUTE 1: ENERGY FORECASTING (Prophet) ---
@app.get("/forecast/energy")
async def energy_forecast(hours_ahead: int = 24):
    """Returns real ML energy consumption forecast using live weather data."""
    
    if models["prophet_energy"] is None:
        raise HTTPException(status_code=503, detail="Model not loaded in memory.")

    try:
        # 1. Fetch the LIVE weather forecast from Open-Meteo for Magdeburg
        # (Prophet needs to know the future temperature to predict future energy!)
        url = "https://api.open-meteo.com/v1/forecast?latitude=52.12&longitude=11.62&hourly=temperature_2m&forecast_days=2&timezone=Europe%2FBerlin"
        weather_res = requests.get(url).json()
        
        # 2. Format the future data exactly how Prophet expects it
        future_dates = pd.to_datetime(weather_res['hourly']['time'])[:hours_ahead]
        future_temps = weather_res['hourly']['temperature_2m'][:hours_ahead]
        
        future_df = pd.DataFrame({
            'ds': future_dates,
            'temperature_2m': future_temps
        })
        
        # Add our 'is_weekend' regressor logic
        future_df['is_weekend'] = future_df['ds'].dt.dayofweek.isin([5, 6]).astype(int)
        
        # 3. THE MAGIC: Ask the ML model to predict the future!
        forecast = models["prophet_energy"].predict(future_df)
        
        # 4. Format the output for our JavaScript frontend
        results = []
        for index, row in forecast.iterrows():
            results.append({
                "timestamp": row['ds'].isoformat(),
                "forecast_watts": max(100, round(row['yhat'], 2)) # Prevent negative watts
            })
            
        return {
            "status": "success",
            "model": "Prophet_v1",
            "hours_ahead": hours_ahead,
            "forecast": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# # --- ROUTE 2: OCCUPANCY PREDICTION (Stub) ---
# @app.get("/predict/occupancy")
# async def predict_occupancy():
#     return {"status": "stub", "probabilities": {"living_room": 0.85, "kitchen": 0.12, "master_bed": 0.05}}


# --- ROUTE 3: ANOMALY DETECTION (Isolation Forest) ---
@app.get("/detect/anomalies")
async def detect_anomalies(current_draw_watts: float):
    """Real AI Anomaly Detection using Isolation Forest."""
    
    if models["isolation_forest"] is None:
        raise HTTPException(status_code=503, detail="Isolation Forest model not loaded.")

    try:
        # Create a dataframe just like the model was trained on
        input_data = pd.DataFrame([[current_draw_watts]], columns=['power_watts'])
        
        # Predict: Returns [1] for normal, [-1] for anomaly
        prediction = models["isolation_forest"].predict(input_data)[0]
        
        # Convert the -1/1 output into a True/False boolean for the frontend
        is_anomaly = bool(prediction == -1)
        
        return {
            "status": "success",
            "model": "IsolationForest_v1",
            "current_draw": current_draw_watts,
            "is_anomaly": is_anomaly
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def health_check():
    return {"status": "ok", "models_loaded": models["prophet_energy"] is not None}


@app.get("/api/analytics/7-day")
async def get_weekly_analytics():
    """Returns energy consumption and solar yield (kWh) for the last 7 days."""
    
    # Generate the dates for the last 7 days
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    
    # Synthetic daily usage (between 12 kWh and 35 kWh)
    usage_kwh = [round(random.uniform(12.0, 35.0), 1) for _ in range(7)]
    
    # Synthetic daily solar yield (between 8 kWh and 28 kWh - assuming a decent solar setup!)
    solar_kwh = [round(random.uniform(8.0, 28.0), 1) for _ in range(7)]
    
    return {
        "dates": dates,
        "usage_kwh": usage_kwh,
        "solar_kwh": solar_kwh
    }