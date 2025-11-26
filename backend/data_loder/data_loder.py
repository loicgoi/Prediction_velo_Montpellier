from pathlib import Path
from abc import ABC, abstractmethod
import logging
import requests
import pandas as pd
from requests.exceptions import HTTPError, RequestException
import time

IDS_PATH = Path(__file__).parent
DATA_PATH = IDS_PATH / "../data"
OUTPUT_PATH = DATA_PATH / "output"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


logging.basicConfig(filename="myapp.log", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Started")


class Loader(ABC):
    @abstractmethod
    def counter_ids(self, file_path):
        pass

    @abstractmethod
    def load_api(self, base_url):
        pass


class DataAPI(Loader):
    def counter_ids(self, q):
        """function to fetch ecnocounter endpoint
        Args:
            q (int): Limit the number of elements of entities to return (max 1000)
        Returns:
            list: list of counter ids
        """
        self.q = q
        try:
            logger.info("started to fetch ids ...!")
            url = "https://portail-api-data.montpellier3m.fr/ecocounter"
            params = {"limit": q}
            response = requests.get(url, params=params)
            response.raise_for_status()
            if response.status_code == 200:
                logger.info("success ..!")
                data = response.json()
                logger.info("Raw data has been fetched successfully")
                self.data_ids = [item["id"] for item in data]
                self.df_ids = pd.DataFrame(self.data_ids)
                self.ids = self.df_ids.iloc[:, 0].to_list()
                logger.info("the list of counter ids has been recoverd successfully")
                print(self.ids)
            return self.ids
        except HTTPError as http_err:
            logger.info(f"HTTP error occurred {http_err}")
        except Exception as e:
            logger.info(f"other error occurred {e}")
            return None

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
            "fromDate": "2023-01-01",
            "toDate": "2025-10-30",
        }

        try:
            for station_id in self.counter_ids(100):
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
