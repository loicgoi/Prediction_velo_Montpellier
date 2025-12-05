from requests.exceptions import HTTPError, RequestException, Timeout, ConnectionError
import requests_cache
from retry_requests import retry
from utils.logging_config import logger
from download.abstract_loader import BaseAPILoader
from typing import Optional, Dict, Any


class WeatherHistoryLoader(BaseAPILoader):
    """
    Loader that connects to Open-Meteo API and returns raw JSON weather data.
    Inherits from BaseAPILoader and implements the abstract method `fetch_data`.
    """

    def __init__(self, latitude: float = 43.6107, longitude: float = 3.8767):
        """
        Initialize WeatherHistoryLoader with caching and retry sessions.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
        """
        cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.3)
        self.session = retry_session
        self.url = "https://archive-api.open-meteo.com/v1/archive"
        self.latitude = latitude
        self.longitude = longitude

    def fetch_data(
        self, start_date: str = "2022-12-24", end_date: str = "2025-12-04"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch historical weather data from Open-Meteo API.

        Args:
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.

        Returns:
            dict: JSON response containing weather data if successful.
            None: If an error occurs.
        """
        logger.info(f"Fetching weather history from {start_date} to {end_date}...")
        print(f"Fetching weather history from {start_date} to {end_date}...")

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"],
            "timezone": "Europe/Paris",
        }

        try:
            response = self.session.get(self.url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            logger.info("Weather history fetched successfully.")
            print("Weather data fetched successfully")
            return data

        except HTTPError as e:
            logger.error(f"HTTP error: {e}")

        except Timeout:
            logger.error("Timeout while contacting Open-Meteo API.")

        except ConnectionError as e:
            logger.error(f"Connection error: {e}")

        except RequestException as e:
            logger.error(f"Unexpected requests error: {e}")

        except ValueError as e:
            logger.error(f"JSON parsing error: {e}")

        except Exception as e:
            logger.error(f"Unexpected WeatherHistoryLoader error: {e}")

        return None
