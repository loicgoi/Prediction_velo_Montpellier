import os
from typing import Dict, Optional, List
import numpy as np
import requests


# CONFIGURATION API
def _get_api_url() -> str:
    """
    Determines the API base URL with a smart fallback mechanism.
    The function prioritizes the URL in the following order:

    1.  **Environment Variable (`API_BASE_URL`)**:
        Used for production deployments like Azure App Service.

    2.  **Docker Environment**:
        If the file `/.dockerenv` exists, it assumes it's running in a Docker
        container via Docker Compose and uses the service name.

    3.  **Local Development**:
        As a final fallback, it uses `localhost` for local development
        without containers.
    """
    if "API_BASE_URL" in os.environ:
        return os.environ["API_BASE_URL"]
    if os.path.exists("/.dockerenv"):
        return "http://backend:8000"  # Docker Compose service name
    return "http://localhost:8000"  # Local development without Docker


API_BASE_URL = _get_api_url()

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


def get_dashboard_data(station_id: str) -> Dict:
    """
    Retrieves the actual aggregated data from the backend for a meter.
    """
    try:
        url = f"{API_BASE_URL}/api/dashboard/{station_id}"

        res = requests.get(url, timeout=4)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error fetching dashboard for {station_id}: {e}")
        # Returns an empty “safe” structure to prevent the UI from crashing
        return {
            "prediction_today": 0,
            "yesterday": {"real": 0, "predicted": 0},
            "history_30_days": [0] * 30,
            "accuracy_7_days": {"real": [0] * 7, "pred": [0] * 7},
            "weekly_averages": [0] * 7,
            "weekly_totals": [0] * 12,
        }
