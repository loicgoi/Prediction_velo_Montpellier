import logging
import requests
import pandas as pd
import urllib.parse
import time
from pathlib import Path

# Configuration
IDS_PATH = Path(__file__).parent
# On remonte d'un cran (..) pour aller dans backend/ puis dans data/raw
DATA_PATH = IDS_PATH / "../data/raw"
DATA_PATH.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


class MontpellierAPILoader:
    def __init__(self, base_url="https://portail-api-data.montpellier3m.fr"):
        self.base_url = base_url
        self.start_date = "2024-01-01"
        self.end_date = "2024-12-31"

    def get_stations_metadata(self, limit=1000):
        logger.info("Récupération des métadonnées (IDs + Coordonnées)...")
        url = f"{self.base_url}/ecocounter"
        params = {"limit": limit}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            stations_list = []
            for item in data:
                if "id" not in item:
                    continue

                station_data = {
                    "station_id": item["id"],
                    "name": item.get("name", {}).get("value", "Inconnu"),
                    "latitude": None,
                    "longitude": None,
                }

                try:
                    if "location" in item and "value" in item["location"]:
                        coords = item["location"]["value"]["coordinates"]
                        station_data["longitude"] = coords[0]
                        station_data["latitude"] = coords[1]
                except Exception:
                    pass

                stations_list.append(station_data)

            return pd.DataFrame(stations_list)

        except Exception as e:
            logger.error(f"Erreur métadonnées : {e}")
            return pd.DataFrame()

    def fetch_timeseries(self, station_ids_list):
        all_records = []
        logger.info(
            f"Démarrage récupération trafic pour {len(station_ids_list)} stations..."
        )

        for i, station_id in enumerate(station_ids_list):
            full_id = (
                f"urn:ngsi-ld:EcoCounter:{station_id}"
                if "urn:" not in station_id
                else station_id
            )
            encoded_id = urllib.parse.quote(full_id)
            url = f"{self.base_url}/ecocounter_timeseries/{encoded_id}/attrs/intensity"
            params = {"fromDate": self.start_date, "toDate": self.end_date}

            try:
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "index" in data and "values" in data:
                        for d, v in zip(data["index"], data["values"]):
                            all_records.append(
                                {"date": d, "station_id": station_id, "intensity": v}
                            )
            except Exception as e:
                logger.error(f"Erreur sur {station_id}: {e}")

            time.sleep(0.1)

        return pd.DataFrame(all_records)

    def run_full_extraction(self):
        df_stations = self.get_stations_metadata()
        if df_stations.empty:
            return None

        df_stations.to_csv(DATA_PATH / "stations_metadata.csv", index=False)
        print(f"Stations sauvegardées dans : {DATA_PATH}")

        ids_to_fetch = df_stations["station_id"].tolist()
        df_trafic = self.fetch_timeseries(ids_to_fetch)

        if not df_trafic.empty:
            df_trafic["date"] = pd.to_datetime(df_trafic["date"])
            df_trafic.to_csv(DATA_PATH / "trafic_history.csv", index=False)
            print(f"Trafic sauvegardé dans : {DATA_PATH}")
            return df_trafic

        return None
