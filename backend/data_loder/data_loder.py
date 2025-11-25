from pathlib import Path
from abc import ABC, abstractmethod
import logging
import requests
import pandas as pd
from requests.exceptions import HTTPError, RequestException
import time

IDS_PATH = Path(__file__).parent
DATA_PATH = IDS_PATH / "../data"
IDS_FILE = DATA_PATH / "stations_ids.csv"
OUTPUT_PATH = DATA_PATH / "output"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


logging.basicConfig(filename="myapp.log", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Started")


class Loader(ABC):
    @abstractmethod
    def load_csv(self, file_path):
        pass

    @abstractmethod
    def load_api(self, base_url):
        pass


class DataAPI(Loader):
    def load_csv(self, file_path):
        """Load station IDs from CSV file."""
        logger.info("Loading IDs from CSV...")
        df = pd.read_csv(file_path)
        self.ids = df.iloc[:, 0].tolist()
        logger.info(f"Loaded {len(self.ids)} IDs")
        return self.ids

    def fetch_with_retry(self, url, params, retries=3, timeout=10):
        """Helper function to retry failed API calls."""
        for attempt in range(retries):
            try:
                response = requests.get(url=url, params=params, timeout=timeout)
                response.raise_for_status()
                return response
            except RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    raise

    def load_api(self, base_url):
        """Fetch data from API for each ID and return separate DataFrames."""
        logger.info("Fetching data from API...")

        results = {}

        params = {
            "fromDate": "2024-01-01",
            "toDate": "2024-12-30",
        }

        try:
            for station_id in self.ids:
                url = f"{base_url}/{station_id}/attrs/intensity"
                logger.info(f"Fetching data for station {station_id}")
                response = self.fetch_with_retry(url, params)
                data = response.json()
                if not data or "index" not in data or not data["index"]:
                    logger.warning(f"No data for station {station_id}, skipping...")
                    continue
                df = pd.DataFrame(
                    {"timestamp": data["index"], "value": data["values"][0]}
                )
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                output_file = OUTPUT_PATH / f"station_{station_id}.csv"
                df.to_csv(output_file, index=False)
                logger.info(f"Saved: {output_file}")
                results[station_id] = df
                print(f"\n===== STATION {station_id} SAMPLE =====")
                print(df.head())
            return results
        except HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
        except Exception as e:
            logger.error(f"Other error occurred: {e}")
        return None
