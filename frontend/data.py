from typing import Dict, Optional
import numpy as np
import requests

# CONFIGURATION & DATA
MOCK_COUNTERS = [
    {"station_id": "counter-01", "name": "Albert 1er", "lat": 43.615, "lon": 3.872},
    {"station_id": "counter-02", "name": "Lattes", "lat": 43.567, "lon": 3.908},
    {
        "station_id": "counter-03",
        "name": "Place de la Comédie",
        "lat": 43.608,
        "lon": 3.879,
    },
]


def get_mock_backend_data() -> Dict:
    """Simule une réponse du backend avec des données aléatoires."""
    return {
        "prediction_today": np.random.randint(200, 800),
        "yesterday": {
            "predicted": np.random.randint(200, 800),
            "real": np.random.randint(200, 800),
        },
        "history_30_days": np.random.randint(150, 700, 30).tolist(),
        "accuracy_7_days": {
            "real": np.random.randint(300, 600, 7).tolist(),
            "pred": np.random.randint(300, 600, 7).tolist(),
        },
        "weekly_averages": np.random.randint(400, 650, 7).tolist(),
        "weekly_totals": np.random.randint(2500, 4500, 12).tolist(),
    }


def get_real_weather(lat: float, lon: float) -> Dict[str, str]:
    """Retrieves current weather data from the Open-Meteo API."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,wind_speed_10m&timezone=auto"
        res = requests.get(url, timeout=2)
        res.raise_for_status()
        d = res.json().get("current", {})
        return {
            "temp": f"{d.get('temperature_2m')}°C",
            "precip": f"{d.get('precipitation')}mm",
            "wind": f"{d.get('wind_speed_10m')}km/h",
        }
    except requests.RequestException:
        return {"temp": "--", "precip": "--", "wind": "--"}


def get_counter_by_id(station_id: str) -> Optional[Dict]:
    """Find a counter in the list by its ID."""
    return next((c for c in MOCK_COUNTERS if c["station_id"] == station_id), None)
