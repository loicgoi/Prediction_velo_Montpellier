from datetime import datetime, timedelta
import pandas as pd

# Imports pour la récupération de données (Legacy du collègue)
from download.daily_weather_api import OpenMeteoDailyAPIC
from download.ecocounters_ids import EncountersIDsLoader
from download.weeather_api import WeatherHistoryLoader
from src.api_data_processing import (
    extract_station_metadata,
    fetch_and_extract_timeseries,
    extract_weather_fields,
    extract_daily_weather
)

# Imports pour la base de données et logs
from pipelines.data_insertion import insert_data_to_db
from utils.logging_config import logger
from core.dependencies import db_manager 
from monitoring.performance import PerformanceMonitor


def fetch_data_for_date(target_date: datetime):
    """
    Download traffic and weather data for a specific date.
    This function is used by the daily update pipeline.
    """
    logger.info(f"Téléchargement des données pour le {target_date.strftime('%Y-%m-%d')}...")

    # 1. Récupération des IDs et Métadonnées
    df_metadata, ids = extract_station_metadata(EncountersIDsLoader().fetch_data())
    if not ids:
        logger.warning("No station IDs found.")
        return None, None, None

    date_str = target_date.strftime("%Y-%m-%d")

    # 2. Récupération du Trafic (J-1)
    df_trafic = fetch_and_extract_timeseries(
        ids, start_date=date_str, end_date=date_str
    )
    
    # 3. Récupération de l'Historique Météo (J-1)
    df_weather = extract_weather_fields(
        WeatherHistoryLoader().fetch_data(start_date=date_str, end_date=date_str)
    )

    return df_trafic, df_weather, df_metadata


def run_daily_update():
    """
    Orchestrates the daily update pipeline.
    1. Fetches yesterday's traffic (J-1).
    2. Fetches today's weather forecast.
    3. Inserts everything into DB.
    4. Runs Monitoring to compare J-1 predictions vs reality.
    """

    logger.info("--- Starting the daily update pipeline ---")

    # J-1
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    logger.info(f"Data targeting for the date: {date_str}")

    try:
        # --- ETAPE 1 : RECUPERATION DES DONNEES ---
        # Fetch daily aggregated data (Trafic J-1)
        df_traffic, df_weather, df_metadata = fetch_data_for_date(yesterday)
        logger.info("Fetched traffic, weather and metadata successfully.")

        # Fetch OpenMeteo daily weather (Forecast J0)
        logger.info("Fetching daily weather from OpenMeteo API...")
        client = OpenMeteoDailyAPIC()

        today_str = datetime.now().strftime("%Y-%m-%d")
        json_response = client.get_weather_json(
            latitude=43.6109,
            longitude=3.8763,
            start_date=today_str,
            end_date=today_str,
        )

        df_daily_weather = extract_daily_weather(json_response)
        logger.info(f"Fetched OpenMeteo daily weather. Rows: {len(df_daily_weather)}")

        # --- ETAPE 2 : INSERTION EN BASE ---
        # Prepare datasets for insertion
        datasets = [
            ("Traffic Data", df_traffic, df_weather, df_metadata),
            ("OpenMeteo Daily Weather", None, df_daily_weather, None),
        ]

        # Insert each dataset
        for name, traffic_df, weather_df, metadata_df in datasets:
            has_data = any(
                df is not None and hasattr(df, "empty") and not df.empty
                for df in [traffic_df, weather_df, metadata_df]
            )

            if has_data:
                logger.info(f"Inserting {name} into DB...")
                insert_data_to_db(traffic_df, weather_df, metadata_df)
                logger.info(f"{name} inserted successfully.")
            else:
                logger.warning(f"{name} is empty or None → Skipping.")

        logger.info("Daily data update completed.")

        # --- ETAPE 3 : MONITORING (Feedback Loop) ---
        logger.info("--- Démarrage du Monitoring (Comparaison J-1) ---")
        
        session = db_manager.get_session()
        try:
            monitor = PerformanceMonitor(session)
            # On évalue la performance pour la date 'yesterday'
            monitor.run_daily_evaluation(yesterday)
        except Exception as e:
            logger.error(f"Erreur lors du monitoring : {e}")
        finally:
            session.close()
            
        logger.info("Daily pipeline finished.")

    except Exception as e:
        logger.error(
            f"An error occurred during the update pipeline: {e}", exc_info=True
        )

if __name__ == "__main__":
    run_daily_update()