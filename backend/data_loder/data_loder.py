# src/data_loader/data_loader.py
import logging
import requests
import pandas as pd
import urllib.parse
import time
from pathlib import Path

# Configuration
IDS_PATH = Path(__file__).parent
DATA_PATH = IDS_PATH / "../../data/raw" # On s'assure d'être dans data/raw
DATA_PATH.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

class MontpellierAPILoader:
    def __init__(self, base_url="https://portail-api-data.montpellier3m.fr"):
        self.base_url = base_url
        self.start_date = "2023-01-01"
        self.end_date = "2024-12-31"

    def get_stations_metadata(self, limit=1000):
        """
        Récupère la liste des compteurs AVEC leurs coordonnées.
        Retourne un DataFrame de métadonnées (Table STATIONS).
        """
        logger.info("📡 Récupération des métadonnées (IDs + Coordonnées)...")
        url = f"{self.base_url}/ecocounter"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            stations_list = []
            
            for item in data:
                # Extraction sécurisée des données
                if "id" not in item:
                    continue
                
                station_data = {
                    "station_id": item["id"],
                    "name": item.get("name", {}).get("value", "Inconnu"),
                    "latitude": None,
                    "longitude": None
                }
                
                # Extraction GeoJSON des coordonnées
                # Format habituel : location: {value: {coordinates: [lon, lat]}}
                try:
                    if "location" in item and "value" in item["location"]:
                        coords = item["location"]["value"]["coordinates"]
                        # Attention : GeoJSON c'est souvent [Longitude, Latitude]
                        station_data["longitude"] = coords[0]
                        station_data["latitude"] = coords[1]
                except Exception:
                    pass # Si pas de coords, on laisse None
                
                stations_list.append(station_data)
                
            logger.info(f"✅ {len(stations_list)} stations identifiées.")
            
            # On retourne un DataFrame 'STATIONS'
            return pd.DataFrame(stations_list)
            
        except Exception as e:
            logger.error(f"❌ Erreur métadonnées : {e}")
            return pd.DataFrame()

    def fetch_timeseries(self, station_ids_list):
        """Récupère l'historique de trafic pour une liste d'IDs"""
        all_records = []
        logger.info(f"🚀 Démarrage récupération trafic pour {len(station_ids_list)} stations...")

        for i, station_id in enumerate(station_ids_list):
            # Encodage URL
            full_id = f"urn:ngsi-ld:EcoCounter:{station_id}" if "urn:" not in station_id else station_id
            encoded_id = urllib.parse.quote(full_id)
            url = f"{self.base_url}/ecocounter_timeseries/{encoded_id}/attrs/intensity"
            
            params = {"fromDate": self.start_date, "toDate": self.end_date}

            try:
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "index" in data and "values" in data:
                        for d, v in zip(data["index"], data["values"]):
                            all_records.append({
                                "date": d,
                                "station_id": station_id, # Lien avec la table STATIONS
                                "intensity": v
                            })
            except Exception as e:
                logger.error(f"Erreur sur {station_id}: {e}")
            
            time.sleep(0.1) # Pause API

        return pd.DataFrame(all_records)

    def run_full_extraction(self):
        """Orchestre tout : Métadonnées + Trafic"""
        
        # 1. Récupérer la table STATIONS (avec Lat/Lon)
        df_stations = self.get_stations_metadata()
        if df_stations.empty:
            return None
        
        # Sauvegarde STATIONS
        df_stations.to_csv(DATA_PATH / "stations_metadata.csv", index=False)
        logger.info("💾 Fichier stations_metadata.csv sauvegardé.")

        # 2. Récupérer la table TRAFIC
        # On ne prend que les IDs trouvés à l'étape 1
        ids_to_fetch = df_stations['station_id'].tolist()
        df_trafic = self.fetch_timeseries(ids_to_fetch)
        
        # Sauvegarde TRAFIC
        if not df_trafic.empty:
            df_trafic['date'] = pd.to_datetime(df_trafic['date'])
            df_trafic.to_csv(DATA_PATH / "trafic_history.csv", index=False)
            logger.info("💾 Fichier trafic_history.csv sauvegardé.")
            return df_trafic
        
        return None