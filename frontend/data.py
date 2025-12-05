from typing import Dict, Optional, List
import numpy as np
import requests

# CONFIGURATION API
API_BASE_URL = "http://localhost:8000"

# Counters cache
_COUNTERS_CACHE: List[Dict] = []


def get_all_counters() -> List[Dict]:
    """
    Retrieves the list of counters (ID, name, lat/lon) via the FastAPI API.
    Uses a cache to avoid repeating the request each time the page is loaded.
    """
    global _COUNTERS_CACHE
    if _COUNTERS_CACHE:
        return _COUNTERS_CACHE

    try:
        url = f"{API_BASE_URL}/api/counters"
        response = requests.get(url, timeout=2)
        response.raise_for_status()

        _COUNTERS_CACHE = response.json()
        if not _COUNTERS_CACHE:
            print("No counters found.")
            return []
        return _COUNTERS_CACHE
    except requests.RequestException as e:
        print(f"Error retrieving counters: {e}")
        return []


def get_counter_by_id(station_id: str) -> Optional[Dict]:
    """Find a counter in the list by its ID."""
    for counter in get_all_counters():
        if counter["station_id"] == station_id:
            return counter
    return None


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
