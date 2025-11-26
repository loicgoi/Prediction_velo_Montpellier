import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from pathlib import Path
import logging

# Configuration des chemins
IDS_PATH = Path(__file__).parent
DATA_PATH = IDS_PATH / "../../data/raw"
DATA_PATH.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

class WeatherLoader:
    def __init__(self):
        # Configuration du client API avec cache (ton code d'origine)
        # Le cache évite de redemander la même météo si on relance le script 5 min après
        cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        self.openmeteo = openmeteo_requests.Client(session = retry_session)
        
        self.url = "https://archive-api.open-meteo.com/v1/archive"
        
        # Coordonnées de Montpellier (Place de la Comédie environ)
        self.lat = 43.6107
        self.lon = 3.8767

    def fetch_history(self, start_date="2023-01-01", end_date="2025-10-31"):
        """Récupère l'historique météo journalier"""
        logger.info(f"☀️ Récupération Météo de {start_date} à {end_date}...")

        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": start_date,
            "end_date": end_date,
            # On demande les variables qui correspondent à notre BDD
            "daily": ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"],
            "timezone": "Europe/Paris"
        }

        try:
            responses = self.openmeteo.weather_api(self.url, params=params)
            response = responses[0] 
            
            # --- Traitement des données ---
            daily = response.Daily()
            
            # Extraction des valeurs numpy
            daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
            daily_precipitation_sum = daily.Variables(1).ValuesAsNumpy()
            daily_wind_speed_10m_max = daily.Variables(2).ValuesAsNumpy()

            # Création du dictionnaire
            daily_data = {
                "date": pd.date_range(
                    start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
                    end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
                    freq = pd.Timedelta(seconds = daily.Interval()),
                    inclusive = "left"
                )
            }
            
            daily_data["avg_temp"] = daily_temperature_2m_mean
            daily_data["precipitation_mm"] = daily_precipitation_sum
            daily_data["vent_max"] = daily_wind_speed_10m_max

            # Création DataFrame
            df = pd.DataFrame(data = daily_data)
            
            # Nettoyage format date (on retire l'heure et le timezone pour le CSV)
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            # Sauvegarde
            output_file = DATA_PATH / "weather_history.csv"
            df.to_csv(output_file, index=False)
            
            logger.info(f"Météo sauvegardée : {len(df)} jours récupérés.")
            return df

        except Exception as e:
            logger.error(f" Erreur OpenMeteo : {e}")
            return None

# Test rapide si on lance ce fichier seul
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loader = WeatherLoader()
    df = loader.fetch_history()
    print(df.head())