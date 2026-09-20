import pandas as pd
import numpy as np

DORMS = ["Maple Hall", "Pine House", "Cedar Court", "Birch Lodge", "Elm Residence"]


def generate_mock_data(days=30, seed=42):
    """Generate fake daily energy usage (kWh) per dorm."""
    np.random.seed(seed)

    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)

    records = []
    for dorm in DORMS:
        base_usage = np.random.uniform(80, 150)  # each dorm has a different baseline
        trend = np.random.uniform(-0.5, 0.3)  # some dorms trend down (improving), some up

        for i, date in enumerate(dates):
            noise = np.random.normal(0, 8)  # daily randomness
            usage = base_usage + (trend * i) + noise
            usage = max(usage, 20)  # keep it realistic, no negative energy

            records.append({
                "dorm": dorm,
                "date": date,
                "kwh": round(usage, 1)
            })

    return pd.DataFrame(records)