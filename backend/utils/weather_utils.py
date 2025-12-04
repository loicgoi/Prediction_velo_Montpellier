from typing import Dict, Any

def extract_daily_values(response: Any) -> Dict[str, float]:
    """
    Extracts scalar values (Temp, Precip, Wind) from an OpenMeteo SDK response object.
    
    This function is a helper: it doesn't fetch data, it just formats 
    the binary object received from the API into a clean Dictionary.
    
    Args:
        response: The OpenMeteo API response object (from the SDK).
        
    Returns:
        dict: Simplified dictionary with keys 'avg_temp', 'vent_max', 'precipitation_mm'.
    """
    # The 'response' object is passed as an argument.
    # We access its methods (.Daily(), .Variables()) dynamically.
    daily = response.Daily()
    
    # IMPORTANT: The index (0, 1, 2) depends on the order of variables 
    # requested in daily_weather_api.py.
    # Order assumed: ["temperature_2m_mean", "wind_speed_10m_mean", "precipitation_sum"]
    
    # .ValuesAsNumpy() returns an array. We take the first element [0] (today).
    avg_temp = float(daily.Variables(0).ValuesAsNumpy()[0])
    wind_max = float(daily.Variables(1).ValuesAsNumpy()[0])
    precip_mm = float(daily.Variables(2).ValuesAsNumpy()[0])
    
    return {
        "avg_temp": avg_temp,
        "vent_max": wind_max,
        "precipitation_mm": precip_mm
    }