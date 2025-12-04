from datetime import datetime, timedelta
from download.daily_weather_api import OpenMeteoDailyAPIC
from src.api_data_processing import extract_daily_weather
from pipelines.data_insertion import insert_data_to_db
from utils.logging_config import logger
from download.ecocounters_ids import EncountersIDsLoader
from download.weeather_api import WeatherHistoryLoader
from src.api_data_processing import (
    extract_station_metadata,
    fetch_and_extract_timeseries,
    extract_weather_fields,
)


def fetch_data_for_date(target_date: datetime):
    """
    Download traffic and weather data for a specific date.
    This function is used by the daily update pipeline.
    """
    print(f"Téléchargement des données pour le {target_date.strftime('%Y-%m-%d')}...")

    df_metadata, ids = extract_station_metadata(EncountersIDsLoader().fetch_data())
    if not ids:
        print("No station IDs found.")
        return None, None, None

    date_str = target_date.strftime("%Y-%m-%d")

    df_trafic = fetch_and_extract_timeseries(
        ids, start_date=date_str, end_date=date_str
    )
    df_weather = extract_weather_fields(
        WeatherHistoryLoader().fetch_data(start_date=date_str, end_date=date_str)
    )

    return df_trafic, df_weather, df_metadata


def run_daily_update():
    """
    Orchestrates the daily update pipeline.
    """

    logger.info("--- Starting the daily update pipeline ---")

    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    logger.info(f"Data targeting for the date: {date_str}")

    try:
        # Fetch daily aggregated data
        df_traffic, df_weather, df_metadata = fetch_data_for_date(yesterday)
        logger.info("Fetched traffic, weather and metadata successfully.")

        # Fetch OpenMeteo daily weather
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

        logger.info("Daily update pipeline completed successfully.")

    except Exception as e:
        logger.error(
            f"An error occurred during the update pipeline: {e}", exc_info=True
        )
