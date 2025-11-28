import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from pathlib import Path
import logging

# Configuration des chemins (meme logique que data_loder.py)
CURRENT_DIR = Path(__file__).resolve().parent
DATA_PATH = CURRENT_DIR.parent.parent / "data/raw"
DATA_PATH.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherLoader:
    def __init__(self):
        # Configuration du client avec cache et retry automatique
        cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        self.openmeteo = openmeteo_requests.Client(session = retry_session)
        
        self.url = "https://archive-api.open-meteo.com/v1/archive"
        # Coordonnees de Montpellier
        self.lat = 43.6107
        self.lon = 3.8767

    def fetch_history(self, start_date="2023-01-01", end_date="2025-10-31"):
        """
        Interroge l'API OpenMeteo Archive pour recuperer temperature, pluie et vent.
        Sauvegarde le resultat en CSV.
        """
        logger.info(f"Recuperation Meteo de {start_date} a {end_date}...")

        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"],
            "timezone": "Europe/Paris"
        }

        try:
            responses = self.openmeteo.weather_api(self.url, params=params)
            response = responses[0]
            
            daily = response.Daily()
            
            # Extraction des variables
            daily_data = {
                "date": pd.date_range(
                    start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
                    end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
                    freq = pd.Timedelta(seconds = daily.Interval()),
                    inclusive = "left"
                ),
                "avg_temp": daily.Variables(0).ValuesAsNumpy(),
                "precipitation_mm": daily.Variables(1).ValuesAsNumpy(),
                "vent_max": daily.Variables(2).ValuesAsNumpy()
            }

            df = pd.DataFrame(data = daily_data)
            # Formatage de la date en YYYY-MM-DD
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            output_file = DATA_PATH / "weather_history.csv"
            df.to_csv(output_file, index=False)
            
            print(f"Meteo sauvegardee dans : {DATA_PATH}")
            return df

        except Exception as e:
            logger.error(f"Erreur OpenMeteo : {e}")
            return None