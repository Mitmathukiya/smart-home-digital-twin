# 🏠 AI-Powered Smart Home Digital Twin

A real-time, closed-loop cyber-physical system that uses Machine Learning to perceive, anticipate, and protect a simulated smart home environment. 

## 🧠 Intelligence Architecture

This project moves beyond standard static dashboards by integrating three distinct Machine Learning algorithms into a unified FastAPI backend:

1. **Predictive Analytics (Time-Series):** Uses **Prophet** to forecast the home's 6-hour energy draw and solar yield based on historical usage and live weather data.
2. **Behavioral Classification:** Uses **XGBoost** to calculate real-time probabilities of human occupancy in different spatial zones, autonomously controlling lighting and climate systems.
3. **Unsupervised Anomaly Detection:** Uses an **Isolation Forest** (The "Eco-Guard") to continuously monitor aggregate house load. It flags dangerous power spikes (e.g., running AC and Space Heaters simultaneously) and flashes a UI warning to prevent grid strain.

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn
* **Machine Learning:** Scikit-Learn, XGBoost, Prophet, Pandas, NumPy
* **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript, Chart.js
* **Data Sources:** Open-Meteo API (Live Weather & AQI integration)

## 🚀 How to Run Locally

### 1. Start the ML Brain (Backend)
Navigate to the backend directory, activate your virtual environment, and start the server:
```bash
cd backend
uvicorn main:app --reload