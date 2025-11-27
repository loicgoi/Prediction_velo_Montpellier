import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from pathlib import Path
import logging

# Configuration
IDS_PATH = Path(__file__).parent
# On remonte d'un cran (..) pour aller dans backend/ puis dans data/raw
DATA_PATH = IDS_PATH / "../data/raw"
DATA_PATH.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


class WeatherLoader:
    def __init__(self):
        cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
        self.url = "https://archive-api.open-meteo.com/v1/archive"
        self.lat = 43.6107
        self.lon = 3.8767

    def fetch_history(self, start_date="2024-01-01", end_date="2024-12-31"):
        logger.info(f"Récupération Météo de {start_date} à {end_date}...")
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"],
            "timezone": "Europe/Paris",
        }

        try:
            responses = self.openmeteo.weather_api(self.url, params=params)
            response = responses[0]
            daily = response.Daily()

            daily_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left",
                ),
                "avg_temp": daily.Variables(0).ValuesAsNumpy(),
                "precipitation_mm": daily.Variables(1).ValuesAsNumpy(),
                "vent_max": daily.Variables(2).ValuesAsNumpy(),
            }

            df = pd.DataFrame(data=daily_data)
            df["date"] = df["date"].dt.strftime("%Y-%m-%d")

            output_file = DATA_PATH / "weather_history.csv"
            df.to_csv(output_file, index=False)
            print(f"Météo sauvegardée dans : {DATA_PATH}")
            return df

        except Exception as e:
            logger.error(f"Erreur OpenMeteo : {e}")
            return None
