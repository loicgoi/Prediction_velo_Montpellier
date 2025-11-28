import requests
import urllib.parse
import time
from download.abstract_loader import BaseAPILoader
from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException
from utils.logging_config import logger
from typing import List, Dict, Optional


class EcoCounterTimeseriesLoader(BaseAPILoader):
    """
    Loader to fetch time series data from Montpellier Ecocounter API for multiple stations.

    Inherits from BaseAPILoader and implements the abstract method `fetch_data`.
    """

    def fetch_data(
        self,
        station_ids_list: List[str],
        start_date: str,
        end_date: str,
        timeout: int = 5,
        retries: int = 3,
    ) -> Dict[str, Optional[Dict]]:
        """
        Loop over station IDs and fetch JSON data from the API with retry mechanism.

        Args:
            station_ids_list (List[str]): List of station IDs to fetch data for.
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.
            timeout (int): Timeout in seconds for each request.
            retries (int): Number of retry attempts in case of failure.

        Returns:
            Dict[str, Optional[Dict]]: Dictionary mapping station_id to response JSON,
                                        or None if fetching failed.
        """
        results: Dict[str, Optional[Dict]] = {}
        total_stations = len(station_ids_list)

        for idx, station_id in enumerate(station_ids_list, start=1):
            full_id = (
                f"urn:ngsi-ld:EcoCounter:{station_id}"
                if "urn:" not in station_id
                else station_id
            )
            encoded_id = urllib.parse.quote(full_id)
            url = f"https://portail-api-data.montpellier3m.fr/ecocounter_timeseries/{encoded_id}/attrs/intensity"
            params = {"fromDate": start_date, "toDate": end_date}

            print(
                f"[{idx}/{total_stations}] Downloading data for station {station_id}...",
                end=" ",
                flush=True,
            )

            for attempt in range(retries):
                try:
                    response = requests.get(url, params=params, timeout=timeout)
                    response.raise_for_status()
                    results[station_id] = response.json()
                    print("Done")
                    break

                except Timeout:
                    logger.warning(
                        f"Timeout on attempt {attempt + 1} for station {station_id}"
                    )

                except ConnectionError:
                    logger.warning(
                        f"Connection error on attempt {attempt + 1} for station {station_id}"
                    )

                except HTTPError as http_err:
                    logger.error(f"HTTP error {http_err} for station {station_id}")
                    break

                except ValueError as json_err:
                    logger.error(
                        f"JSON decode error {json_err} for station {station_id}"
                    )
                    break

                except RequestException as req_err:
                    logger.error(
                        f"Request exception {req_err} for station {station_id}"
                    )

                time.sleep(0.5 * (attempt + 1))

            if station_id not in results:
                results[station_id] = None
                print("Failed")

        return results
