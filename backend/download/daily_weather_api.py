import openmeteo_requests
import requests_cache
from retry_requests import retry
from typing import Any, List
import requests
from utils.logging_config import logger


class OpenMeteoDailyAPIC:
    """
    A client class to fetch daily weather data from Open-Meteo API.
    Uses caching and automatic retry on errors.
    """

    def __init__(self) -> None:
        """
        Initialize the API client with cache and retry configuration.
        """
        try:
            cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
            self.session = retry(cache_session, retries=5, backoff_factor=0.2)
            self.client = openmeteo_requests.Client(session=self.session)
        except Exception as e:
            logger.error(f"Failed to initialize Open-Meteo client: {e}")
            raise

    def get_weather_json(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        daily_variables: List[str] = [
            "temperature_2m_mean",
            "wind_speed_10m_mean",
            "precipitation_sum",
        ],
        timezone: str = "Europe/London",
    ) -> Any:
        """
        Fetch daily weather data from Open-Meteo API for the given coordinates and date range.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.
            daily_variables (List[str], optional): List of daily variables to fetch.
                Defaults to temperature, wind speed, and precipitation.
            timezone (str, optional): Timezone for the response. Defaults to "Europe/London".

        Returns:
            Any: JSON-like response object from Open-Meteo API.

        Raises:
            ValueError: If the API returns no data.
            requests.exceptions.RequestException: If a network or HTTP error occurs.
            Exception: For other unexpected errors.
        """
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": daily_variables,
                "timezone": timezone,
                "start_date": start_date,
                "end_date": end_date,
            }

            responses = self.client.weather_api(url, params=params)

            if not responses or len(responses) == 0:
                raise ValueError("No data returned from Open-Meteo API.")

            return responses

        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network or HTTP error: {req_err}")
            raise

        except IndexError as idx_err:
            logger.error(
                f"Unexpected response structure from Open-Meteo API: {idx_err}"
            )
            raise

        except ValueError as val_err:
            logger.error(f"Data error: {val_err}")
            raise

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise
