import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_synthetic_occupancy(days=90):
    """
    Generates realistic synthetic occupancy data for 3 rooms over N days.
    Includes weekday vs weekend logic, time-of-day curves, and Gaussian noise.
    """
    print(f"Generating {days} days of synthetic occupancy data...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Create an hourly timestamp index
    timestamps = pd.date_range(start=start_date, end=end_date, freq='h')
    df = pd.DataFrame({'time': timestamps})
    
    # Extract temporal features
    df['hour'] = df['time'].dt.hour
    df['day_of_week'] = df['time'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    # Initialize empty columns
    df['occ_living_room'] = 0
    df['occ_kitchen'] = 0
    df['occ_master_bed'] = 0

    for index, row in df.iterrows():
        h = row['hour']
        is_weekend = row['is_weekend']
        
        # --- KITCHEN LOGIC (Spikes at meals) ---
        k_prob = 0.05
        if 7 <= h <= 9: k_prob = 0.8 if not is_weekend else 0.4  # Breakfast
        elif 12 <= h <= 14: k_prob = 0.5  # Lunch
        elif 18 <= h <= 20: k_prob = 0.85 # Dinner
        
        # --- LIVING ROOM LOGIC (Evening relaxation) ---
        l_prob = 0.1
        if 18 <= h <= 23: 
            l_prob = 0.9  # High chance in the evening
        elif is_weekend and 10 <= h <= 22:
            l_prob = 0.6  # Consistent chance on weekends
            
        # --- MASTER BEDROOM LOGIC (Sleeping) ---
        b_prob = 0.05
        if h >= 22 or h <= 7:
            b_prob = 0.95 # Almost definitely asleep
            
        # Add Gaussian noise (randomness) to make it realistic for ML
        k_prob = np.clip(k_prob + np.random.normal(0, 0.1), 0, 1)
        l_prob = np.clip(l_prob + np.random.normal(0, 0.1), 0, 1)
        b_prob = np.clip(b_prob + np.random.normal(0, 0.1), 0, 1)
        
        # Convert probabilities to binary (1 = occupied, 0 = empty)
        df.at[index, 'occ_kitchen'] = np.random.binomial(1, k_prob)
        df.at[index, 'occ_living_room'] = np.random.binomial(1, l_prob)
        df.at[index, 'occ_master_bed'] = np.random.binomial(1, b_prob)

    # Save to CSV
    df.set_index('time', inplace=True)
    df.to_csv("synthetic_occupancy_data.csv")
    print(f"Success! Generated {len(df)} rows. Saved to backend/data/synthetic_occupancy_data.csv")

if __name__ == "__main__":
    generate_synthetic_occupancy()