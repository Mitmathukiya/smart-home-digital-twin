import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_historical_weather(days=90):
    """Fetches hourly weather data from Open-Meteo for ML training."""
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Magdeburg Coordinates
    lat, lon = 52.12, 11.62
    
    url = f"https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": "temperature_2m,relative_humidity_2m,direct_radiation,cloud_cover",
        "timezone": "Europe/Berlin"
    }
    
    print(f"Fetching {days} days of data from {start_date} to {end_date}...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['hourly'])
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        
        # Save to CSV for the Jupyter Notebooks to consume
        df.to_csv("historical_weather_magdeburg.csv")
        print(f"Success! Shape: {df.shape}. Saved to historical_weather_magdeburg.csv")
        return df
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

if __name__ == "__main__":
    fetch_historical_weather()