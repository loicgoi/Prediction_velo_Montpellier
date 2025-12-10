from download.abstract_loader import BaseAPILoader
import requests
import time
from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException
from utils.logging_config import logger
from typing import Optional, Any, Dict

base_url = "https://portail-api-data.montpellier3m.fr/ecocounter"


class EncountersIDsLoader(BaseAPILoader):
    """
    Loader to fetch metadata (IDs and coordinates) of Ecocounter stations
    from Montpellier Open Data API.

    Inherits from BaseAPILoader and implements the abstract method `fetch_data`.
    """

    def fetch_data(
        self, limit: int = 1000, timeout: int = 10, retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch station metadata from the API with retry mechanism.

        Args:
            limit (int): Maximum number of station records to fetch.
            timeout (int): Timeout in seconds for each request.
            retries (int): Number of retry attempts in case of failure.

        Returns:
            dict: JSON response containing station metadata if successful.
            None: If all retries fail or an unrecoverable error occurs.
        """
        logger.info("Starting metadata fetch for Ecocounter station IDs...")
        print("Fetching station metadata...")

        url = base_url
        params = {"limit": limit}

        for attempt in range(retries):
            print(f"Attempt {attempt + 1} of {retries}...")
            try:
                response = requests.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                logger.info("Successfully fetched station metadata.")
                print("Metadata fetched successfully")
                return response.json()

            except Timeout:
                logger.warning(
                    f"Timeout occurred on attempt {attempt + 1} for URL: {url}"
                )

            except ConnectionError:
                logger.warning(
                    f"Connection error on attempt {attempt + 1} for URL: {url}"
                )

            except HTTPError as http_err:
                logger.error(f"HTTP error: {http_err} for URL: {url}")
                break

            except ValueError as json_err:
                logger.error(f"JSON decode error: {json_err} for URL: {url}")
                break

            except RequestException as req_err:
                logger.error(f"Request exception: {req_err} for URL: {url}")

            time.sleep(0.5 * (attempt + 1))

        print("Failed to fetch station metadata after all retries")
        logger.error("All attempts to fetch station metadata failed.")
        return None
