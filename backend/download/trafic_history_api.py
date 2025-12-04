import requests
import urllib.parse
import time
import pandas as pd
from download.abstract_loader import BaseAPILoader
from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException
from utils.logging_config import logger
from typing import List, Dict, Optional, Tuple


class EcoCounterTimeseriesLoader(BaseAPILoader):
    """
    Loader to fetch time series data from Montpellier Ecocounter API for multiple stations.
    Handles API pagination limits (max 10k records) by chunking the time range.

    Inherits from BaseAPILoader and implements the abstract method `fetch_data`.
    """

    def _generate_date_chunks(self, start_str: str, end_str: str, months: int = 6) -> List[Tuple[str, str]]:
        """
        Helper method to split a date range into smaller chunks (e.g., 6 months).
        """
        start = pd.to_datetime(start_str)
        end = pd.to_datetime(end_str)
        chunks = []
        # If the range is a single day (or instantaneous), return one chunk immediately
        if start == end:
            return [(
                start.strftime("%Y-%m-%dT%H:%M:%S"),
                end.strftime("%Y-%m-%dT%H:%M:%S")
            )]
        
        current = start
        while current < end:
            next_date = current + pd.DateOffset(months=months)
            chunk_end = min(next_date, end)
            
            # Format expected by the API (YYYY-MM-DDTHH:MM:SS)
            chunks.append((
                current.strftime("%Y-%m-%dT%H:%M:%S"),
                chunk_end.strftime("%Y-%m-%dT%H:%M:%S")
            ))
            # Next chunk starts where the previous one ended
            current = chunk_end
            
        return chunks

    def fetch_data(
        self,
        station_ids_list: List[str],
        start_date: str,
        end_date: str,
        timeout: int = 5,
        retries: int = 3,
    ) -> Dict[str, Optional[Dict]]:
        """
        Loop over station IDs AND date chunks to fetch complete JSON data with retry mechanism.
        """
        results: Dict[str, Optional[Dict]] = {}
        total_stations = len(station_ids_list)

        # 1. Prepare date chunks to bypass API limits
        date_chunks = self._generate_date_chunks(start_date, end_date)
        logger.info(f"Time range split into {len(date_chunks)} chunks per station to ensure full data retrieval.")

        for idx, station_id in enumerate(station_ids_list, start=1):
            full_id = (
                f"urn:ngsi-ld:EcoCounter:{station_id}"
                if "urn:" not in station_id
                else station_id
            )
            encoded_id = urllib.parse.quote(full_id)
            url = f"https://portail-api-data.montpellier3m.fr/ecocounter_timeseries/{encoded_id}/attrs/intensity"
            
            print(
                f"[{idx}/{total_stations}] Downloading data for station {station_id}...",
                end=" ",
                flush=True,
            )

            # Containers to merge results from different time chunks
            consolidated_index = []
            consolidated_values = []
            
            # 2. Loop over time chunks
            for chunk_start, chunk_end in date_chunks:
                params = {"fromDate": chunk_start, "toDate": chunk_end}
                chunk_success = False

                for attempt in range(retries):
                    try:
                        response = requests.get(url, params=params, timeout=timeout)
                        
                        # Specific handling: 404 on a chunk isn't fatal (just no data for this period)
                        if response.status_code == 404:
                            chunk_success = True
                            break

                        response.raise_for_status()
                        data = response.json()
                        
                        # Merge data into the main lists
                        if "index" in data and "values" in data:
                            consolidated_index.extend(data["index"])
                            consolidated_values.extend(data["values"])
                        
                        chunk_success = True
                        # Success for this chunk, exit retry loop
                        break 

                    except Timeout:
                        logger.warning(
                            f"Timeout on attempt {attempt + 1} for station {station_id} (chunk {chunk_start})"
                        )

                    except ConnectionError:
                        logger.warning(
                            f"Connection error on attempt {attempt + 1} for station {station_id}"
                        )

                    except HTTPError as http_err:
                        # Log critical errors (other than handled 404)
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
                
                # End of retry loop for this chunk

            # 3. Reconstruct the final JSON response structure for this station
            if consolidated_index:
                results[station_id] = {
                    "index": consolidated_index,
                    "values": consolidated_values,
                    "id": station_id
                }
                print("Done (Merged)")
            else:
                results[station_id] = None
                print("No Data or Failed")

        return results